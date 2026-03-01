"""
Chief Justice - Final synthesis and report generation
"""

from typing import Dict, List
from collections import defaultdict
from src.nodes.state_models import AgentState, JudicialOpinion


def chief_justice_node(state: AgentState) -> Dict:
    """
    Synthesize all judicial opinions into final verdict
    Applies deterministic conflict resolution rules
    """
    print("\n" + "=" * 60)
    print("👑 CHIEF JUSTICE: Final Synthesis")
    print("=" * 60)
    print("Role: Synthesizing all judicial opinions into final verdict\n")

    opinions = state["opinions"]
    synthesis_rules = _get_synthesis_rules(state)

    # Group opinions by criterion
    opinions_by_criterion = defaultdict(list)
    for opinion in opinions:
        opinions_by_criterion[opinion.criterion_id].append(opinion)

    # Log all opinions being synthesized
    print("\n📋 All Judicial Opinions to be Synthesized:")
    for criterion_id, criterion_opinions in opinions_by_criterion.items():
        print(f"\n  Criterion: {criterion_id}")
        for opinion in criterion_opinions:
            print(f"    - {opinion.judge}: {opinion.score}/5")

    # Apply synthesis rules
    final_verdicts = {}
    dissent_summaries = {}

    for criterion_id, criterion_opinions in opinions_by_criterion.items():
        verdict, dissent = _synthesize_criterion(criterion_id, criterion_opinions, synthesis_rules)
        final_verdicts[criterion_id] = verdict
        dissent_summaries[criterion_id] = dissent

        # Log verdict synthesis
        print(f"\n📋 Verdict Synthesis for '{criterion_id}':")
        print(f"   Final Score: {verdict}/5")
        print(f"   Dissent Summary: {dissent}")

    # Generate markdown report
    report = _generate_markdown_report(
        final_verdicts, dissent_summaries, opinions_by_criterion, state
    )

    print("\n" + "-" * 40)
    print(f"📊 Chief Justice Summary: {len(final_verdicts)} verdicts synthesized")
    print("-" * 40)

    return {"final_report": report}


def _get_synthesis_rules(state: AgentState) -> Dict:
    """Extract synthesis rules from rubric"""
    return {
        "security_override": "Confirmed security flaws cap total score at 3",
        "fact_supremacy": "Forensic evidence always overrules judicial opinion",
        "dissent_requirement": "Must summarize why Prosecutor and Defense disagreed",
    }


def _synthesize_criterion(
    criterion_id: str, opinions: List[JudicialOpinion], rules: Dict
) -> tuple[int, str]:
    """
    Apply deterministic rules to resolve judicial conflict
    Returns:
        (final_score, dissent_summary)
    """
    print(f"\n  🔍 Synthesizing '{criterion_id}'...")

    if not opinions:
        return 1, "No opinions provided"

    scores_by_judge = {op.judge: op.score for op in opinions}

    prosecutor_score = scores_by_judge.get("Prosecutor", 3)
    defense_score = scores_by_judge.get("Defense", 3)
    tech_lead_score = scores_by_judge.get("TechLead", 3)

    # Log individual judge scores
    print(f"    Prosecutor Score: {prosecutor_score}/5")
    print(f"    Defense Score: {defense_score}/5")
    print(f"    TechLead Score: {tech_lead_score}/5")

    # Security Override
    security_keywords = ["security", "os.system", "injection", "sanitization"]
    prosecutor_opinion = next((op for op in opinions if op.judge == "Prosecutor"), None)

    if prosecutor_opinion and prosecutor_score <= 2:
        if any(keyword in prosecutor_opinion.argument.lower() for keyword in security_keywords):
            final_score = min(3, max(prosecutor_score, defense_score, tech_lead_score))
            dissent = (
                "Security override applied. Prosecutor flagged security issues, "
                "capping score at 3."
            )
            print(f"    ⚠️  Security Override Applied - Final Score: {final_score}/5")
            return final_score, dissent

    # Fact Supremacy (TechLead weighted double)
    weighted_score = (prosecutor_score + defense_score + (tech_lead_score * 2)) / 4

    final_score = round(weighted_score)
    final_score = max(1, min(5, final_score))

    score_variance = max(prosecutor_score, defense_score, tech_lead_score) - min(
        prosecutor_score, defense_score, tech_lead_score
    )

    print(f"    Weighted Score Calculation: ({prosecutor_score} + {defense_score} + {tech_lead_score}*2) / 4 = {weighted_score:.2f}")
    print(f"    Final Score (clamped 1-5): {final_score}/5")

    if score_variance > 2:
        dissent = (
            f"Significant disagreement (variance: {score_variance}). "
            f"Prosecutor: {prosecutor_score}, "
            f"Defense: {defense_score}, "
            f"TechLead: {tech_lead_score}. "
            "Tech Lead's practical assessment weighted double in synthesis."
        )
        print(f"    ⚠️  Significant Disagreement Detected - Variance: {score_variance}")
    else:
        dissent = (
            f"Judges reached consensus. Scores ranged from "
            f"{min(prosecutor_score, defense_score, tech_lead_score)} "
            f"to {max(prosecutor_score, defense_score, tech_lead_score)}."
        )
        print(f"    ✅ Consensus Reached")

    return final_score, dissent


