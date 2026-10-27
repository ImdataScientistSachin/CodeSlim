"""Unit tests for codeslim.utils.file_utils."""

import tempfile
from pathlib import Path

from codeslim.utils.file_utils import (
    collect_target_files,
    is_ignored,
    load_ignore_patterns,
    validate_file_path,
)


def test_validate_file_path() -> None:
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(b"print('hello')\n")
        temp_path = Path(f.name)

    try:
        resolved = validate_file_path(temp_path)
        assert resolved.exists()
        assert resolved.is_file()
    finally:
        temp_path.unlink()


def test_load_ignore_patterns_and_is_ignored() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        ignore_file = root / ".codeslimignore"
        ignore_file.write_text("**/custom_ignore/**\n*.tmp.py\n", encoding="utf-8")

        patterns = load_ignore_patterns(root)
        assert "**/custom_ignore/**" in patterns
        assert "*.tmp.py" in patterns

        sub_py = root / "script.py"
        sub_py.write_text("x = 1\n", encoding="utf-8")

        ignored_py = root / "custom_ignore" / "bad.py"
        ignored_py.parent.mkdir()
        ignored_py.write_text("y = 2\n", encoding="utf-8")

        assert is_ignored(ignored_py, root, patterns) is True
        assert is_ignored(sub_py, root, patterns) is False

        discovered = collect_target_files(root)
        discovered_names = [p.name for p in discovered]
        assert "script.py" in discovered_names
        assert "bad.py" not in discovered_names
