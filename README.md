# 🏛️ Automaton Auditor

**Production-Grade Multi-Agent Code Quality Assessment System**

A sophisticated LangGraph-based agent swarm implementing a Digital Courtroom architecture for autonomous code evaluation.

## 🎯 Overview

The Automaton Auditor is a hierarchical multi-agent system designed to audit code repositories with the rigor of a judicial process. It implements:

- **Detective Layer**: Forensic evidence collection from repositories and documentation
- **Judicial Layer**: Dialectical evaluation through three persona lenses (Prosecutor, Defense, Tech Lead)
- **Synthesis Layer**: Deterministic conflict resolution and structured reporting

## 🏗️ Architecture

```

START
↓
ContextBuilder (loads rubric)
↓
┌─────────────────────┐
│ RepoInvestigator │ (parallel)
│ DocAnalyst │ (parallel)
└─────────────────────┘
↓
EvidenceAggregator (fan-in)
↓
┌─────────────────────┐
│ Prosecutor │ (parallel)
│ Defense │ (parallel)
│ TechLead │ (parallel)
└─────────────────────┘
↓
ChiefJustice (synthesis)
↓
END

```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- Git installed on system

### Installation

Using `uv` (recommended):

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (development)
uv pip install -e .
```

### Reproducible setup (with uv.lock)

For fully deterministic installs, use the committed `uv.lock`:

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Sync exactly the locked dependencies
uv sync --locked
```

### Using pip (alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:

```bash
OPENAI_API_KEY=your-key-here
LANGCHAIN_API_KEY=your-langsmith-key-here  # Optional but recommended
```

3. Verify configuration:

```bash
python -m src.main --config-check
```

## 📖 Usage

### Basic Audit

```bash
python -m src.main \
  --repo https://github.com/username/repository \
  --pdf path/to/architectural_report.pdf
```

### Custom Output Directory

```bash
python -m src.main \
  --repo https://github.com/username/repository \
  --pdf report.pdf \
  --output ./custom_output_dir
```

### Programmatic Usage

```python
from src.main import run_audit

report_path = run_audit(
    repo_url="https://github.com/username/repository",
    pdf_path="report.pdf",
    output_dir="./audit_output"
)

print(f"Report saved to: {report_path}")
```

## 📊 Output Structure

```
audit/
├── report_bypeer_received/     # Audits you received from peers
├── report_onpeer_generated/    # Audits you ran on peers
├── report_onself_generated/    # Self-audits
└── langsmith_logs/             # LangSmith trace exports
```

## 🔬 Components

### Detective Layer

**RepoInvestigator** (`src/tools/git_tools.py`, `src/tools/ast_tools.py`)

- Git forensic analysis (commit history, patterns)
- AST-based code structure analysis
- Security vulnerability scanning
- State management verification

**DocAnalyst** (`src/tools/pdf_tools.py`)

- PDF document parsing and chunking
- Concept verification (not just keyword matching)
- Cross-referencing with repository evidence
- Hallucination detection

### Judicial Layer

**Three Judge Personas** (`src/nodes/judges.py`)

1. **Prosecutor** – Critical lens, assumes vibe coding
2. **Defense** – Optimistic lens, rewards effort and intent
3. **Tech Lead** – Pragmatic lens, evaluates maintainability

All judges use `.with_structured_output()` to enforce Pydantic schema compliance.

### Synthesis Layer

**Chief Justice** (`src/nodes/justice.py`)

- Applies deterministic conflict resolution rules
- Security override (security flaws cap scores)
- Fact supremacy (evidence > opinion)
- Generates structured markdown reports

## 🎓 Key Features

### 1. Typed State Management

```python
class AgentState(TypedDict):
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior]
    opinions: Annotated[List[JudicialOpinion], operator.add]
```

Uses `operator.ior` and `operator.add` for safe parallel updates.

### 2. Parallel Execution

- Detectives run in parallel (fan-out)
- Evidence aggregation (fan-in)
- Judges evaluate independently in parallel
- Final synthesis in Chief Justice

### 3. Structured Output Enforcement

All judges return Pydantic-validated `JudicialOpinion` objects, preventing hallucination.

### 4. Sandboxed Tool Execution

Git operations isolated in temporary directories with comprehensive error handling.

### 5. Observable Execution

Full LangSmith tracing integration for debugging multi-agent flows.

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## 📋 Rubric

The system evaluates against four dimensions:

1. **Forensic Accuracy (Code)** – Repository structure and implementation
2. **Forensic Accuracy (Docs)** – Documentation quality and accuracy
3. **Judicial Nuance** – Persona separation and dialectical reasoning
4. **LangGraph Architecture** – Proper orchestration and parallelism

See `rubric/week2_rubric.json` for complete specifications.

## 🐳 Docker Deployment

```bash
# Build image
docker build -t automaton-auditor .

# Run audit
docker run -v $(pwd)/audit:/app/audit \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  automaton-auditor \
  --repo https://github.com/user/repo \
  --pdf /app/report.pdf
```

## 🔍 Debugging

### Enable Verbose Logging

```bash
export LOG_LEVEL=DEBUG
python -m src.main --repo ... --pdf ...
```

### View LangSmith Traces

1. Ensure `LANGCHAIN_TRACING_V2=true` in `.env`
2. Run audit
3. Visit https://smith.langchain.com/
4. Navigate to your project to view traces

## 📚 Project Structure

```
automaton_auditor/
├── src/
│   ├── nodes/
│   │   ├── state_models.py    # Pydantic state schemas
│   │   ├── detectives.py      # Evidence collection agents
│   │   ├── judges.py          # Judicial evaluation agents
│   │   └── justice.py         # Chief Justice synthesis
│   ├── tools/
│   │   ├── git_tools.py       # Safe git operations
│   │   ├── ast_tools.py       # Code structure analysis
│   │   └── pdf_tools.py       # Document analysis
│   ├── graph.py               # LangGraph orchestration
│   ├── config.py              # Configuration management
│   └── main.py                # CLI entry point
├── rubric/
│   └── week2_rubric.json      # Evaluation constitution
├── audit/                     # Generated reports
├── tests/                     # Test suite
├── pyproject.toml
├── uv.lock                    # Locked dependencies for deterministic installs
└── README.md
```

## 🤝 Contributing

This is a challenge implementation. For production use cases:

1. Extend detective capabilities (add VisionInspector)
2. Implement retry logic for LLM calls
3. Add caching for expensive operations
4. Enhance error handling and recovery
5. Add more sophisticated cross-validation

## 📄 License

MIT License – See LICENSE file for details.

## 🏆 Acknowledgments

Built for the FDE Week 2 Challenge: The Automaton Auditor.

Implements concepts from:

- LangGraph documentation
- Multi-Agent Systems research
- Constitutional AI principles
- LLM-as-Judge methodologies

---

**Note**: This system is designed for educational and assessment purposes. For production deployments, additional hardening and testing are recommended.

```

```
