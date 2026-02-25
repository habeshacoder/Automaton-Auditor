"""
Judicial Layer - Three distinct judge personas with LLM backing
"""
from typing import Dict, List
from src.nodes.state_models import AgentState, JudicialOpinion, Evidence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError
import os


class JudgeAgent:
    """Base class for Judge agents with structured output"""

    def __init__(self, persona: str, rubric_logic: Dict):
        self.persona = persona
        self.rubric_logic = rubric_logic

        # Initialize LLM with structured output
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0.3  # Lower temperature for more deterministic judging
        ).with_structured_output(JudicialOpinion)

        # Persona-specific system prompts
        self.system_prompts = {
            "Prosecutor": """You are THE PROSECUTOR in a code quality trial.

Core Philosophy: "Trust No One. Assume Vibe Coding."

Your role:
- Scrutinize evidence for gaps, security flaws, and laziness
- Look for bypassed structures and missing implementations
- Charge defendants with specific violations
- Provide harsh but fair scores backed by evidence
- Focus on what's MISSING or BROKEN

Scoring Guidelines:
- Score 1: Critical failures, security issues, or fundamental misunderstandings
- Score 2: Major gaps with some attempt at implementation
- Score 3: Basic implementation but with significant flaws
- Score 4: Solid implementation with minor issues
- Score 5: Only if absolutely flawless (rare)

Be the critical voice that ensures quality standards.""",

            "Defense": """You are THE DEFENSE ATTORNEY in a code quality trial.

Core Philosophy: "Reward Effort and Intent. Look for the Spirit of the Law."

Your role:
- Highlight creative workarounds and deep thinking
- Recognize the engineering journey, not just the final state
- Advocate for partial credit when effort is evident
- Look at git history for iteration and learning
- Find the strengths even in imperfect implementations

Scoring Guidelines:
- Score 1: Only if absolutely no effort or understanding shown
- Score 2: Some effort but fundamental misunderstanding
- Score 3: Good effort with partial understanding
- Score 4: Strong understanding with minor execution issues
- Score 5: Deep understanding and solid execution

Be the voice that recognizes genuine engineering effort.""",

            "TechLead": """You are THE TECH LEAD in a code quality trial.

Core Philosophy: "Does it actually work? Is it maintainable?"

Your role:
- Evaluate practical viability and technical soundness
- Assess architectural decisions and code quality
- Ignore both harsh criticism and generous praise
- Focus on: Does it work? Can it be maintained? Is it production-ready?
- Be the tie-breaker with pragmatic judgment

Scoring Guidelines:
- Score 1: Broken, unmaintainable, or fundamentally flawed
- Score 2: Works partially but has significant technical debt
- Score 3: Works adequately but not production-grade
- Score 4: Production-ready with minor improvements needed
- Score 5: Excellent architecture and implementation

Be the pragmatic voice of technical reality."""
        }

    def create_prompt(self, criterion_id: str, evidences: List[Evidence]) -> str:
        """Create persona-specific prompt with rubric logic"""

        system_prompt = self.system_prompts[self.persona]
        rubric_instruction = self.rubric_logic.get(self.persona.lower(), "")

        # Format evidence
        evidence_text = "\n\n".join([
            f"Evidence {i+1}: {ev.goal}\n"
            f"  Found: {ev.found}\n"
            f"  Location: {ev.location}\n"
            f"  Content: {ev.content}\n"
            f"  Rationale: {ev.rationale}\n"
            f"  Confidence: {ev.confidence}"
            for i, ev in enumerate(evidences)
        ])

        user_prompt = f"""Evaluate criterion: {criterion_id}

Rubric Instructions for {self.persona}:
{rubric_instruction}

Evidence Collected:
{evidence_text}

Provide your judicial opinion with:
1. A score from 1-5
2. Detailed argument supporting your score
3. Specific evidence citations

Remember your role as {self.persona}. Be consistent with your persona's philosophy."""

        return system_prompt, user_prompt


    def evaluate(self, criterion_id: str, evidences: List[Evidence]) -> JudicialOpinion:
        """
        Evaluate evidence and return structured opinion
        """
        system_prompt, user_prompt = self.create_prompt(criterion_id, evidences)

        try:
            # Create messages
            messages = [
                ("system", system_prompt),
                ("user", user_prompt)
            ]

            # Invoke LLM with structured output
            opinion = self.llm.invoke(messages)

            # Ensure judge field is set correctly
            opinion.judge = self.persona
            opinion.criterion_id = criterion_id

            # Validate opinion
            if not (1 <= opinion.score <= 5):
                opinion.score = 3  # Default to middle score if invalid

            return opinion

        except ValidationError as e:
            # Fallback if structured output fails
            return JudicialOpinion(
                judge=self.persona,
                criterion_id=criterion_id,
                score=3,
                argument=f"Error in structured output: {str(e)}. Defaulting to neutral score.",
                cited_evidence=[ev.goal for ev in evidences]
            )
        except Exception as e:
            return JudicialOpinion(
                judge=self.persona,
                criterion_id=criterion_id,
                score=1,
                argument=f"Evaluation error: {str(e)}",
                cited_evidence=[]
            )


