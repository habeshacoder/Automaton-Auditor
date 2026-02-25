"""
Main entry point for Automaton Auditor
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime
from src.config import Config
from src.graph import build_audit_graph
from src.nodes.state_models import AgentState


def run_audit(repo_url: str, pdf_path: str, output_dir: str = None) -> str:
    """
    Execute the complete audit pipeline

    Args:
        repo_url: GitHub repository URL
        pdf_path: Path to PDF report
        output_dir: Directory to save audit report

    Returns:
        Path to generated audit report
    """
    print("\n" + "=" * 60)
    print("🏛️  AUTOMATON AUDITOR - DIGITAL COURTROOM")
    print("=" * 60)

    # Validate configuration
    Config.display()
    issues = Config.validate()

    if issues:
        print("\n❌ Cannot proceed with configuration issues")
        return None

    # Build the graph
    print("\n📊 Building StateGraph...")
    graph = build_audit_graph()
    print("✅ Graph compiled successfully")

    # Initialize state
    initial_state: AgentState = {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "rubric_dimensions": [],
        "evidences": {},
        "opinions": [],
        "final_report": "",
        "errors": []
    }

    print(f"\n🔍 Starting audit...")
    print(f"  Repository: {repo_url}")
    print(f"  PDF Report: {pdf_path}")

    try:
        # Execute the graph
        print("\n⚙️  Executing agent swarm...")

        # Show progress
        print("  [1/6] Loading rubric...")
        print("  [2/6] Collecting evidence (Detectives)...")
        print("  [3/6] Aggregating evidence...")
        print("  [4/6] Rendering judicial opinions...")
        print("  [5/6] Synthesizing verdict (Chief Justice)...")

        final_state = graph.invoke(initial_state)

        print("  [6/6] Generating report...")

        # Extract report
        report = final_state.get("final_report", "")

        if not report:
            print("\n❌ Failed to generate report")
            return None

        # Save report
        if output_dir is None:
            output_dir = Config.AUDIT_OUTPUT_DIR / "report_onself_generated"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"audit_report_{timestamp}.md"

        with open(report_file, "w") as f:
            f.write(report)

        print(f"\n✅ Audit complete!")
        print(f"📄 Report saved to: {report_file}")

        # Display errors if any
        errors = final_state.get("errors", [])
        if errors:
            print(f"\n⚠️  {len(errors)} warnings/errors occurred:")
            for error in errors[:5]:  # Show first 5
                print(f"  - {error}")

        print("\n" + "=" * 60)

        return str(report_file)

    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Automaton Auditor - Multi-Agent Code Quality Assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audit a repository with PDF report
  python -m src.main \\
    --repo https://github.com/user/repo \\
    --pdf report.pdf

  # Audit with custom output directory
  python -m src.main \\
    --repo https://github.com/user/repo \\
    --pdf report.pdf \\
    --output ./custom_audit_dir
        """
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository URL to audit"
    )

    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to PDF architectural report"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Output directory for audit report (default: audit/report_onself_generated/)"
    )

    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Only check configuration and exit"
    )

    args = parser.parse_args()

    if args.config_check:
        Config.display()
        sys.exit(0 if not Config.validate() else 1)

    # Validate inputs
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        sys.exit(1)

    # Run audit
    report_path = run_audit(
        repo_url=args.repo,
        pdf_path=str(pdf_path),
        output_dir=args.output
    )

    sys.exit(0 if report_path else 1)


if __name__ == "__main__":
    main()
