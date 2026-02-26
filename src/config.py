"""
Configuration management for Automaton Auditor
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration container"""

    # OpenRouter API
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv(
        "OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"  # default; can be any OpenRouter model id
    )

    # LangSmith Tracing
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "automaton-auditor")

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    RUBRIC_PATH = PROJECT_ROOT / "rubric" / "week2_rubric.json"
    AUDIT_OUTPUT_DIR = PROJECT_ROOT / "audit"

    # Execution Settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))

    @classmethod
    def validate(cls) -> list:
        """Validate configuration and return list of issues"""
        issues = []

        if not cls.OPENROUTER_API_KEY:
            issues.append("OPENROUTER_API_KEY not set")

        if cls.LANGCHAIN_TRACING_V2 == "true" and not cls.LANGCHAIN_API_KEY:
            issues.append("LANGCHAIN_API_KEY not set but tracing is enabled")

        if not cls.RUBRIC_PATH.exists():
            issues.append(f"Rubric file not found at {cls.RUBRIC_PATH}")

        return issues

    @classmethod
    def display(cls):
        """Display current configuration (safe mode - no secrets)"""
        print("=" * 60)
        print("Automaton Auditor Configuration")
        print("=" * 60)
        print(f"OpenRouter Model: {cls.OPENROUTER_MODEL}")
        print(f"LangSmith Tracing: {cls.LANGCHAIN_TRACING_V2}")
        print(f"LangSmith Project: {cls.LANGCHAIN_PROJECT}")
        print(f"Rubric Path: {cls.RUBRIC_PATH}")
        print(f"Audit Output: {cls.AUDIT_OUTPUT_DIR}")
        print(f"Max Retries: {cls.MAX_RETRIES}")
        print(f"Timeout: {cls.TIMEOUT_SECONDS}s")

        issues = cls.validate()
        if issues:
            print("\n⚠️  Configuration Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ Configuration valid")

        print("=" * 60)
