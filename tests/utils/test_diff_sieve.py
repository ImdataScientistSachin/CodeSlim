"""
Unit tests for codeslim.utils.diff_sieve — Trim-1 Diff Sieve Utility.
"""

from codeslim.utils.diff_sieve import sieve_diff


def test_sieve_diff_empty():
    assert sieve_diff("") == ""
    assert sieve_diff("   \n  ") == ""


def test_sieve_diff_small_unchanged():
    diff = (
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,3 +1,3 @@\n"
        " def hello():\n"
        "-    print('old')\n"
        "+    print('new')\n"
    )
    result = sieve_diff(diff, max_chars=2000, max_lines=50)
    assert result == diff


def test_sieve_diff_omits_large_unchanged_spans():
    lines = [
        "--- a/service.py",
        "+++ b/service.py",
        "@@ -1,150 +1,150 @@",
        "def main():",
    ]
    # Add 40 unchanged lines
    for i in range(40):
        lines.append(f"    val_{i} = {i}")

    # Add modification
    lines.append("-    return False")
    lines.append("+    return True")

    # Add another 40 unchanged lines
    for i in range(40, 80):
        lines.append(f"    more_{i} = {i}")

    diff = "\n".join(lines)
    result = sieve_diff(diff, max_chars=500, max_lines=20)

    # Must preserve headers and hunk
    assert "--- a/service.py" in result
    assert "+++ b/service.py" in result
    assert "@@ -1,150 +1,150 @@" in result
    # Must preserve changes
    assert "-    return False" in result
    assert "+    return True" in result
    # Must contain omission markers
    assert "unchanged lines omitted" in result
