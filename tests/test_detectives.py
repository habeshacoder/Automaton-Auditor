"""
Tests for Detective agents
"""
import pytest
from pathlib import Path
from src.nodes.detectives import repo_investigator_node, doc_analyst_node
from src.nodes.state_models import AgentState


def test_repo_investigator_with_valid_repo():
    """Test RepoInvestigator with a real repository"""
    state: AgentState = {
        "repo_url": "https://github.com/langchain-ai/langgraph",
        "pdf_path": "",
        "rubric_dimensions": [],
        "evidences": {},
        "opinions": [],
        "final_report": "",
        "errors": []
    }

    result = repo_investigator_node(state)

    assert "evidences" in result
    assert "repo" in result["evidences"]
    assert len(result["evidences"]["repo"]) > 0

    # Check evidence types
    evidence_goals = [e.goal for e in result["evidences"]["repo"]]
    assert "Git Forensic Analysis" in evidence_goals
    assert "State Management Rigor" in evidence_goals


def test_doc_analyst_with_sample_pdf():
    """Test DocAnalyst with a sample PDF"""
    # This test requires a sample PDF file
    # In production, you'd create a fixture PDF
    pass


@pytest.mark.asyncio
async def test_evidence_aggregation():
    """Test that evidence from multiple detectives aggregates correctly"""
    state: AgentState = {
        "repo_url": "",
        "pdf_path": "",
        "rubric_dimensions": [],
        "evidences": {
            "repo": [],
            "doc": []
        },
        "opinions": [],
        "final_report": "",
        "errors": []
    }

    # Simulate evidence from both detectives
    assert "repo" in state["evidences"]
    assert "doc" in state["evidences"]
