"""
Git Tools - Safe repository operations with sandboxing
"""
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime


class GitTool:
    """Sandboxed git operations with error handling"""

    def __init__(self):
        self.temp_dir: Optional[Path] = None

    def clone_repo(self, repo_url: str) -> Tuple[bool, str, Optional[Path]]:
        """
        Safely clone a repository into a temporary directory

        Returns:
            (success, message, repo_path)
        """
        try:
            # Create sandboxed temporary directory
            self.temp_dir = Path(tempfile.mkdtemp(prefix="audit_repo_"))

            # Execute git clone with timeout and capture output
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(self.temp_dir)],
                capture_output=True,
                text=True,
                timeout=60,  # 1 minute timeout
                check=True
            )

            return True, f"Successfully cloned to {self.temp_dir}", self.temp_dir

        except subprocess.TimeoutExpired:
            self.cleanup()
            return False, "Git clone timed out after 60 seconds", None

        except subprocess.CalledProcessError as e:
            self.cleanup()
            return False, f"Git clone failed: {e.stderr}", None

        except Exception as e:
            self.cleanup()
            return False, f"Unexpected error during clone: {str(e)}", None

    def extract_git_history(self, repo_path: Path) -> Tuple[bool, List[dict]]:
        """
        Extract detailed commit history with timestamps

        Returns:
            (success, commits) where commits is list of {hash, message, timestamp, author}
        """
        try:
            # Get commits with detailed format
            result = subprocess.run(
                [
                    "git", "log", 
                    "--all",
                    "--format=%H|%s|%ai|%an",
                    "--reverse"
                ],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0][:8],  # Short hash
                            "message": parts[1],
                            "timestamp": parts[2],
                            "author": parts[3]
                        })

            return True, commits

        except Exception as e:
            return False, [{"error": str(e)}]

    def count_commits(self, repo_path: Path) -> int:
        """Count total commits in repository"""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--all", "--count"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            return int(result.stdout.strip())
        except:
            return 0

    def classify_commit_pattern(self, commits: List[dict]) -> str:
        """
        Classify commit history as atomic vs monolithic

        Returns:
            "atomic", "monolithic", or "mixed"
        """
        if len(commits) <= 1:
            return "monolithic"

        # Check for progression keywords
        progression_keywords = [
            "setup", "init", "environment", "tool", "engineering",
            "detective", "judge", "orchestration", "graph", "test"
        ]

        matched_stages = 0
        for commit in commits:
            msg = commit["message"].lower()
            if any(keyword in msg for keyword in progression_keywords):
                matched_stages += 1

        # If >40% of commits show progression, consider atomic
        if matched_stages / len(commits) > 0.4:
            return "atomic"
        elif len(commits) > 5:
            return "mixed"
        else:
            return "monolithic"

    def cleanup(self):
        """Remove temporary directory"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Warning: Could not clean up {self.temp_dir}: {e}")

    def __del__(self):
        """Ensure cleanup on deletion"""
        self.cleanup()
