"""
State Models for Automaton Auditor
Defines typed state structures using Pydantic and TypedDict with proper reducers
"""
import operator
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class Evidence(BaseModel):
    """Structured evidence collected by Detective agents"""
    goal: str = Field(description="What this evidence aims to prove")
    found: bool = Field(description="Whether the artifact exists")
    content: Optional[str] = Field(default=None, description="Actual content or snippet")
    location: str = Field(description="File path, commit hash, or PDF page")
    rationale: str = Field(description="Reasoning behind confidence level")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")

    class Config:
        json_schema_extra = {
            "example": {
                "goal": "Verify StateGraph instantiation",
                "found": True,
                "content": "builder = StateGraph(AgentState)",
                "location": "src/graph.py:45",
                "rationale": "Found typed StateGraph with proper schema",
                "confidence": 0.95
            }
        }


class JudicialOpinion(BaseModel):
    """Opinion from a Judge agent with persona-specific reasoning"""
    judge: Literal["Prosecutor", "Defense", "TechLead"] = Field(
        description="Judge persona rendering verdict"
    )
    criterion_id: str = Field(description="Rubric criterion being evaluated")
    score: int = Field(ge=1, le=5, description="Score from 1-5")
    argument: str = Field(description="Detailed reasoning for the score")
    cited_evidence: List[str] = Field(
        description="Evidence IDs supporting this opinion"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "judge": "Prosecutor",
                "criterion_id": "forensic_accuracy_code",
                "score": 3,
                "argument": "State management uses Pydantic but lacks proper reducers",
                "cited_evidence": ["state_structure_check", "reducer_verification"]
            }
        }


class AgentState(TypedDict):
    """
    Main state container for the Automaton Auditor graph.
    Uses operator.ior and operator.add for safe parallel updates.
    """
    # Input parameters
    repo_url: str
    pdf_path: str
    rubric_dimensions: List[Dict]

    # Detective outputs - use operator.ior to merge dicts from parallel branches
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior]

    # Judge outputs - use operator.add to concatenate lists from parallel branches
    opinions: Annotated[List[JudicialOpinion], operator.add]

    # Final synthesis
    final_report: str

    # Error tracking
    errors: Annotated[List[str], operator.add]
