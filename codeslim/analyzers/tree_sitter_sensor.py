"""Tree-Sitter C-Native Sensor for CodeSlim Node 1 static analysis.

Provides high-speed AST/CST parsing and zero-loss code skeletonization.
"""

from typing import Any

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor, QueryError


class TreeSitterSensor:
    """C-native Tree-Sitter parser for Python source code skeletonization."""

    def __init__(self) -> None:
        """Initialize the Tree-Sitter parser with Python grammar."""
        self._language = Language(tspython.language())
        self._parser = Parser(self._language)

    @property
    def language(self) -> Language:
        """Return the underlying Tree-Sitter Language instance."""
        return self._language

    def parse_bytes(self, source_bytes: bytes) -> Any:
        """Parse source code bytes into a Tree-Sitter SyntaxTree."""
        return self._parser.parse(source_bytes)

    def extract_skeleton(self, source_code: str) -> str:
        """Extract a structural code skeleton by preserving signatures and stripping method bodies.

        Args:
            source_code: The Python source code string.

        Returns:
            The pruned code skeleton string with signatures intact and method bodies replaced with '...'.
        """
        if not source_code.strip():
            return source_code

        source_bytes = source_code.encode("utf-8")
        tree = self.parse_bytes(source_bytes)
        root_node = tree.root_node

        try:
            query = Query(
                self._language,
                """
                (function_definition
                    name: (identifier)
                    body: (block) @func.body)
                """,
            )
            cursor = QueryCursor(query)
            captures = cursor.captures(root_node)
        except QueryError:
            # Fallback to original code if query fails
            return source_code

        body_spans: list[tuple[int, int]] = []
        if isinstance(captures, list):
            for node, capture_name in captures:
                if capture_name == "func.body":
                    body_spans.append((node.start_byte, node.end_byte))
        elif isinstance(captures, dict):
            for capture_name, nodes in captures.items():
                if capture_name == "func.body":
                    for n in nodes:
                        body_spans.append((n.start_byte, n.end_byte))

        if not body_spans:
            return source_code

        # Sort spans by start_byte ascending
        body_spans.sort(key=lambda s: s[0])

        # Reconstruct source code by replacing body spans with ':\n    ...'
        result_chunks: list[str] = []
        current_idx = 0

        for start_byte, end_byte in body_spans:
            if start_byte > current_idx:
                result_chunks.append(source_bytes[current_idx:start_byte].decode("utf-8", errors="replace"))

            # Calculate indentation level from preceding line if possible
            result_chunks.append(":\n    ...")
            current_idx = end_byte

        if current_idx < len(source_bytes):
            result_chunks.append(source_bytes[current_idx:].decode("utf-8", errors="replace"))

        return "".join(result_chunks)