def _generate_markdown_report(
    verdicts: Dict[str, int],
    dissents: Dict[str, str],
    opinions_by_criterion: Dict[str, List[JudicialOpinion]],
    state: AgentState,
) -> str:
    """Generate professional markdown audit report"""

    overall_score = sum(verdicts.values()) / len(verdicts) if verdicts else 0

    report = ""
    report += "# 🏛️ Automaton Auditor Report\n\n"
    report += "## Executive Summary\n\n"
    report += f"**Repository:** {state['repo_url']}\n"
    report += f"**Report Date:** {_get_timestamp()}\n"
    report += f"**Overall Score:** {overall_score:.2f} / 5.0\n\n"
    report += (
        "This report was generated by the Automaton Auditor, "
        "a multi-agent system implementing a Digital Courtroom "
        "architecture with specialized Detective and Judge agents.\n\n"
    )
    report += "---\n\n"
    report += "## 🔍 Detective Evidence Collection\n\n"
    report += "Structured evidence collected by Detective agents during the forensic analysis:\n\n"

    # Display evidence by source
    evidences = state.get("evidences", {})
    for source, evidence_list in evidences.items():
        report += f"### 🕵️ {source.replace('_', ' ').title()}\n\n"
        if evidence_list:
            for i, evidence in enumerate(evidence_list, 1):
                report += f"#### Evidence {i}: {evidence.goal}\n\n"
                report += f"- **Found:** {'✅ Yes' if evidence.found else '❌ No'}\n"
                report += f"- **Location:** {evidence.location}\n"
                report += f"- **Content:** {evidence.content or 'N/A'}\n"
                report += f"- **Rationale:** {evidence.rationale}\n"
                report += f"- **Confidence:** {evidence.confidence:.0%}\n\n"
        else:
            report += "*No evidence collected for this source.*\n\n"
        report += "---\n\n"

    report += "## 📊 Final Verdicts\n\n"

    for criterion_id, score in verdicts.items():
        criterion_name = criterion_id.replace("_", " ").title()
        score_emoji = _get_score_emoji(score)

        report += f"### {score_emoji} {criterion_name}\n\n"
        report += f"**Final Score:** {score} / 5\n\n"
        report += f"**Synthesis:** " f"{dissents.get(criterion_id, 'No dissent recorded')}\n\n"

        if criterion_id in opinions_by_criterion:
            report += "**Judge Opinions:**\n\n"
            for opinion in opinions_by_criterion[criterion_id]:
                snippet = opinion.argument[:200]
                report += (
                    f"- **{opinion.judge}** " f"(Score: {opinion.score}/5): " f"{snippet}...\n"
                )
            report += "\n"

    report += "---\n\n"
    report += "## ⚖️ Dialectical Analysis\n\n"
    report += "The Digital Courtroom operates on a " "thesis-antithesis-synthesis model:\n\n"

    for criterion_id, criterion_opinions in opinions_by_criterion.items():
        criterion_name = criterion_id.replace("_", " ").title()
        report += f"### {criterion_name}\n\n"

        prosecutor = next((op for op in criterion_opinions if op.judge == "Prosecutor"), None)
        defense = next((op for op in criterion_opinions if op.judge == "Defense"), None)
        tech_lead = next((op for op in criterion_opinions if op.judge == "TechLead"), None)

        if prosecutor:
            report += f"**Prosecutor (Critical Lens):** Score {prosecutor.score}/5\n"
            report += f"- {prosecutor.argument}\n\n"

        if defense:
            report += f"**Defense (Optimistic Lens):** Score {defense.score}/5\n"
            report += f"- {defense.argument}\n\n"

        if tech_lead:
            report += f"**Tech Lead (Pragmatic Lens):** Score {tech_lead.score}/5\n"
            report += f"- {tech_lead.argument}\n\n"

        report += f"**Resolution:** " f"{dissents.get(criterion_id, 'Consensus reached')}\n\n"
        report += "---\n\n"

    report += "## 🔧 Remediation Plan\n\n"

    for criterion_id, score in verdicts.items():
        if score < 4:
            criterion_name = criterion_id.replace("_", " ").title()
            report += f"### {criterion_name} (Score: {score}/5)\n\n"
            report += "**Recommended Actions:**\n\n"

            for opinion in opinions_by_criterion.get(criterion_id, []):
                if opinion.score < 4:
                    report += f"- **From {opinion.judge}:** "

                    arg_lower = opinion.argument.lower()

                    if "missing" in arg_lower:
                        report += "Implement missing components\n"
                    elif "security" in arg_lower:
                        report += "Address security vulnerabilities\n"
                    elif "parallel" in arg_lower:
                        report += "Implement proper parallelism\n"
                    else:
                        report += f"{opinion.argument[:100]}...\n"

            report += "\n"

    report += "---\n\n"
    report += "## 📝 Methodology\n\n"
    report += (
        "1. **Detective Layer:** Parallel evidence collection\n"
        "2. **Judicial Layer:** Three-persona dialectical evaluation\n"
        "3. **Synthesis Layer:** Deterministic conflict resolution\n\n"
        "**Evidence Sources:**\n"
        "- Git forensic analysis\n"
        "- AST-based code structure analysis\n"
        "- PDF documentation cross-referencing\n"
        "- Security and best practice scanning\n\n"
    )

    report += "---\n\n"
    report += "_This report was generated by an AI agent system. " "Human review recommended._\n"

    return report


def _get_score_emoji(score: int) -> str:
    if score >= 5:
        return "🌟"
    elif score >= 4:
        return "✅"
    elif score >= 3:
        return "⚠️"
    else:
        return "❌"


def _get_timestamp() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
