"""
Diff Sieve Utility for CodeSlim.

Applies trim-1 verbatim context compression principles to unified diffs,
extracting surgical hunk headers, modified lines, and surrounding control flow
while omitting large unchanged spans with clean '[... N lines omitted ...]' markers.
"""

from __future__ import annotations

import re
import shutil
import subprocess


def sieve_diff(
    diff: str,
    *,
    max_chars: int = 2500,
    max_lines: int = 60,
    context_lines: int = 2,
) -> str:
    """
    Sieve a unified diff using trim-1 verbatim line retention invariants.

    Preserves:
    - Diff headers (diff --git, ---, +++)
    - Hunk boundaries (@@ -L,S +L,S @@)
    - Added and removed lines (+ and -)
    - Key structural control flow (def, class, return)
    - Surrounding context lines up to `context_lines`

    Omitted unchanged lines are consolidated into '[... N lines omitted ...]'.

    Args:
        diff: The raw unified diff string.
        max_chars: Target character budget before aggressive sieving.
        max_lines: Target maximum lines to retain.
        context_lines: Number of unchanged lines to retain around modified hunks.

    Returns:
        A pristine, verbatim unified diff string safe for GitHub PR comments.
    """
    if not diff or not diff.strip():
        return ""

    lines = diff.splitlines()
    if len(lines) <= max_lines and len(diff) <= max_chars:
        return diff

    # 1. Try external trim binary if present on system PATH
    trim_bin = shutil.which("trim")
    if trim_bin:
        try:
            proc = subprocess.run(
                [trim_bin, "--query", "@@ |+ |- |def |class |return |raise", "--point", "balanced"],
                input=diff,
                text=True,
                capture_output=True,
                timeout=2,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.strip()
        except Exception:
            pass

    # 2. Native Trim-1 Verbatim Diff Sieve Algorithm (Zero External Dependency)
    hunk_header_re = re.compile(r"^@@\s+-\d+,\d+\s+\+\d+,\d+\s+@@")
    diff_header_re = re.compile(r"^(diff\s+--git|---\s+|\+\+\+\s+|index\s+)")
    symbol_re = re.compile(r"^\s*(def |class |async def |return |raise |import |from )")

    # Score each line for relevance
    keep_indices: set[int] = set()

    for idx, line in enumerate(lines):
        # Always keep diff headers and hunk coordinates
        if diff_header_re.match(line) or hunk_header_re.match(line):
            keep_indices.add(idx)
            continue

        # Keep modifications (+ and -)
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            keep_indices.add(idx)
            # Expand context window around modifications
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + context_lines + 1)
            for c in range(start, end):
                keep_indices.add(c)
            continue

        # Keep enclosing function/class definitions
        clean_line = line[1:].strip() if line.startswith(("+", "-")) else line.strip()
        if symbol_re.match(clean_line):
            keep_indices.add(idx)

    # Reconstruct the sieved diff with verbatim omission markers
    output_lines: list[str] = []
    omitted_count = 0

    for idx in range(len(lines)):
        if idx in keep_indices:
            if omitted_count > 0:
                output_lines.append(f" [... {omitted_count} unchanged lines omitted ...]")
                omitted_count = 0
            output_lines.append(lines[idx])
        else:
            omitted_count += 1

    if omitted_count > 0:
        output_lines.append(f" [... {omitted_count} unchanged lines omitted ...]")

    result = "\n".join(output_lines)

    # Hard safety ceiling: if still oversized, cleanly truncate at last hunk boundary
    if len(result) > max_chars * 2:
        capped_lines = result.splitlines()[:max_lines]
        result = "\n".join(capped_lines) + f"\n\n[... {len(result.splitlines()) - max_lines} diff lines omitted for comment length ...]"

    return result
