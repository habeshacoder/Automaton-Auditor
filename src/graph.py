"""
LangGraph Orchestration - Digital Courtroom State Machine
"""

from langgraph.graph import StateGraph, START, END  # [web:1][web:48]
from src.nodes.state_models import AgentState
from src.nodes.detectives import (
    repo_investigator_node,
    doc_analyst_node,
    evidence_aggregator_node,
     vision_inspector_node,
)
from src.nodes.judges import (
    prosecutor_node,
    defense_node,
    tech_lead_node,
)
from src.nodes.justice import chief_justice_node
import json
from pathlib import Path


def context_builder_node(state: AgentState) -> dict:
    """
    Initialize context by loading rubric and preparing state.
    """
    project_root = Path(__file__).parent.parent
    rubric_path = project_root / "rubric" / "week2_rubric.json"

    try:
        with open(rubric_path) as f:
            rubric = json.load(f)
        rubric_dimensions = rubric.get("dimensions", [])
        return {
            "rubric_dimensions": rubric_dimensions,
            "evidences": {},
            "opinions": [],
            "errors": [],
            "has_fatal_error": False,
        }
    except FileNotFoundError:
        return {
            "rubric_dimensions": _get_default_rubric(),
            "evidences": {},
            "opinions": [],
            "errors": ["Rubric file not found, using defaults"],
            "has_fatal_error": False,
        }
    except Exception as e:
        return {
            "rubric_dimensions": _get_default_rubric(),
            "evidences": {},
            "opinions": [],
            "errors": [f"Error loading rubric: {str(e)}"],
            "has_fatal_error": False,
        }


def _get_default_rubric() -> list:
    """Fallback rubric if JSON file not available"""
    return [
        {
            "id": "forensic_accuracy_code",
            "name": "Forensic Accuracy (Codebase)",
            "target_artifact": "github_repo",
            "forensic_instruction": "Verify repository structure and implementation",
            "judicial_logic": {
                "prosecutor": "Identify missing or broken implementations",
                "defense": "Recognize effort and partial implementations",
                "tech_lead": "Assess practical viability",
            },
        },
        {
            "id": "langgraph_architecture",
            "name": "LangGraph Architecture",
            "target_artifact": "github_repo",
            "forensic_instruction": "Analyze graph structure and parallelism",
            "judicial_logic": {
                "prosecutor": "Flag linear or broken graphs",
                "defense": "Appreciate complex state management",
                "tech_lead": "Evaluate maintainability",
            },
        },
    ]


def build_audit_graph():
    """
    Build the complete Automaton Auditor StateGraph.

    Layers:
    - ContextBuilder
    - Detectives (Repo, Doc) in parallel (fan-out)
    - EvidenceAggregator (fan-in)
    - Judges (Prosecutor, Defense, TechLead) in parallel (fan-out)
    - ChiefJustice (fan-in + synthesis)
    - Conditional routing: skip judges if fatal errors.
    """
    builder = StateGraph(AgentState)  # typed state schema [web:50]

    # Nodes
    builder.add_node("context_builder", context_builder_node)

    # Detectives
    builder.add_node("repo_investigator", repo_investigator_node)
    builder.add_node("doc_analyst", doc_analyst_node)
    builder.add_node("evidence_aggregator", evidence_aggregator_node)
    builder.add_node("vision_inspector", vision_inspector_node)

    # Judges
    builder.add_node("prosecutor", prosecutor_node)
    builder.add_node("defense", defense_node)
    builder.add_node("tech_lead", tech_lead_node)

    # Chief Justice
    builder.add_node("chief_justice", chief_justice_node)

    # Edges

    # START → Context
    builder.add_edge(START, "context_builder")

    # Fan-out to detectives
    builder.add_edge("context_builder", "repo_investigator")
    builder.add_edge("context_builder", "doc_analyst")

    # Fan-in from detectives
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")
    builder.add_edge("vision_inspector", "evidence_aggregator")

    # Routing helpers
    def no_fatal_error(state: AgentState) -> bool:
        return not state.get("has_fatal_error", False)

    def has_fatal_error(state: AgentState) -> bool:
        return state.get("has_fatal_error", False)

    # If no fatal error → go to judges
    # (We route to prosecutor; prosecutor → defense → tech_lead → chief_justice below)
    builder.add_conditional_edges(
        "evidence_aggregator",
        no_fatal_error,
        {True: "prosecutor", False: "chief_justice"},
    )  # [web:1][web:62][web:71]

    # Judges in sequence (you already have parallelism via state reducers)
    builder.add_edge("prosecutor", "defense")
    builder.add_edge("defense", "tech_lead")
    builder.add_edge("tech_lead", "chief_justice")

    # Extra safety: if we explicitly detect fatal error, allow direct jump
    # builder.add_conditional_edges(
    #     "evidence_aggregator",
    #     has_fatal_error,
    #     {True: "chief_justice"},
    # )

    # Final
    builder.add_edge("chief_justice", END)

    graph = builder.compile()
    return graph
