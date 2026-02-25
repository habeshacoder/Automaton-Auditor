"""
LangGraph Orchestration - Digital Courtroom State Machine
"""
from langgraph.graph import StateGraph, START, END
from src.nodes.state_models import AgentState
from src.nodes.detectives import (
    repo_investigator_node,
    doc_analyst_node,
    evidence_aggregator_node
)
from src.nodes.judges import (
    prosecutor_node,
    defense_node,
    tech_lead_node
)
from src.nodes.justice import chief_justice_node


def build_audit_graph():
    """
    Build the complete Automaton Auditor StateGraph

    Architecture:
        START
          ↓
        ContextBuilder (loads rubric)
          ↓
        ┌─────────────┐
        │ RepoInvestigator (parallel)
        │ DocAnalyst (parallel)
        └─────────────┘
          ↓
        EvidenceAggregator (fan-in)
          ↓
        ┌─────────────┐
        │ Prosecutor (parallel)
        │ Defense (parallel)
        │ TechLead (parallel)
        └─────────────┘
          ↓
        ChiefJustice (synthesis)
          ↓
        END
    """

    # Initialize StateGraph with typed state schema
    builder = StateGraph(AgentState)

    # Layer 0: Context initialization
    builder.add_node("context_builder", context_builder_node)

    # Layer 1: Detective agents (parallel evidence collection)
    builder.add_node("repo_investigator", repo_investigator_node)
    builder.add_node("doc_analyst", doc_analyst_node)

    # Layer 1.5: Evidence aggregation (fan-in)
    builder.add_node("evidence_aggregator", evidence_aggregator_node)

    # Layer 2: Judge agents (parallel evaluation)
    builder.add_node("prosecutor", prosecutor_node)
    builder.add_node("defense", defense_node)
    builder.add_node("tech_lead", tech_lead_node)

    # Layer 3: Chief Justice (synthesis)
    builder.add_node("chief_justice", chief_justice_node)

    # Define edges
    # START -> Context Builder
    builder.add_edge(START, "context_builder")

    # Context Builder -> Detectives (fan-out to parallel branches)
    builder.add_edge("context_builder", "repo_investigator")
    builder.add_edge("context_builder", "doc_analyst")

    # Detectives -> Evidence Aggregator (fan-in)
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")

    # Evidence Aggregator -> Judges (fan-out to parallel branches)
    builder.add_edge("evidence_aggregator", "prosecutor")
    builder.add_edge("evidence_aggregator", "defense")
    builder.add_edge("evidence_aggregator", "tech_lead")

    # Judges -> Chief Justice (fan-in)
    builder.add_edge("prosecutor", "chief_justice")
    builder.add_edge("defense", "chief_justice")
    builder.add_edge("tech_lead", "chief_justice")

    # Chief Justice -> END
    builder.add_edge("chief_justice", END)

    # Compile the graph
    graph = builder.compile()

    return graph


def context_builder_node(state: AgentState) -> dict:
    """
    Initialize context by loading rubric and preparing state
    """
    import json
    from pathlib import Path

    # Load rubric JSON
    rubric_path = Path(__file__).parent.parent / "rubric" / "week2_rubric.json"

    try:
        with open(rubric_path) as f:
            rubric = json.load(f)

        rubric_dimensions = rubric.get("dimensions", [])

        return {
            "rubric_dimensions": rubric_dimensions,
            "evidences": {},
            "opinions": [],
            "errors": []
        }

    except FileNotFoundError:
        return {
            "rubric_dimensions": _get_default_rubric(),
            "evidences": {},
            "opinions": [],
            "errors": ["Rubric file not found, using defaults"]
        }
    except Exception as e:
        return {
            "rubric_dimensions": _get_default_rubric(),
            "evidences": {},
            "opinions": [],
            "errors": [f"Error loading rubric: {str(e)}"]
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
                "tech_lead": "Assess practical viability"
            }
        },
        {
            "id": "langgraph_architecture",
            "name": "LangGraph Architecture",
            "target_artifact": "github_repo",
            "forensic_instruction": "Analyze graph structure and parallelism",
            "judicial_logic": {
                "prosecutor": "Flag linear or broken graphs",
                "defense": "Appreciate complex state management",
                "tech_lead": "Evaluate maintainability"
            }
        }
    ]
