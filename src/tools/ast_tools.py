"""
AST Tools - Deep code structure analysis without regex
"""
import ast
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class ASTAnalyzer:
    """Parse Python code structure using AST"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def find_state_definition(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Find AgentState or similar typed state definition

        Returns:
            (found, file_path, code_snippet)
        """
        target_files = ["src/state.py", "src/graph.py", "src/nodes/state_models.py"]

        for file_rel in target_files:
            file_path = self.repo_path / file_rel
            if not file_path.exists():
                continue

            try:
                with open(file_path) as f:
                    source = f.read()
                    tree = ast.parse(source)

                # Look for TypedDict or BaseModel classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if inherits from BaseModel or TypedDict
                        for base in node.bases:
                            base_name = self._get_name(base)
                            if base_name in ["BaseModel", "TypedDict"]:
                                # Extract the class definition
                                snippet = ast.get_source_segment(source, node)
                                if snippet:
                                    return True, str(file_path), snippet[:500]

            except Exception as e:
                continue

        return False, None, None

    def analyze_graph_structure(self) -> Dict:
        """
        Analyze StateGraph construction and edge definitions

        Returns dict with:
            - has_state_graph: bool
            - parallel_branches: bool
            - fan_in_node: bool
            - nodes: List[str]
            - edges: List[Tuple[str, str]]
        """
        result = {
            "has_state_graph": False,
            "parallel_branches": False,
            "fan_in_node": False,
            "nodes": [],
            "edges": [],
            "location": None
        }

        graph_file = self.repo_path / "src" / "graph.py"
        if not graph_file.exists():
            return result

        try:
            with open(graph_file) as f:
                source = f.read()
                tree = ast.parse(source)

            result["location"] = str(graph_file)

            # Find StateGraph instantiation
            for node in ast.walk(tree):
                # Check for StateGraph() calls
                if isinstance(node, ast.Call):
                    func_name = self._get_name(node.func)
                    if func_name == "StateGraph":
                        result["has_state_graph"] = True

                # Check for add_node calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == "add_node" and node.args:
                            node_name = self._extract_string_arg(node.args[0])
                            if node_name:
                                result["nodes"].append(node_name)

                # Check for add_edge calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == "add_edge" and len(node.args) >= 2:
                            from_node = self._extract_string_arg(node.args[0])
                            to_node = self._extract_string_arg(node.args[1])
                            if from_node and to_node:
                                result["edges"].append((from_node, to_node))

            # Analyze for parallelism
            result["parallel_branches"] = self._detect_parallel_branches(result["edges"])
            result["fan_in_node"] = self._detect_fan_in(result["edges"])

        except Exception as e:
            result["error"] = str(e)

        return result

    def _detect_parallel_branches(self, edges: List[Tuple[str, str]]) -> bool:
        """Detect if multiple nodes branch from a single source"""
        from collections import defaultdict

        outgoing = defaultdict(list)
        for source, target in edges:
            outgoing[source].append(target)

        # Check if any node has multiple outgoing edges
        return any(len(targets) > 1 for targets in outgoing.values())

    def _detect_fan_in(self, edges: List[Tuple[str, str]]) -> bool:
        """Detect if multiple nodes converge to a single target"""
        from collections import defaultdict

        incoming = defaultdict(list)
        for source, target in edges:
            incoming[target].append(source)

        # Check if any node has multiple incoming edges
        return any(len(sources) > 1 for sources in incoming.values())

    def check_structured_output(self) -> Tuple[bool, List[str]]:
        """
        Check if judges use .with_structured_output() or .bind_tools()

        Returns:
            (found, locations)
        """
        locations = []
        judge_file = self.repo_path / "src" / "nodes" / "judges.py"

        if not judge_file.exists():
            return False, []

        try:
            with open(judge_file) as f:
                source = f.read()

            # Simple text search for these methods
            if "with_structured_output" in source:
                locations.append("with_structured_output found in judges.py")
            if "bind_tools" in source:
                locations.append("bind_tools found in judges.py")

            return len(locations) > 0, locations

        except Exception:
            return False, []

    def check_for_security_issues(self) -> List[Dict]:
        """
        Scan for dangerous patterns like os.system without sanitization

        Returns:
            List of security issues found
        """
        issues = []

        for py_file in self.repo_path.rglob("*.py"):
            try:
                with open(py_file) as f:
                    source = f.read()
                    tree = ast.parse(source)

                for node in ast.walk(tree):
                    # Check for os.system calls
                    if isinstance(node, ast.Call):
                        func_name = self._get_full_name(node.func)
                        if func_name in ["os.system", "subprocess.call"]:
                            issues.append({
                                "type": "Unsafe system call",
                                "location": f"{py_file.name}:line {node.lineno}",
                                "severity": "high"
                            })

            except Exception:
                continue

        return issues

    def _get_name(self, node) -> Optional[str]:
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _get_full_name(self, node) -> Optional[str]:
        """Get full dotted name like os.system"""
        if isinstance(node, ast.Attribute):
            value_name = self._get_full_name(node.value)
            if value_name:
                return f"{value_name}.{node.attr}"
            return node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return None

    def _extract_string_arg(self, node) -> Optional[str]:
        """Extract string value from AST node"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None
