"""
JSON Report Formatter for CodeSlim.

Renders CodeSlimReport objects into structured, pretty-printed JSON.
"""

from codeslim.models.report import CodeSlimReport


def format_json_report(report: CodeSlimReport, indent: int = 2) -> str:
    """
    Format CodeSlimReport as pretty-printed JSON.

    Args:
        report: CodeSlimReport model instance.
        indent: Indentation level for formatting.

    Returns:
        JSON string.
    """
    return report.model_dump_json(indent=indent)
