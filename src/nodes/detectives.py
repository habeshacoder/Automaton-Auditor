"""
Detective Layer - Forensic evidence collection agents
"""

from typing import Dict, List
from pathlib import Path
from src.nodes.state_models import AgentState, Evidence
from src.tools.git_tools import GitTool
from src.tools.ast_tools import ASTAnalyzer
from src.tools.pdf_tools import PDFAnalyzer


def repo_investigator_node(state: AgentState) -> Dict:
    """
    Detective 1: RepoInvestigator - Code forensics
    Collects evidence from GitHub repository.
    """
    print("\n" + "=" * 60)
    print("🕵️  DETECTIVE: RepoInvestigator")
    print("=" * 60)

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

        evidence = Evidence(
            goal="Git Forensic Analysis",
            found=commit_count > 0,
            content=f"Commits: {commit_count}, Pattern: {commit_pattern}. Sample: {commits[:3] if commits else []}",
            location=".git/",
            rationale=f"Pattern: {commit_pattern} with {commit_count} commits",
            confidence=0.95 if commit_count > 3 else 0.5,
        )
        evidences.append(evidence)

        # Log evidence to console
        print(f"\n📋 Evidence Collected:")
        print(f"   Goal: {evidence.goal}")
        print(f"   Found: {'✅ Yes' if evidence.found else '❌ No'}")
        print(f"   Location: {evidence.location}")
        print(f"   Content: {evidence.content}")
        print(f"   Rationale: {evidence.rationale}")
        print(f"   Confidence: {evidence.confidence:.0%}")

        # State management rigor
        ast_analyzer = ASTAnalyzer(repo_path)
        found_state, state_file, state_snippet = ast_analyzer.find_state_definition()

        evidence = Evidence(
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
        evidences.append(evidence)

        # Log evidence to console
        print(f"\n📋 Evidence Collected:")
        print(f"   Goal: {evidence.goal}")
        print(f"   Found: {'✅ Yes' if evidence.found else '❌ No'}")
        print(f"   Location: {evidence.location}")
        print(f"   Content: {evidence.content}")
        print(f"   Rationale: {evidence.rationale}")
        print(f"   Confidence: {evidence.confidence:.0%}")

        # Graph orchestration
        graph_analysis = ast_analyzer.analyze_graph_structure()
        evidence = Evidence(
            goal="Graph Orchestration",
            found=graph_analysis["has_state_graph"],
            content=f"Nodes: {graph_analysis['nodes']}, Parallel: {graph_analysis['parallel_branches']}, Fan-in: {graph_analysis['fan_in_node']}",
            location=graph_analysis.get("location", "src/graph.py"),
            rationale=f"StateGraph {'found' if graph_analysis['has_state_graph'] else 'not found'}, Parallelism: {graph_analysis['parallel_branches']}",
            confidence=0.85 if graph_analysis["has_state_graph"] else 0.2,
        )
        evidences.append(evidence)

        # Log evidence to console
        print(f"\n📋 Evidence Collected:")
        print(f"   Goal: {evidence.goal}")
        print(f"   Found: {'✅ Yes' if evidence.found else '❌ No'}")
        print(f"   Location: {evidence.location}")
        print(f"   Content: {evidence.content}")
        print(f"   Rationale: {evidence.rationale}")
        print(f"   Confidence: {evidence.confidence:.0%}")

        # Security issues
        security_issues = ast_analyzer.check_for_security_issues()
        has_security_issues = len(security_issues) > 0

        evidence = Evidence(
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
        evidences.append(evidence)

        # Log evidence to console
        print(f"\n📋 Evidence Collected:")
        print(f"   Goal: {evidence.goal}")
        print(f"   Found: {'✅ Yes' if evidence.found else '❌ No'}")
        print(f"   Location: {evidence.location}")
        print(f"   Content: {evidence.content}")
        print(f"   Rationale: {evidence.rationale}")
        print(f"   Confidence: {evidence.confidence:.0%}")

    except Exception as e:
        errors.append(f"RepoInvestigator error: {str(e)}")
        has_fatal_error = True
    finally:
        git_tool.cleanup()

    print("\n" + "-" * 40)
    print(f"📊 RepoInvestigator Summary: {len(evidences)} evidence items collected")
    print("-" * 40)

    return {
        "evidences": {"repo": evidences},
        "errors": errors,
        "has_fatal_error": has_fatal_error,
    }


def doc_analyst_node(state: AgentState) -> Dict:
    """
    Detective 2: DocAnalyst - PDF report forensics
    """
    print("\n" + "=" * 60)
    print("🕵️  DETECTIVE: DocAnalyst")
    print("=" * 60)

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

        evidence = Evidence(
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
        evidences.append(evidence)

        # Log evidence to console
        print(f"\n📋 Evidence Collected:")
        print(f"   Goal: {evidence.goal}")
        print(f"   Found: {'✅ Yes' if evidence.found else '❌ No'}")
        print(f"   Location: {evidence.location}")
        print(f"   Content: {evidence.content}")
        print(f"   Rationale: {evidence.rationale}")
        print(f"   Confidence: {evidence.confidence:.0%}")

        evidence = Evidence(
            goal="Documentation Accuracy",
            found=True,
            content=f"PDF mentions {len(file_paths)} file paths: {file_paths[:5]}",
            location="PDF report",
            rationale=f"Extracted {len(file_paths)} file path claims for verification",
            confidence=0.7,
        )
        evidences.append(evidence)

        # Log evidence to console
        print(f"\n📋 Evidence Collected:")
        print(f"   Goal: {evidence.goal}")
        print(f"   Found: {'✅ Yes' if evidence.found else '❌ No'}")
        print(f"   Location: {evidence.location}")
        print(f"   Content: {evidence.content}")
        print(f"   Rationale: {evidence.rationale}")
        print(f"   Confidence: {evidence.confidence:.0%}")

        evidence = Evidence(
            goal="Architectural Claims",
            found=len(claims) > 0,
            content=f"Found {len(claims)} architectural claims",
            location="PDF report",
            rationale=f"Document makes {len(claims)} specific architectural claims",
            confidence=0.75,
        )
        evidences.append(evidence)

        # Log evidence to console
        print(f"\n📋 Evidence Collected:")
        print(f"   Goal: {evidence.goal}")
        print(f"   Found: {'✅ Yes' if evidence.found else '❌ No'}")
        print(f"   Location: {evidence.location}")
        print(f"   Content: {evidence.content}")
        print(f"   Rationale: {evidence.rationale}")
        print(f"   Confidence: {evidence.confidence:.0%}")

    except Exception as e:
        errors.append(f"DocAnalyst error: {str(e)}")

    print("\n" + "-" * 40)
    print(f"📊 DocAnalyst Summary: {len(evidences)} evidence items collected")
    print("-" * 40)

    return {
        "evidences": {"doc": evidences},
        "errors": errors,
        "has_fatal_error": has_fatal_error,
    }


def evidence_aggregator_node(state: AgentState) -> Dict:
    """
    Fan-In Node: Aggregates evidence from all detectives and decides if we can proceed.
    """
    print("\n" + "=" * 60)
    print("🕵️  DETECTIVE: EvidenceAggregator")
    print("=" * 60)

    repo_evidences = state["evidences"].get("repo", [])
    doc_evidences = state["evidences"].get("doc", [])
    errors = state.get("errors", [])
    fatal_flag = state.get("has_fatal_error", False)

    has_repo = len(repo_evidences) > 0

    # Log aggregated evidence
    print(f"\n📊 Evidence Aggregation Summary:")
    print(f"   Repo Evidence: {len(repo_evidences)} items")
    print(f"   Doc Evidence: {len(doc_evidences)} items")
    print(f"   Total Evidence: {len(repo_evidences) + len(doc_evidences)} items")

    # Display all evidence
    print(f"\n📋 All Collected Evidence:")
    for i, ev in enumerate(repo_evidences, 1):
        print(f"\n   Evidence {i} (Repo):")
        print(f"      Goal: {ev.goal}")
        print(f"      Found: {'✅ Yes' if ev.found else '❌ No'}")
        print(f"      Location: {ev.location}")
        print(f"      Content: {ev.content}")
        print(f"      Rationale: {ev.rationale}")
        print(f"      Confidence: {ev.confidence:.0%}")

    for i, ev in enumerate(doc_evidences, 1):
        print(f"\n   Evidence {i} (Doc):")
        print(f"      Goal: {ev.goal}")
        print(f"      Found: {'✅ Yes' if ev.found else '❌ No'}")
        print(f"      Location: {ev.location}")
        print(f"      Content: {ev.content}")
        print(f"      Rationale: {ev.rationale}")
        print(f"      Confidence: {ev.confidence:.0%}")

    # Policy: if no repo evidence or repo failed, treat as fatal and skip judges
    if not has_repo:
        errors.append("Fatal: missing repo evidence; skipping judges.")
        fatal_flag = True
        print(f"\n⚠️  Fatal: missing repo evidence; skipping judges.")

    print("\n" + "-" * 40)
    print(f"✅ EvidenceAggregator Complete")
    print("-" * 40)

    return {
        "errors": errors,
        "has_fatal_error": fatal_flag,
    }

def vision_inspector_node(state: AgentState) -> Dict:
    """
    VisionInspector (Diagram Detective):
    - Scans a diagrams directory (or infers image paths from the PDF/repo).
    - Sends diagrams to a vision LLM.
    - Emits Evidence focused on flow: Detectives -> Aggregation -> Judges -> Synthesis,
      and whether parallelism is clearly depicted.
    """
    print("\n" + "=" * 60)
    print("🕵️  DETECTIVE: VisionInspector")
    print("=" * 60)

    evidences = state.get("evidences", {})
    errors = state.get("errors", [])
    repo_url = state.get("repo_url", "")
    project_root = Path(__file__).parent.parent

    # You can choose a convention: diagrams under ./reports/diagrams or repo/docs/diagrams
    diagrams_root = project_root / "reports" / "diagrams"
    if not diagrams_root.exists():
        # Non-fatal: just record that no diagrams were found
        errors.append("VisionInspector: no diagrams directory found at ./reports/diagrams")
        return {"evidences": evidences, "errors": errors}

    image_paths = list(diagrams_root.glob("*.png")) + list(diagrams_root.glob("*.jpg"))
    if not image_paths:
        errors.append("VisionInspector: no diagram images found")
        return {"evidences": evidences, "errors": errors}

    # Use your chosen vision model.
    # If you’re using OpenRouter + a vision-capable model:
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # or another vision-capable model exposed via your provider
        temperature=0.2,
    )

    vision_evidences = []

    for img_path in image_paths:
        prompt = """
You are the VisionInspector (Diagram Detective).

Forensic Protocol A (Flow Analysis):
- Look at the architectural diagram.
- Determine whether:
  1) Detectives run in parallel,
  2) Their outputs feed into an Evidence Aggregation stage,
  3) Judges (multiple personas) operate in parallel,
  4) A final Synthesis / Chief Justice stage produces a verdict.
- If the flow is shown as a simple linear pipeline without parallel branches, call that out.

Respond with:
- A short classification: "correct_parallel_flow", "mostly_correct", or "linear_or_misleading".
- A concise rationale, referencing visual elements (arrows, swimlanes, labels).
"""

        # langchain_openai’s vision interface uses "image_url" blocks or similar;
        # adapt this to the exact client you’re using.
        # Pseudo-code for multi-modal call:
        result = llm.invoke([
            ("user", [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"file://{img_path}"},
            ])
        ])

        text = result.content if hasattr(result, "content") else str(result)
        # Very simple classification heuristic
        text_lower = text.lower()
        if "correct_parallel_flow" in text_lower:
            classification = "correct_parallel_flow"
        elif "mostly_correct" in text_lower:
            classification = "mostly_correct"
        elif "linear_or_misleading" in text_lower:
            classification = "linear_or_misleading"
        else:
            classification = "unknown"

        ev = Evidence(
            goal="Analyze diagram flow from Detectives (Parallel) -> Evidence Aggregation -> Judges (Parallel) -> Synthesis",
            found=classification != "unknown",
            location=str(img_path),
            content=text,
            rationale=f"VisionInspector classification: {classification}",
            confidence=0.7,
        )
        vision_evidences.append(ev)

        # Log evidence to console
        print(f"\n📋 Evidence Collected:")
        print(f"   Goal: {ev.goal}")
        print(f"   Found: {'✅ Yes' if ev.found else '❌ No'}")
        print(f"   Location: {ev.location}")
        print(f"   Content: {ev.content}")
        print(f"   Rationale: {ev.rationale}")
        print(f"   Confidence: {ev.confidence:.0%}")

    evidences.setdefault("vision_inspector", []).extend(vision_evidences)

    print("\n" + "-" * 40)
    print(f"📊 VisionInspector Summary: {len(vision_evidences)} evidence items collected")
    print("-" * 40)

    return {"evidences": evidences, "errors": errors}
