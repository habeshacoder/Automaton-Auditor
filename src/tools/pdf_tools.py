"""
PDF Tools - Document analysis with RAG-lite approach
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re


class PDFAnalyzer:
    """
    PDF document analysis with chunking and query capabilities
    Note: Uses PyPDF2 for basic extraction, can be upgraded to docling
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.text = ""
        self.chunks = []
        self.file_paths_mentioned = []

        if self.pdf_path.exists():
            self._ingest_pdf()

    def _ingest_pdf(self):
        """Extract text from PDF and create chunks"""
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(self.pdf_path)
            pages_text = []

            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_text.append({
                    "page": i + 1,
                    "text": text
                })

            # Combine all text
            self.text = " ".join([p["text"] for p in pages_text])

            # Create chunks (simple sentence-based chunking)
            sentences = re.split(r'[.!?]\s+', self.text)
            chunk_size = 5  # sentences per chunk

            for i in range(0, len(sentences), chunk_size):
                chunk_text = ". ".join(sentences[i:i+chunk_size])
                if chunk_text:
                    self.chunks.append({
                        "id": f"chunk_{i//chunk_size}",
                        "text": chunk_text
                    })

            # Extract file path mentions
            self._extract_file_paths()

        except ImportError:
            print("Warning: PyPDF2 not installed. Install with: pip install PyPDF2")
        except Exception as e:
            print(f"Error ingesting PDF: {e}")

    def _extract_file_paths(self):
        """Extract mentioned file paths from text"""
        # Pattern for file paths like src/nodes/judges.py
        path_pattern = r'\b(src/[\w/]+\.py|tests/[\w/]+\.py|[\w]+/[\w/]+\.py)\b'

        matches = re.findall(path_pattern, self.text)
        self.file_paths_mentioned = list(set(matches))  # Remove duplicates

    def query_terms(self, terms: List[str]) -> Dict[str, bool]:
        """
        Check if specific terms appear in the document

        Returns:
            Dict mapping term to boolean (found/not found)
        """
        results = {}
        text_lower = self.text.lower()

        for term in terms:
            results[term] = term.lower() in text_lower

        return results

    def query_concept(self, concept: str, context_window: int = 200) -> List[Dict]:
        """
        Find mentions of a concept with surrounding context

        Args:
            concept: The concept to search for
            context_window: Characters before and after to include

        Returns:
            List of {text, location} dicts with context
        """
        results = []
        text_lower = self.text.lower()
        concept_lower = concept.lower()

        # Find all occurrences
        start = 0
        while True:
            pos = text_lower.find(concept_lower, start)
            if pos == -1:
                break

            # Extract context
            context_start = max(0, pos - context_window)
            context_end = min(len(self.text), pos + len(concept) + context_window)

            context = self.text[context_start:context_end]

            results.append({
                "text": context,
                "location": f"Position {pos}",
                "snippet": concept
            })

            start = pos + 1

        return results

    def verify_deep_understanding(self, concept: str, min_context_length: int = 100) -> Tuple[bool, str]:
        """
        Check if concept is explained (not just mentioned)

        Returns:
            (has_deep_understanding, evidence)
        """
        occurrences = self.query_concept(concept, context_window=150)

        if not occurrences:
            return False, f"Concept '{concept}' not mentioned"

        # Check if any occurrence has substantial explanation
        for occurrence in occurrences:
            context = occurrence["text"]
            # Remove the concept itself to check surrounding text
            surrounding = context.replace(concept, "").strip()

            if len(surrounding) > min_context_length:
                # Has substantial surrounding text
                return True, f"Found detailed explanation: {context[:200]}..."

        return False, f"Concept '{concept}' mentioned but not explained in depth"

    def cross_reference_files(self, verified_files: List[str]) -> Dict:
        """
        Cross-reference file paths mentioned in PDF with actual repo files

        Args:
            verified_files: List of files that actually exist in repo

        Returns:
            {
                "verified": [...],
                "hallucinated": [...],
                "verification_rate": float
            }
        """
        verified = []
        hallucinated = []

        for mentioned_file in self.file_paths_mentioned:
            if mentioned_file in verified_files:
                verified.append(mentioned_file)
            else:
                hallucinated.append(mentioned_file)

        total = len(self.file_paths_mentioned)
        rate = len(verified) / total if total > 0 else 0.0

        return {
            "verified": verified,
            "hallucinated": hallucinated,
            "verification_rate": rate
        }

    def extract_architectural_claims(self) -> List[str]:
        """
        Extract key architectural claims from the document

        Returns:
            List of claim sentences
        """
        claims = []

        # Keywords indicating architectural claims
        claim_keywords = [
            "we implemented", "we use", "we built", "our architecture",
            "the system uses", "parallelism", "fan-out", "fan-in",
            "StateGraph", "LangGraph", "judges", "detectives"
        ]

        for chunk in self.chunks:
            text = chunk["text"].lower()
            if any(keyword in text for keyword in claim_keywords):
                claims.append(chunk["text"])

        return claims
