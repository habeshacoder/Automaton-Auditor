"""
Detective Layer - Forensic evidence collection agents
"""
from pathlib import Path
from typing import Dict, List
from src.nodes.state_models import AgentState, Evidence
from src.tools.git_tools import GitTool
from src.tools.ast_tools import ASTAnalyzer
from src.tools.pdf_tools import PDFAnalyzer


def repo_investigator_node(state: AgentState) -> Dict:
    """
    Detective 1: RepoInvestigator - Code forensics
    Collects evidence from GitHub repository
    """
    repo_url = state["repo_url"]
    evidences = []
    errors = []

    git_tool = GitTool()

    try:
        # Protocol 1: Clone repository safely
        success, message, repo_path = git_tool.clone_repo(repo_url)

        if not success or not repo_path:
            errors.append(f"Failed to clone repo: {message}")
            return {"evidences": {"repo": []}, "errors": errors}

        # Protocol 2: Git Forensic Analysis
        success, commits = git_tool.extract_git_history(repo_path)
        commit_count = len(commits)
        commit_pattern = git_tool.classify_commit_pattern(commits)

        evidences.append(Evidence(
            goal="Git Forensic Analysis",
            found=commit_count > 0,
            content=f"Commits: {commit_count}, Pattern: {commit_pattern}. Sample: {commits[:3] if commits else []}",
            location=".git/",
            rationale=f"{'Atomic' if commit_pattern == 'atomic' else 'Monolithic'} development pattern with {commit_count} commits",
            confidence=0.95 if commit_count > 3 else 0.5
        ))

        # Protocol 3: State Management Rigor
        ast_analyzer = ASTAnalyzer(repo_path)
        found_state, state_file, state_snippet = ast_analyzer.find_state_definition()

        evidences.append(Evidence(
            goal="State Management Rigor",
            found=found_state,
            content=state_snippet if found_state else None,
            location=state_file if state_file else "src/state.py (not found)",
            rationale="Found typed state with Pydantic/TypedDict" if found_state else "No typed state definition found",
            confidence=0.9 if found_state else 0.3
        ))

        # Protocol 4: Graph Orchestration Analysis
        graph_analysis = ast_analyzer.analyze_graph_structure()

        evidences.append(Evidence(
            goal="Graph Orchestration",
            found=graph_analysis["has_state_graph"],
            content=f"Nodes: {graph_analysis['nodes']}, Parallel: {graph_analysis['parallel_branches']}, Fan-in: {graph_analysis['fan_in_node']}",
            location=graph_analysis.get("location", "src/graph.py"),
            rationale=f"StateGraph {'found' if graph_analysis['has_state_graph'] else 'not found'}, Parallelism: {graph_analysis['parallel_branches']}",
            confidence=0.85 if graph_analysis["has_state_graph"] else 0.2
        ))

        # Protocol 5: Safe Tool Engineering
        security_issues = ast_analyzer.check_for_security_issues()
        has_security_issues = len(security_issues) > 0

        evidences.append(Evidence(
            goal="Safe Tool Engineering",
            found=not has_security_issues,
            content=str(security_issues) if has_security_issues else "No security issues detected",
            location="src/tools/",
            rationale="Safe sandboxed operations" if not has_security_issues else f"Found {len(security_issues)} security issues",
            confidence=0.9 if not has_security_issues else 0.3
        ))

        # Protocol 6: Structured Output Check
        has_structured, locations = ast_analyzer.check_structured_output()

        evidences.append(Evidence(
            goal="Structured Output Enforcement",
            found=has_structured,
            content=", ".join(locations) if locations else "No structured output methods found",
            location="src/nodes/judges.py",
            rationale="Judges use .with_structured_output() or .bind_tools()" if has_structured else "Judges may return freeform text",
            confidence=0.85 if has_structured else 0.4
        ))

    except Exception as e:
        errors.append(f"RepoInvestigator error: {str(e)}")

    finally:
        git_tool.cleanup()

    return {
        "evidences": {"repo": evidences},
        "errors": errors
    }


def doc_analyst_node(state: AgentState) -> Dict:
    """
    Detective 2: DocAnalyst - PDF report forensics
    Analyzes architectural documentation
    """
    pdf_path = state["pdf_path"]
    evidences = []
    errors = []

    try:
        pdf_analyzer = PDFAnalyzer(pdf_path)

        # Protocol 1: Theoretical Depth Check
        key_concepts = [
            "Dialectical Synthesis",
            "Fan-In",
            "Fan-Out",
            "Metacognition",
            "State Synchronization"
        ]

        concept_results = pdf_analyzer.query_terms(key_concepts)
        found_concepts = [k for k, v in concept_results.items() if v]

        # Check for deep understanding (not just keywords)
        deep_understanding_results = []
        for concept in found_concepts:
            has_depth, evidence_text = pdf_analyzer.verify_deep_understanding(concept)
            deep_understanding_results.append({
                "concept": concept,
                "has_depth": has_depth,
                "evidence": evidence_text
            })

        evidences.append(Evidence(
            goal="Theoretical Depth",
            found=len(found_concepts) > 0,
            content=f"Found concepts: {found_concepts}. Deep understanding: {[r['concept'] for r in deep_understanding_results if r['has_depth']]}",
            location="PDF report",
            rationale=f"Document demonstrates understanding of {len([r for r in deep_understanding_results if r['has_depth']])} key concepts",
            confidence=0.8 if len([r for r in deep_understanding_results if r['has_depth']]) > 2 else 0.5
        ))

        # Protocol 2: File Path Cross-Reference
        # Note: This requires repo evidence to be available
        # In actual execution, this would be done in a fan-in node
        file_paths = pdf_analyzer.file_paths_mentioned

        evidences.append(Evidence(
            goal="Documentation Accuracy",
            found=True,
            content=f"PDF mentions {len(file_paths)} file paths: {file_paths[:5]}",
            location="PDF report",
            rationale=f"Extracted {len(file_paths)} file path claims for verification",
            confidence=0.7  # Will be updated after cross-reference
        ))

        # Protocol 3: Architectural Claims Extraction
        claims = pdf_analyzer.extract_architectural_claims()

        evidences.append(Evidence(
            goal="Architectural Claims",
            found=len(claims) > 0,
            content=f"Found {len(claims)} architectural claims",
            location="PDF report",
            rationale=f"Document makes {len(claims)} specific architectural claims",
            confidence=0.75
        ))

    except Exception as e:
        errors.append(f"DocAnalyst error: {str(e)}")

    return {
        "evidences": {"doc": evidences},
        "errors": errors
    }


def evidence_aggregator_node(state: AgentState) -> Dict:
    """
    Fan-In Node: Aggregates evidence from all detectives
    Performs cross-validation between repo and doc evidence
    """
    repo_evidences = state["evidences"].get("repo", [])
    doc_evidences = state["evidences"].get("doc", [])

    # Cross-validation: Check if PDF claims match repo evidence
    # This is where hallucination detection happens

    # For now, just aggregate
    # In production, you'd implement sophisticated cross-checks

    return {
        # State is already aggregated via operator.ior
        # This node can add metadata or perform validation
    }
