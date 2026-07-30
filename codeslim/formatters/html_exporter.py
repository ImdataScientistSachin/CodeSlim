"""
Interactive HTML Observatory Exporter for CodeSlim.

Generates a standalone, self-contained HTML/CSS/JS Project Observatory dashboard
complete with Tokyo Night theme styling, SVG health gauge, dynamic search/filters,
interactive treemaps, cross-file anomaly panels, codebase fingerprinting,
and an Interactive File Surgery & Diff Inspector Modal.
"""

import html
import json
from pathlib import Path

from codeslim.models.project_report import ProjectReport
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.formatters.html_exporter")

TEMPLATE_PATH = Path(__file__).parent / "templates" / "observatory.html"


def generate_html_observatory_report(project_report: ProjectReport) -> str:
    """
    Generate interactive HTML source string for ProjectReport.

    Args:
        project_report: Aggregated ProjectReport dataset.

    Returns:
        Self-contained HTML string.
    """
    if not TEMPLATE_PATH.exists():
        log.error("template_not_found", path=str(TEMPLATE_PATH))
        raise FileNotFoundError(f"Observatory template not found: {TEMPLATE_PATH}")

    template_str = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Summary stats
    grade = project_report.overall_grade
    score = round(project_report.overall_bloat_score, 1)
    total_files = project_report.total_files
    clean_files = sum(1 for f in project_report.file_reports if f.bloat_grade in ("A", "B"))
    moderate_files = sum(1 for f in project_report.file_reports if f.bloat_grade == "C")
    severe_files = sum(1 for f in project_report.file_reports if f.bloat_grade in ("D", "F"))

    gauge_color = {
        "A": "#00e676",
        "B": "#00e5ff",
        "C": "#ffd600",
        "D": "#e040fb",
        "F": "#ff1744",
    }.get(grade, "#ffffff")

    sorted_file_reports = sorted(project_report.file_reports, key=lambda f: f.bloat_score, reverse=True)

    file_data_map = {}
    file_rows = []
    treemap_items = []

    for item in sorted_file_reports:
        key = item.file_path
        max_cc = item.metrics.max_cc if item.metrics else 0
        dead_count = len(item.metrics.dead_code) if item.metrics else 0
        opt_lines = item.optimized_lines or item.original_lines
        lines_saved = max(0, item.original_lines - opt_lines)

        bloat_map_list = [
            {
                "severity": entry.severity,
                "bloat_type": entry.bloat_type,
                "line_start": entry.line_start,
                "line_end": entry.line_end,
                "explanation": entry.explanation,
                "suggestion": entry.suggestion,
            }
            for entry in item.bloat_map
        ]

        file_data_map[key] = {
            "file_path": item.file_path,
            "file_name": item.file_name,
            "bloat_score": round(item.bloat_score, 1),
            "bloat_grade": item.bloat_grade,
            "original_lines": item.original_lines,
            "optimized_lines": opt_lines,
            "lines_saved": lines_saved,
            "max_cc": max_cc,
            "dead_count": dead_count,
            "diff": item.diff or "",
            "bloat_map": bloat_map_list,
        }

        status_color = (
            "#ff1744"
            if item.bloat_grade == "F"
            else ("#e040fb" if item.bloat_grade == "D" else ("#ffd600" if item.bloat_grade == "C" else "#00e676"))
        )
        bar_width = min(100, max(5, int(item.bloat_score)))
        escaped_key = item.file_path.replace("\\", "\\\\").replace("'", "\\'")
        safe_display_path = html.escape(item.file_path)

        file_rows.append(
            f"""
            <tr class="file-row" data-grade="{item.bloat_grade}" data-file="{item.file_path.lower()}" onclick="openSurgeryModal('{escaped_key}')">
                <td style="font-weight:600; color:#c0caf5;">{safe_display_path}</td>
                <td style="color:{status_color}; font-weight:700;">Grade {item.bloat_grade} ({item.bloat_score:.1f})</td>
                <td>{item.original_lines}</td>
                <td><span class="badge" style="background:{status_color}22; color:{status_color}; border:1px solid {status_color};">{max_cc}</span></td>
                <td>{dead_count}</td>
                <td style="width:160px;">
                    <div style="background:#24283b; height:10px; border-radius:5px; overflow:hidden;">
                        <div style="background:{status_color}; width:{bar_width}%; height:100%;"></div>
                    </div>
                </td>
            </tr>
            """
        )

        size_flex = max(1, item.original_lines)
        file_name_clean = html.escape(Path(item.file_path).name)
        treemap_items.append(
            f"""
            <div class="tree-box" style="flex-grow: {size_flex}; background: {status_color}1a; border: 1px solid {status_color};"
                 title="Click to inspect: {safe_display_path} (Grade {item.bloat_grade})"
                 onclick="openSurgeryModal('{escaped_key}')">
                <div class="tree-name" style="color: {status_color};">{file_name_clean}</div>
                <div class="tree-meta">{item.original_lines} L | CC {max_cc}</div>
            </div>
            """
        )

    # Anomaly Panels
    cross_file_anomalies = []
    if project_report.phantom_functions:
        pf_rows = "".join(
            f'<li style="margin-bottom:6px;"><code>{html.escape(pf.function_name)}()</code> in <span style="color:var(--cyan);">{html.escape(pf.file_path)}:L{pf.line_number}</span></li>'
            for pf in project_report.phantom_functions
        )
        cross_file_anomalies.append(
            f"""
            <div class="card" style="border-color: #ffd600;">
                <div style="color: var(--yellow); font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">
                    👻 Phantom Functions ({len(project_report.phantom_functions)})
                </div>
                <ul style="font-size: 13px; list-style: none; color: var(--text-main);">
                    {pf_rows}
                </ul>
            </div>
            """
        )

    if project_report.hallucination_spread:
        hs_rows = "".join(
            f'<li style="margin-bottom:6px;"><code style="color:var(--magenta);">{html.escape(pkg)}</code> imported in <strong>{len(files)}</strong> files ({", ".join(html.escape(f) for f in files[:3])})</li>'
            for pkg, files in project_report.hallucination_spread.items()
        )
        cross_file_anomalies.append(
            f"""
            <div class="card" style="border-color: #e040fb;">
                <div style="color: var(--magenta); font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">
                    ☣️ Hallucination Spread Index ({len(project_report.hallucination_spread)})
                </div>
                <ul style="font-size: 13px; list-style: none; color: var(--text-main);">
                    {hs_rows}
                </ul>
            </div>
            """
        )

    cross_file_anomalies_html = (
        f"<div class='grid-stats' style='margin-bottom:30px;'>{''.join(cross_file_anomalies)}</div>"
        if cross_file_anomalies
        else ""
    )

    # Fingerprint Stats
    fp = project_report.fingerprint
    fp_dead_pct = round((fp.dead_lines / fp.total_lines * 100), 1) if fp.total_lines > 0 else 0.0
    fp_complex_pct = round((fp.complex_lines / fp.total_lines * 100), 1) if fp.total_lines > 0 else 0.0
    fp_dup_pct = round((fp.duplicate_lines / fp.total_lines * 100), 1) if fp.total_lines > 0 else 0.0
    hallucination_spread_pct = (
        len(project_report.hallucination_spread) / total_files * 100.0 if total_files > 0 else 0.0
    )

    replacements = {
        "var(--gauge-color, #ffffff)": gauge_color,
        "var(--fp-clean-pct, 0%)": f"{fp.clean_pct}%",
        "var(--fp-dead-pct, 0%)": f"{fp_dead_pct}%",
        "var(--fp-complex-pct, 0%)": f"{fp_complex_pct}%",
        "var(--fp-dup-pct, 0%)": f"{fp_dup_pct}%",
        "project_path": project_report.project_path,
        "grade": grade,
        "score": str(score),
        "gauge_color": gauge_color,
        "gauge_dash_offset": str(251.2 * (1 - score / 100.0)),
        "total_files": str(total_files),
        "clean_files": str(clean_files),
        "moderate_files": str(moderate_files),
        "severe_files": str(severe_files),
        "phantom_count": str(len(project_report.phantom_functions)),
        "hallucination_spread_pct": f"{hallucination_spread_pct:.1f}",
        "fp_total_lines": f"{fp.total_lines:,}",
        "fp_clean_lines": f"{fp.clean_lines:,}",
        "fp_clean_pct": str(fp.clean_pct),
        "fp_dead_lines": f"{fp.dead_lines:,}",
        "fp_dead_pct": str(fp_dead_pct),
        "fp_complex_lines": f"{fp.complex_lines:,}",
        "fp_complex_pct": str(fp_complex_pct),
        "fp_duplicate_lines": f"{fp.duplicate_lines:,}",
        "fp_dup_pct": str(fp_dup_pct),
        "cross_file_anomalies_html": cross_file_anomalies_html,
        "treemap_html": "".join(treemap_items),
        "total_scanned_files": str(len(sorted_file_reports)),
        "file_rows_html": "".join(file_rows),
        "js_file_data_map": json.dumps(file_data_map).replace("<", "\\u003c"),
    }

    result_html = template_str
    for k, v in replacements.items():
        result_html = result_html.replace("{" + k + "}", v)

    return result_html


def export_html_report(project_report: ProjectReport, output_path: Path) -> Path:
    """
    Generate and write self-contained HTML observatory report to file.

    Args:
        project_report: Aggregated ProjectReport.
        output_path: Target .html file path.

    Returns:
        Written output Path.
    """
    html_content = generate_html_observatory_report(project_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")
    log.info("html_report_exported", path=str(output_path), bytes=len(html_content))
    return output_path