def prosecutor_node(state: AgentState) -> Dict:
    """Judge Node 1: The Prosecutor"""
    opinions = []
    errors = []

    try:
        # Get all evidence
        all_evidences = []
        for detective_type, evidence_list in state["evidences"].items():
            all_evidences.extend(evidence_list)

        # Get rubric dimensions
        for dimension in state["rubric_dimensions"]:
            if dimension["target_artifact"] == "github_repo":
                criterion_id = dimension["id"]
                rubric_logic = dimension["judicial_logic"]

                # Filter relevant evidence for this criterion
                relevant_evidence = [
                    ev for ev in all_evidences 
                    if any(keyword in ev.goal.lower() 
                           for keyword in criterion_id.split("_"))
                ]

                if not relevant_evidence:
                    relevant_evidence = all_evidences  # Use all if none match

                judge = JudgeAgent("Prosecutor", rubric_logic)
                opinion = judge.evaluate(criterion_id, relevant_evidence)
                opinions.append(opinion)

    except Exception as e:
        errors.append(f"Prosecutor error: {str(e)}")

    return {
        "opinions": opinions,
        "errors": errors
    }


def defense_node(state: AgentState) -> Dict:
    """Judge Node 2: The Defense Attorney"""
    opinions = []
    errors = []

    try:
        all_evidences = []
        for detective_type, evidence_list in state["evidences"].items():
            all_evidences.extend(evidence_list)

        for dimension in state["rubric_dimensions"]:
            if dimension["target_artifact"] == "github_repo":
                criterion_id = dimension["id"]
                rubric_logic = dimension["judicial_logic"]

                relevant_evidence = [
                    ev for ev in all_evidences 
                    if any(keyword in ev.goal.lower() 
                           for keyword in criterion_id.split("_"))
                ]

                if not relevant_evidence:
                    relevant_evidence = all_evidences

                judge = JudgeAgent("Defense", rubric_logic)
                opinion = judge.evaluate(criterion_id, relevant_evidence)
                opinions.append(opinion)

    except Exception as e:
        errors.append(f"Defense error: {str(e)}")

    return {
        "opinions": opinions,
        "errors": errors
    }


def tech_lead_node(state: AgentState) -> Dict:
    """Judge Node 3: The Tech Lead"""
    opinions = []
    errors = []

    try:
        all_evidences = []
        for detective_type, evidence_list in state["evidences"].items():
            all_evidences.extend(evidence_list)

        for dimension in state["rubric_dimensions"]:
            if dimension["target_artifact"] == "github_repo":
                criterion_id = dimension["id"]
                rubric_logic = dimension["judicial_logic"]

                relevant_evidence = [
                    ev for ev in all_evidences 
                    if any(keyword in ev.goal.lower() 
                           for keyword in criterion_id.split("_"))
                ]

                if not relevant_evidence:
                    relevant_evidence = all_evidences

                judge = JudgeAgent("TechLead", rubric_logic)
                opinion = judge.evaluate(criterion_id, relevant_evidence)
                opinions.append(opinion)

    except Exception as e:
        errors.append(f"TechLead error: {str(e)}")

    return {
        "opinions": opinions,
        "errors": errors
    }
