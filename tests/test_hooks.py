"""
Unit tests for codeslim.hooks — Git pre-commit hook installer.
"""

from pathlib import Path

from codeslim.hooks import generate_pre_commit_script, install_git_pre_commit_hook


def test_generate_pre_commit_script():
    script = generate_pre_commit_script()
    assert "#!/bin/sh" in script
    assert "codeslim.cli optimize" in script
    assert "git add" in script


def test_install_git_pre_commit_hook_no_git_dir(tmp_path: Path):
    # tmp_path is not a git repo
    success = install_git_pre_commit_hook(tmp_path)
    assert success is False
    assert not (tmp_path / ".git" / "hooks" / "pre-commit").exists()


def test_install_git_pre_commit_hook_success(tmp_path: Path):
    # Create fake .git directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    success = install_git_pre_commit_hook(tmp_path)
    assert success is True

    hook_file = git_dir / "hooks" / "pre-commit"
    assert hook_file.is_file()
    content = hook_file.read_text(encoding="utf-8")
    assert "#!/bin/sh" in content
    assert "codeslim.cli optimize" in content
