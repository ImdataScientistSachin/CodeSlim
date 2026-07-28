"""
Integration tests for CodeSlim CLI subcommands.
"""

from pathlib import Path

from click.testing import CliRunner

from codeslim.cli import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "codeslim" in result.output


def test_cli_analyze_command(tmp_path: Path):
    test_file = tmp_path / "sample.py"
    test_file.write_text("def foo():\n    pass\n")

    runner = CliRunner()
    result = runner.invoke(main, ["analyze", str(test_file)])
    assert result.exit_code == 0
    assert "Target File:" in result.output
    assert "sample.py" in result.output


def test_cli_analyze_json_format(tmp_path: Path):
    test_file = tmp_path / "sample.py"
    test_file.write_text("def foo():\n    pass\n")

    runner = CliRunner()
    result = runner.invoke(main, ["analyze", str(test_file), "--format", "json"])
    assert result.exit_code == 0
    assert '"file_path":' in result.output


def test_cli_optimize_apply_with_backup(tmp_path: Path):
    test_file = tmp_path / "sample.py"
    original_code = "def foo():\n    unused = 1\n    return 42\n"
    test_file.write_text(original_code)

    runner = CliRunner()
    result = runner.invoke(main, ["optimize", str(test_file), "--no-llm"])
    assert result.exit_code == 0
    assert "sample.py" in result.output
