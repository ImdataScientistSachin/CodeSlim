"""Pure Python Standard Library Docstring Compressor for CodeSlim Node 2.

Implements ShortenDoc-style docstring token importance scoring and pruning
using zero heavy external dependencies (pure stdlib: ast, re, collections, math).
"""

import ast
import math
import re
from collections import Counter

STOPWORDS: set[str] = {
    "a",
    "an",
    "the",
    "this",
    "that",
    "these",
    "those",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "of",
    "in",
    "to",
    "for",
    "with",
    "on",
    "at",
    "from",
    "by",
    "about",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "and",
    "or",
    "but",
    "if",
    "then",
    "else",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "can",
    "will",
    "just",
    "should",
    "now",
    "please",
    "note",
}


class DocstringCompressor:
    """Pure stdlib ShortenDoc docstring compressor for context minimization."""

    def __init__(self, target_compression: float = 0.3) -> None:
        """Initialize the docstring compressor.

        Args:
            target_compression: Fraction of low-importance tokens to prune (e.g. 0.3 = 30%).
        """
        self.target_compression = max(0.0, min(0.6, target_compression))

    def compress_docstring(self, docstring: str) -> str:
        """Compress a docstring by pruning low-importance filler tokens.

        Args:
            docstring: The raw docstring text.

        Returns:
            The pruned, concise docstring.
        """
        if not docstring or len(docstring.strip()) < 20:
            return docstring

        lines = docstring.splitlines()
        first_line = lines[0] if lines else ""

        # Extract remaining lines (body)
        body_text = "\n".join(lines[1:]) if len(lines) > 1 else ""
        if not body_text.strip():
            return docstring

        words = re.findall(r"\b\w+\b|\S", body_text)
        if not words:
            return docstring

        # Compute term frequency importance scores
        word_counts = Counter(w.lower() for w in words if w.isalnum())
        total_words = sum(word_counts.values()) or 1

        scores: list[tuple[str, float]] = []
        for w in words:
            clean = w.lower()
            if clean in STOPWORDS:
                score = 0.1
            elif clean.isalnum():
                tf = word_counts[clean] / total_words
                # Length boost for technical term identifiers
                score = tf * (1.0 + math.log(len(clean) + 1))
            else:
                score = 0.8  # Preserve punctuation and formatting symbols
            scores.append((w, score))

        # Filter out lowest-scoring tokens based on target_compression ratio
        num_to_prune = int(len(words) * self.target_compression)
        if num_to_prune <= 0:
            return docstring

        # Sort indices by score ascending to identify tokens to prune
        indexed_scores = list(enumerate(scores))
        # Exclude punctuation from pruning
        prunable_indexed = [item for item in indexed_scores if item[1][0].isalnum() and item[1][1] <= 0.2]
        prunable_indexed.sort(key=lambda x: x[1][1])

        prune_indices = set(item[0] for item in prunable_indexed[:num_to_prune])

        compressed_body_words = [w for idx, (w, _) in enumerate(scores) if idx not in prune_indices]
        compressed_body = " ".join(compressed_body_words)
        compressed_body = re.sub(r"\s+([,.:;?!\)])", r"\1", compressed_body)

        return f"{first_line}\n{compressed_body}".strip()

    def compress_code_docstrings(self, source_code: str) -> str:
        """Parse Python source code and compress all module/class/function docstrings.

        Args:
            source_code: Python source string.

        Returns:
            Source code with compressed docstrings.
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return source_code

        docstring_nodes: list[tuple[int, int, str]] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node, clean=False)
                if doc and len(node.body) > 0 and isinstance(node.body[0], ast.Expr):
                    expr_node = node.body[0]
                    if isinstance(expr_node.value, ast.Constant) and isinstance(expr_node.value.value, str):
                        start_line = expr_node.lineno
                        end_line = getattr(expr_node, "end_lineno", start_line)
                        docstring_nodes.append((start_line, end_line, doc))

        if not docstring_nodes:
            return source_code

        lines = source_code.splitlines()
        docstring_nodes.sort(key=lambda x: x[0], reverse=True)

        for start_line, end_line, orig_doc in docstring_nodes:
            compressed_doc = self.compress_docstring(orig_doc)
            indent = " " * (len(lines[start_line - 1]) - len(lines[start_line - 1].lstrip()))
            new_doc_lines = [f'{indent}"""{compressed_doc}"""']
            lines[start_line - 1 : end_line] = new_doc_lines

        return "\n".join(lines)
