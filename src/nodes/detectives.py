"""
Detective Layer - Forensic evidence collection agents
"""

from typing import Dict, List
from src.nodes.state_models import AgentState, Evidence
from src.tools.git_tools import GitTool
from src.tools.ast_tools import ASTAnalyzer
from src.tools.pdf_tools import PDFAnalyzer


def repo_investigator_node(state: AgentState) -> Dict:
    """
    Detective 1: RepoInvestigator - Code forensics
    Collects evidence from GitHub repository.
    """
    repo_url = state["repo_url"]
    evidences: List[Evidence] = []
    errors: List[str] = []

    git_tool = GitTool()
    has_fatal_error = False

    try:
        # Clone repo
        success, message, repo_path = git_tool.clone_repo(repo_url)

        if not success or not repo_path:
            errors.append(f"Failed to clone repo: {message}")
            has_fatal_error = True
            return {
                "evidences": {"repo": evidences},
                "errors": errors,
                "has_fatal_error": has_fatal_error,
            }

        # Git forensic analysis
        ok_history, commits = git_tool.extract_git_history(repo_path)
        commit_count = len(commits) if ok_history else 0
        commit_pattern = git_tool.classify_commit_pattern(commits) if ok_history else "unknown"

        evidences.append(
            Evidence(
                goal="Git Forensic Analysis",
                found=commit_count > 0,
                content=f"Commits: {commit_count}, Pattern: {commit_pattern}. Sample: {commits[:3] if commits else []}",
                location=".git/",
                rationale=f"Pattern: {commit_pattern} with {commit_count} commits",
                confidence=0.95 if commit_count > 3 else 0.5,
            )
        )

        # State management rigor
        ast_analyzer = ASTAnalyzer(repo_path)
        found_state, state_file, state_snippet = ast_analyzer.find_state_definition()

        evidences.append(
            Evidence(
                goal="State Management Rigor",
                found=found_state,
                content=state_snippet if found_state else None,
                location=state_file or "src/state.py (not found)",
                rationale=(
                    "Found typed state with Pydantic/TypedDict"
                    if found_state
                    else "No typed state definition found"
                ),
                confidence=0.9 if found_state else 0.3,
            )
        )

        # Graph orchestration
        graph_analysis = ast_analyzer.analyze_graph_structure()
        evidences.append(
            Evidence(
                goal="Graph Orchestration",
                found=graph_analysis["has_state_graph"],
                content=f"Nodes: {graph_analysis['nodes']}, Parallel: {graph_analysis['parallel_branches']}, Fan-in: {graph_analysis['fan_in_node']}",
                location=graph_analysis.get("location", "src/graph.py"),
                rationale=f"StateGraph {'found' if graph_analysis['has_state_graph'] else 'not found'}, Parallelism: {graph_analysis['parallel_branches']}",
                confidence=0.85 if graph_analysis["has_state_graph"] else 0.2,
            )
        )

        # Security issues
        security_issues = ast_analyzer.check_for_security_issues()
        has_security_issues = len(security_issues) > 0

        evidences.append(
            Evidence(
                goal="Safe Tool Engineering",
                found=not has_security_issues,
                content=(
                    str(security_issues) if has_security_issues else "No security issues detected"
                ),
                location="src/tools/",
                rationale=(
                    "Safe sandboxed operations"
                    if not has_security_issues
                    else f"Found {len(security_issues)} security issues"
                ),
                confidence=0.9 if not has_security_issues else 0.3,
            )
        )

    except Exception as e:
        errors.append(f"RepoInvestigator error: {str(e)}")
        has_fatal_error = True
    finally:
        git_tool.cleanup()

    return {
        "evidences": {"repo": evidences},
        "errors": errors,
        "has_fatal_error": has_fatal_error,
    }


def doc_analyst_node(state: AgentState) -> Dict:
    """
    Detective 2: DocAnalyst - PDF report forensics
    """
    pdf_path = state["pdf_path"]
    evidences: List[Evidence] = []
    errors: List[str] = []
    has_fatal_error = False  # usually doc failure is not fatal for code audit

    try:
        pdf_analyzer = PDFAnalyzer(pdf_path)

        key_concepts = [
            "Dialectical Synthesis",
            "Fan-In",
            "Fan-Out",
            "Metacognition",
            "State Synchronization",
        ]
        concept_results = pdf_analyzer.query_terms(key_concepts)
        found_concepts = [k for k, v in concept_results.items() if v]

        deep_understanding_results = []
        for concept in found_concepts:
            has_depth, evidence_text = pdf_analyzer.verify_deep_understanding(concept)
            deep_understanding_results.append(
                {
                    "concept": concept,
                    "has_depth": has_depth,
                    "evidence": evidence_text,
                }
            )

        evidences.append(
            Evidence(
                goal="Theoretical Depth",
                found=len(found_concepts) > 0,
                content=f"Found concepts: {found_concepts}. Deep understanding: {[r['concept'] for r in deep_understanding_results if r['has_depth']]}",
                location="PDF report",
                rationale=f"Document shows deep understanding for {len([r for r in deep_understanding_results if r['has_depth']])} concepts",
                confidence=(
                    0.8
                    if len([r for r in deep_understanding_results if r["has_depth"]]) > 2
                    else 0.5
                ),
            )
        )

        file_paths = pdf_analyzer.file_paths_mentioned
        evidences.append(
            Evidence(
                goal="Documentation Accuracy",
                found=True,
                content=f"PDF mentions {len(file_paths)} file paths: {file_paths[:5]}",
                location="PDF report",
                rationale=f"Extracted {len(file_paths)} file path claims for verification",
                confidence=0.7,
            )
        )

        claims = pdf_analyzer.extract_architectural_claims()
        evidences.append(
            Evidence(
                goal="Architectural Claims",
                found=len(claims) > 0,
                content=f"Found {len(claims)} architectural claims",
                location="PDF report",
                rationale=f"Document makes {len(claims)} specific architectural claims",
                confidence=0.75,
            )
        )

    except Exception as e:
        errors.append(f"DocAnalyst error: {str(e)}")

    return {
        "evidences": {"doc": evidences},
        "errors": errors,
        "has_fatal_error": has_fatal_error,
    }


def evidence_aggregator_node(state: AgentState) -> Dict:
    """
    Fan-In Node: Aggregates evidence from all detectives and decides if we can proceed.
    """
    repo_evidences = state["evidences"].get("repo", [])
    doc_evidences = state["evidences"].get("doc", [])
    errors = state.get("errors", [])
    fatal_flag = state.get("has_fatal_error", False)

    has_repo = len(repo_evidences) > 0

    # Policy: if no repo evidence or repo failed, treat as fatal and skip judges
    if not has_repo:
        errors.append("Fatal: missing repo evidence; skipping judges.")
        fatal_flag = True

    return {
        "errors": errors,
        "has_fatal_error": fatal_flag,
    }
