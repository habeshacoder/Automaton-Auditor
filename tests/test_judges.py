"""
Tests for Judge agents
"""
import pytest
from src.nodes.judges import JudgeAgent
from src.nodes.state_models import Evidence, JudicialOpinion


def test_prosecutor_persona():
    """Test that Prosecutor has critical lens"""
    rubric_logic = {
        "prosecutor": "Be critical and identify flaws",
        "defense": "Be supportive",
        "tech_lead": "Be pragmatic"
    }

    judge = JudgeAgent("Prosecutor", rubric_logic)
    assert judge.persona == "Prosecutor"
    assert "Trust No One" in judge.system_prompts["Prosecutor"]


def test_defense_persona():
    """Test that Defense has optimistic lens"""
    rubric_logic = {
        "prosecutor": "Be critical",
        "defense": "Reward effort and intent",
        "tech_lead": "Be pragmatic"
    }

    judge = JudgeAgent("Defense", rubric_logic)
    assert judge.persona == "Defense"
    assert "Reward Effort" in judge.system_prompts["Defense"]


def test_tech_lead_persona():
    """Test that TechLead has pragmatic lens"""
    rubric_logic = {
        "prosecutor": "Be critical",
        "defense": "Be supportive",
        "tech_lead": "Assess maintainability"
    }

    judge = JudgeAgent("TechLead", rubric_logic)
    assert judge.persona == "TechLead"
    assert "Does it actually work" in judge.system_prompts["TechLead"]


@pytest.mark.skip(reason="Requires OpenAI API key")
def test_judge_evaluation():
    """Test that judge returns structured opinion"""
    rubric_logic = {
        "prosecutor": "Be critical",
        "defense": "Be supportive",
        "tech_lead": "Be pragmatic"
    }

    evidence = [
        Evidence(
            goal="Test evidence",
            found=True,
            content="Sample content",
            location="test.py",
            rationale="Test rationale",
            confidence=0.9
        )
    ]

    judge = JudgeAgent("Prosecutor", rubric_logic)
    opinion = judge.evaluate("test_criterion", evidence)

    assert isinstance(opinion, JudicialOpinion)
    assert opinion.judge == "Prosecutor"
    assert 1 <= opinion.score <= 5
