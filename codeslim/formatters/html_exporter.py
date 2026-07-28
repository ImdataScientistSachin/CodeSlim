"""
Interactive HTML Observatory Exporter for CodeSlim.

Generates a standalone, self-contained HTML/CSS/JS Project Observatory dashboard
complete with Tokyo Night theme styling, SVG health gauge, dynamic search/filters,
interactive treemaps, cross-file anomaly panels, codebase fingerprinting,
and an Interactive File Surgery & Diff Inspector Modal.
"""

import json
from pathlib import Path

from codeslim.models.project_report import ProjectReport
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.formatters.html_exporter")


def generate_html_observatory_report(project_report: ProjectReport) -> str:
    """
    Generate interactive HTML source string for ProjectReport.

    Args:
        project_report: Aggregated ProjectReport dataset.

    Returns:
        Self-contained HTML string.
    """
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

    # Sort files by bloat_score descending so table shows worst offenders first
    sorted_file_reports = sorted(project_report.file_reports, key=lambda f: f.bloat_score, reverse=True)

    # Build Client-Side Data Map for JS Modal Inspector
    file_data_map = {}
    for item in project_report.file_reports:
        key = item.file_path
        max_cc = item.metrics.max_cc if item.metrics else 0
        dead_count = len(item.metrics.dead_code) if item.metrics else 0
        opt_lines = item.optimized_lines or item.original_lines
        lines_saved = max(0, item.original_lines - opt_lines)

        bloat_map_list = []
        for entry in item.bloat_map:
            bloat_map_list.append(
                {
                    "severity": entry.severity,
                    "bloat_type": entry.bloat_type,
                    "line_start": entry.line_start,
                    "line_end": entry.line_end,
                    "explanation": entry.explanation,
                    "suggestion": entry.suggestion,
                }
            )

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

    js_file_data_map = json.dumps(file_data_map)

    # Build Table Rows for ALL scanned files
    file_rows = []
    for item in sorted_file_reports:
        status_color = (
            "#ff1744"
            if item.bloat_grade == "F"
            else ("#e040fb" if item.bloat_grade == "D" else ("#ffd600" if item.bloat_grade == "C" else "#00e676"))
        )
        bar_width = min(100, max(5, int(item.bloat_score)))
        max_cc = item.metrics.max_cc if item.metrics else 0
        dead_count = len(item.metrics.dead_code) if item.metrics else 0
        escaped_key = item.file_path.replace("\\", "\\\\").replace("'", "\\'")

        file_rows.append(
            f"""
            <tr class="file-row" data-grade="{item.bloat_grade}" data-file="{item.file_path.lower()}" onclick="openSurgeryModal('{escaped_key}')">
                <td style="font-weight:600; color:#c0caf5;">{item.file_path}</td>
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
    file_rows_html = "".join(file_rows)

    # Build Treemap Items with click-to-modal interaction
    treemap_items = []
    for item in project_report.file_reports:
        bg_color = (
            "#ff1744"
            if item.bloat_grade == "F"
            else ("#e040fb" if item.bloat_grade == "D" else ("#ffd600" if item.bloat_grade == "C" else "#00e676"))
        )
        size_flex = max(1, item.original_lines)
        max_cc = item.metrics.max_cc if item.metrics else 0
        file_name_clean = Path(item.file_path).name
        escaped_key = item.file_path.replace("\\", "\\\\").replace("'", "\\'")
        treemap_items.append(
            f"""
            <div class="tree-box" style="flex-grow: {size_flex}; background: {bg_color}1a; border: 1px solid {bg_color};"
                 title="Click to inspect: {item.file_path} (Grade {item.bloat_grade})"
                 onclick="openSurgeryModal('{escaped_key}')">
                <div class="tree-name" style="color: {bg_color};">{file_name_clean}</div>
                <div class="tree-meta">{item.original_lines} L | CC {max_cc}</div>
            </div>
            """
        )
    treemap_html = "".join(treemap_items)

    # Cross-File Intelligence Section HTML
    phantom_items_html = ""
    if project_report.phantom_functions:
        pf_rows = "".join(
            f'<li style="margin-bottom:6px;"><code>{pf.function_name}()</code> in <span style="color:var(--cyan);">{pf.file_path}:L{pf.line_number}</span></li>'
            for pf in project_report.phantom_functions
        )
        phantom_items_html = f"""
        <div class="card" style="border-color: #ffd600;">
            <div style="color: var(--yellow); font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">
                👻 Phantom Functions ({len(project_report.phantom_functions)})
            </div>
            <ul style="font-size: 13px; list-style: none; color: var(--text-main);">
                {pf_rows}
            </ul>
        </div>
        """

    hallucination_items_html = ""
    if project_report.hallucination_spread:
        hs_rows = "".join(
            f'<li style="margin-bottom:6px;"><code style="color:var(--magenta);">{pkg}</code> imported in <strong>{len(files)}</strong> files ({", ".join(files[:3])})</li>'
            for pkg, files in project_report.hallucination_spread.items()
        )
        hallucination_items_html = f"""
        <div class="card" style="border-color: #e040fb;">
            <div style="color: var(--magenta); font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">
                ☣️ Hallucination Spread Index ({len(project_report.hallucination_spread)})
            </div>
            <ul style="font-size: 13px; list-style: none; color: var(--text-main);">
                {hs_rows}
            </ul>
        </div>
        """

    # Codebase Fingerprint Bar HTML
    fp = project_report.fingerprint
    fp_clean_pct = fp.clean_pct
    fp_dead_pct = round((fp.dead_lines / fp.total_lines * 100), 1) if fp.total_lines > 0 else 0.0
    fp_complex_pct = round((fp.complex_lines / fp.total_lines * 100), 1) if fp.total_lines > 0 else 0.0
    fp_dup_pct = round((fp.duplicate_lines / fp.total_lines * 100), 1) if fp.total_lines > 0 else 0.0

    hallucination_spread_pct = (
        len(project_report.hallucination_spread) / total_files * 100.0 if total_files > 0 else 0.0
    )

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeSlim Project Observatory — {project_report.project_path}</title>
    <style>
        :root {{
            --bg-color: #1a1b26;
            --card-bg: #24283b;
            --text-main: #c0caf5;
            --text-dim: #7982a9;
            --cyan: #00e5ff;
            --emerald: #00e676;
            --yellow: #ffd600;
            --red: #ff1744;
            --magenta: #e040fb;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }}
        body {{ background: var(--bg-color); color: var(--text-main); padding: 30px; line-height: 1.5; }}
        header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2ac3de; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ font-size: 24px; font-weight: 800; color: var(--cyan); letter-spacing: 0.5px; }}
        .meta-tag {{ background: #2ac3de22; color: var(--cyan); border: 1px solid var(--cyan); padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }}
        .grid-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: var(--card-bg); border-radius: 12px; padding: 20px; border: 1px solid #414868; }}
        .stat-val {{ font-size: 32px; font-weight: 800; margin-top: 5px; }}
        .badge {{ padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; display: inline-block; }}
        
        .section-title {{ font-size: 18px; font-weight: 700; color: var(--cyan); margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }}
        
        /* Treemap */
        .treemap-container {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 30px; min-height: 120px; }}
        .tree-box {{ padding: 12px; border-radius: 8px; min-width: 130px; transition: transform 0.15s ease; cursor: pointer; }}
        .tree-box:hover {{ transform: translateY(-3px); filter: brightness(1.2); }}
        .tree-name {{ font-weight: 700; font-size: 13px; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .tree-meta {{ font-size: 11px; color: var(--text-dim); }}
        
        /* Controls & Search */
        .controls {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; gap: 15px; }}
        .search-input {{ background: #1a1b26; border: 1px solid #414868; color: var(--text-main); padding: 10px 16px; border-radius: 8px; width: 300px; outline: none; }}
        .search-input:focus {{ border-color: var(--cyan); }}
        .btn-group {{ display: flex; gap: 8px; }}
        .filter-btn {{ background: #1a1b26; border: 1px solid #414868; color: var(--text-dim); padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px; }}
        .filter-btn.active, .filter-btn:hover {{ border-color: var(--cyan); color: var(--cyan); background: #2ac3de11; }}

        /* Table */
        table {{ width: 100%; border-collapse: collapse; background: var(--card-bg); border-radius: 12px; overflow: hidden; border: 1px solid #414868; }}
        th, td {{ padding: 14px 18px; text-align: left; border-bottom: 1px solid #2f354f; font-size: 14px; }}
        th {{ background: #1f2335; color: var(--text-dim); font-size: 12px; text-transform: uppercase; letter-spacing: 0.8px; }}
        tr.file-row {{ cursor: pointer; transition: background 0.15s ease; }}
        tr.file-row:hover td {{ background: #2e3440; }}
        tr:last-child td {{ border-bottom: none; }}
        
        /* Gauge SVG */
        .gauge-wrapper {{ display: flex; align-items: center; gap: 20px; }}

        /* Fingerprint Bar */
        .fingerprint-bar {{ display: flex; height: 16px; border-radius: 8px; overflow: hidden; background: #1a1b26; margin: 12px 0; }}
        .fp-segment {{ height: 100%; }}

        /* Glassmorphic Modal */
        .modal-backdrop {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 16, 22, 0.85); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 20px; }}
        .modal-card {{ background: #1f2335; border: 1px solid #414868; border-radius: 16px; width: 100%; max-width: 900px; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.6); animation: fadeIn 0.2s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: scale(0.96); }} to {{ opacity: 1; transform: scale(1); }} }}
        .modal-header {{ padding: 20px 24px; background: #1a1b26; border-bottom: 1px solid #3b4261; display: flex; justify-content: space-between; align-items: center; }}
        .close-btn {{ background: transparent; border: none; color: var(--text-dim); font-size: 24px; cursor: pointer; font-weight: bold; padding: 0 8px; }}
        .close-btn:hover {{ color: var(--red); }}
        .modal-tabs {{ display: flex; background: #16161e; border-bottom: 1px solid #3b4261; padding: 0 24px; gap: 8px; }}
        .modal-tab {{ background: transparent; border: none; color: var(--text-dim); padding: 12px 18px; font-size: 13px; font-weight: 700; cursor: pointer; border-bottom: 2px solid transparent; }}
        .modal-tab.active, .modal-tab:hover {{ color: var(--cyan); border-bottom-color: var(--cyan); }}
        .modal-body {{ padding: 24px; overflow-y: auto; flex-grow: 1; }}
        
        /* Diff Display */
        .diff-code {{ background: #1a1b26; padding: 16px; border-radius: 8px; font-family: 'Consolas', 'Fira Code', monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-break: break-all; border: 1px solid #2f354f; color: #a9b1d6; max-height: 400px; overflow-y: auto; }}
        .diff-line-add {{ color: #00e676; background: #00e67615; display: block; padding: 0 4px; border-radius: 2px; }}
        .diff-line-del {{ color: #ff1744; background: #ff174415; display: block; padding: 0 4px; border-radius: 2px; }}
        .diff-line-header {{ color: #00e5ff; font-weight: bold; }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>🔭 CODESLIM PROJECT OBSERVATORY</h1>
            <p style="color: var(--text-dim); font-size: 13px; margin-top: 4px;">Target Directory: <code>{project_report.project_path}</code></p>
        </div>
        <div>
            <span class="meta-tag">CodeSlim v2.0 HTML Observatory</span>
        </div>
    </header>

    <div class="grid-stats">
        <div class="card gauge-wrapper">
            <svg width="90" height="90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" stroke="#1a1b26" stroke-width="12" fill="none"/>
                <circle cx="50" cy="50" r="40" stroke="{gauge_color}" stroke-width="12" fill="none"
                        stroke-dasharray="251.2" stroke-dashoffset="{251.2 * (1 - score / 100)}"
                        stroke-linecap="round" transform="rotate(-90 50 50)"/>
                <text x="50" y="55" font-size="28" font-weight="800" fill="{gauge_color}" text-anchor="middle">{grade}</text>
            </svg>
            <div>
                <div style="color: var(--text-dim); font-size: 12px; font-weight: 700; text-transform: uppercase;">Overall Health</div>
                <div class="stat-val" style="color: {gauge_color};">{score}</div>
                <div style="font-size: 12px; color: var(--text-dim);">Bloat Index Score</div>
            </div>
        </div>

        <div class="card">
            <div style="color: var(--text-dim); font-size: 12px; font-weight: 700; text-transform: uppercase;">Analyzed Files</div>
            <div class="stat-val" style="color: var(--cyan);">{total_files}</div>
            <div style="font-size: 12px; color: var(--text-dim); margin-top: 4px;">
                <span style="color: var(--emerald); font-weight: 700;">{clean_files} Clean</span> | 
                <span style="color: var(--yellow); font-weight: 700;">{moderate_files} Moderate</span> | 
                <span style="color: var(--red); font-weight: 700;">{severe_files} Severe</span>
            </div>
        </div>

        <div class="card">
            <div style="color: var(--text-dim); font-size: 12px; font-weight: 700; text-transform: uppercase;">Cross-File Anomalies</div>
            <div class="stat-val" style="color: var(--magenta);">{len(project_report.phantom_functions)}</div>
            <div style="font-size: 12px; color: var(--text-dim); margin-top: 4px;">
                Phantom Functions | <span style="color: var(--cyan);">{hallucination_spread_pct:.1f}%</span> Spread
            </div>
        </div>
    </div>

    <!-- Codebase Fingerprint Bar -->
    <div class="card" style="margin-bottom: 30px;">
        <div style="color: var(--text-dim); font-size: 12px; font-weight: 700; text-transform: uppercase;">Codebase Composition Fingerprint ({fp.total_lines:,} total lines)</div>
        <div class="fingerprint-bar">
            <div class="fp-segment" style="width: {fp_clean_pct}%; background: var(--emerald);" title="Clean Code: {fp_clean_pct}%"></div>
            <div class="fp-segment" style="width: {fp_dead_pct}%; background: var(--yellow);" title="Dead Code: {fp_dead_pct}%"></div>
            <div class="fp-segment" style="width: {fp_complex_pct}%; background: var(--red);" title="Complex Code: {fp_complex_pct}%"></div>
            <div class="fp-segment" style="width: {fp_dup_pct}%; background: var(--cyan);" title="Duplication: {fp_dup_pct}%"></div>
        </div>
        <div style="display: flex; gap: 20px; font-size: 12px; color: var(--text-dim);">
            <span><strong style="color: var(--emerald);">Clean:</strong> {fp.clean_lines:,} ({fp_clean_pct}%)</span>
            <span><strong style="color: var(--yellow);">Dead:</strong> {fp.dead_lines:,} ({fp_dead_pct}%)</span>
            <span><strong style="color: var(--red);">Complex:</strong> {fp.complex_lines:,} ({fp_complex_pct}%)</span>
            <span><strong style="color: var(--cyan);">Duplicate:</strong> {fp.duplicate_lines:,} ({fp_dup_pct}%)</span>
        </div>
    </div>

    <!-- Cross File Anomaly Details (if any exist) -->
    {"<div class='grid-stats' style='margin-bottom:30px;'>" + phantom_items_html + hallucination_items_html + "</div>" if phantom_items_html or hallucination_items_html else ""}

    <div class="section-title">📊 Codebase Visual Treemap (Click box to inspect diff)</div>
    <div class="treemap-container">
        {treemap_html}
    </div>

    <div class="section-title">⚡ File Bloat Matrix ({len(sorted_file_reports)} files — Click row to inspect diff)</div>
    <div class="controls">
        <input type="text" id="searchInput" class="search-input" placeholder="Search file paths..." onkeyup="filterFiles()">
        <div class="btn-group">
            <button class="filter-btn active" onclick="filterGrade('ALL', this)">All</button>
            <button class="filter-btn" onclick="filterGrade('A', this)">Grade A</button>
            <button class="filter-btn" onclick="filterGrade('B', this)">Grade B</button>
            <button class="filter-btn" onclick="filterGrade('C', this)">Grade C</button>
            <button class="filter-btn" onclick="filterGrade('D', this)">Grade D</button>
            <button class="filter-btn" onclick="filterGrade('F', this)">Grade F</button>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>File Path</th>
                <th>Bloat Health</th>
                <th>Total Lines</th>
                <th>Max CC</th>
                <th>Dead Items</th>
                <th>Bloat Score Gauge</th>
            </tr>
        </thead>
        <tbody id="fileTable">
            {file_rows_html}
        </tbody>
    </table>

    <!-- Interactive File Surgery & Diff Inspector Modal -->
    <div id="surgeryModal" class="modal-backdrop" style="display:none;" onclick="closeModalOnBackdrop(event)">
        <div class="modal-card" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div>
                    <h2 id="modalFileName" style="color:var(--cyan); font-size:18px; font-weight:800;">File Inspector</h2>
                    <p id="modalSubTitle" style="color:var(--text-dim); font-size:12px; margin-top:2px;">Detailed surgery metrics & unified diff preview</p>
                </div>
                <button class="close-btn" onclick="closeSurgeryModal()">&times;</button>
            </div>
            <div class="modal-tabs">
                <button id="btnTabImpact" class="modal-tab active" onclick="switchModalTab('impact')">📊 Impact Metrics</button>
                <button id="btnTabFindings" class="modal-tab" onclick="switchModalTab('findings')">⚠️ Bloat Findings</button>
                <button id="btnTabDiff" class="modal-tab" onclick="switchModalTab('diff')">🔍 Code Diff Viewer</button>
            </div>
            <div class="modal-body">
                <!-- Tab 1: Impact Metrics -->
                <div id="tabImpact" class="tab-pane">
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:15px; margin-bottom:20px;">
                        <div style="background:#1a1b26; padding:16px; border-radius:8px; border:1px solid #3b4261;">
                            <div style="color:var(--text-dim); font-size:11px; font-weight:700;">BLOAT SCORE</div>
                            <div id="mBloatScore" style="font-size:24px; font-weight:800; margin-top:4px;">-</div>
                        </div>
                        <div style="background:#1a1b26; padding:16px; border-radius:8px; border:1px solid #3b4261;">
                            <div style="color:var(--text-dim); font-size:11px; font-weight:700;">ORIGINAL LINES</div>
                            <div id="mOrigLines" style="font-size:24px; font-weight:800; color:var(--text-main); margin-top:4px;">-</div>
                        </div>
                        <div style="background:#1a1b26; padding:16px; border-radius:8px; border:1px solid #3b4261;">
                            <div style="color:var(--text-dim); font-size:11px; font-weight:700;">LINES SAVED</div>
                            <div id="mLinesSaved" style="font-size:24px; font-weight:800; color:var(--emerald); margin-top:4px;">-</div>
                        </div>
                        <div style="background:#1a1b26; padding:16px; border-radius:8px; border:1px solid #3b4261;">
                            <div style="color:var(--text-dim); font-size:11px; font-weight:700;">MAX CYCLOMATIC CC</div>
                            <div id="mMaxCC" style="font-size:24px; font-weight:800; color:var(--yellow); margin-top:4px;">-</div>
                        </div>
                    </div>
                </div>

                <!-- Tab 2: Bloat Findings -->
                <div id="tabFindings" class="tab-pane" style="display:none;">
                    <div id="mFindingsContainer"></div>
                </div>

                <!-- Tab 3: Code Diff -->
                <div id="tabDiff" class="tab-pane" style="display:none;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span style="font-size:12px; color:var(--text-dim); font-weight:600;">Unified Diff Patch Preview</span>
                        <button onclick="copyModalDiff()" style="background:#2ac3de22; border:1px solid var(--cyan); color:var(--cyan); padding:4px 10px; border-radius:4px; font-size:11px; font-weight:700; cursor:pointer;">Copy Diff</button>
                    </div>
                    <div id="mDiffContainer" class="diff-code">No diff available.</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const FILE_DATA_MAP = {js_file_data_map};

        let currentActiveKey = null;

        function openSurgeryModal(fileKey) {{
            const data = FILE_DATA_MAP[fileKey];
            if (!data) return;

            currentActiveKey = fileKey;
            document.getElementById('modalFileName').textContent = data.file_path;
            document.getElementById('modalSubTitle').textContent = 'Bloat Grade ' + data.bloat_grade + ' | ' + data.original_lines + ' lines';

            // Metrics
            const scoreColor = data.bloat_grade === 'F' ? '#ff1744' : (data.bloat_grade === 'D' ? '#e040fb' : (data.bloat_grade === 'C' ? '#ffd600' : '#00e676'));
            document.getElementById('mBloatScore').innerHTML = '<span style="color:' + scoreColor + ';">' + data.bloat_score + '</span> (Grade ' + data.bloat_grade + ')';
            document.getElementById('mOrigLines').textContent = data.original_lines;
            document.getElementById('mLinesSaved').textContent = '-' + data.lines_saved + ' lines';
            document.getElementById('mMaxCC').textContent = data.max_cc;

            // Findings
            const fContainer = document.getElementById('mFindingsContainer');
            if (data.bloat_map && data.bloat_map.length > 0) {{
                let fHtml = '<ul style="list-style:none; display:flex; flex-direction:column; gap:8px;">';
                data.bloat_map.forEach(entry => {{
                    const badgeColor = entry.severity === 'high' ? '#ff1744' : '#ffd600';
                    fHtml += '<li style="background:#1a1b26; padding:12px; border-radius:6px; border:1px solid #2f354f;">' +
                             '<span class="badge" style="background:' + badgeColor + '22; color:' + badgeColor + '; border:1px solid ' + badgeColor + '; margin-right:8px;">' + entry.severity.toUpperCase() + '</span>' +
                             '<strong>Lines ' + entry.line_start + '-' + entry.line_end + ':</strong> ' + entry.explanation +
                             '</li>';
                }});
                fHtml += '</ul>';
                fContainer.innerHTML = fHtml;
            }} else {{
                fContainer.innerHTML = '<div style="color:var(--emerald); font-weight:700;">No bloat findings reported. File is clean!</div>';
            }}

            // Diff
            const dContainer = document.getElementById('mDiffContainer');
            if (data.diff && data.diff.trim().length > 0) {{
                const lines = data.diff.split('\\n');
                let formattedDiff = '';
                lines.forEach(l => {{
                    if (l.startsWith('+') && !l.startsWith('+++')) {{
                        formattedDiff += '<span class="diff-line-add">' + escapeHtml(l) + '</span>';
                    }} else if (l.startsWith('-') && !l.startsWith('---')) {{
                        formattedDiff += '<span class="diff-line-del">' + escapeHtml(l) + '</span>';
                    }} else if (l.startsWith('@@') || l.startsWith('---') || l.startsWith('+++')) {{
                        formattedDiff += '<span class="diff-line-header">' + escapeHtml(l) + '</span>\\n';
                    }} else {{
                        formattedDiff += escapeHtml(l) + '\\n';
                    }}
                }});
                dContainer.innerHTML = formattedDiff;
            }} else {{
                dContainer.innerHTML = '<div style="color:var(--text-dim);">No code modifications required for this file.</div>';
            }}

            switchModalTab('impact');
            document.getElementById('surgeryModal').style.display = 'flex';
        }}

        function closeSurgeryModal() {{
            document.getElementById('surgeryModal').style.display = 'none';
        }}

        function closeModalOnBackdrop(e) {{
            if (e.target.id === 'surgeryModal') {{
                closeSurgeryModal();
            }}
        }}

        function switchModalTab(tabName) {{
            document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');

            if (tabName === 'impact') {{
                document.getElementById('btnTabImpact').classList.add('active');
                document.getElementById('tabImpact').style.display = 'block';
            }} else if (tabName === 'findings') {{
                document.getElementById('btnTabFindings').classList.add('active');
                document.getElementById('tabFindings').style.display = 'block';
            }} else if (tabName === 'diff') {{
                document.getElementById('btnTabDiff').classList.add('active');
                document.getElementById('tabDiff').style.display = 'block';
            }}
        }}

        function copyModalDiff() {{
            if (!currentActiveKey || !FILE_DATA_MAP[currentActiveKey]) return;
            const diffText = FILE_DATA_MAP[currentActiveKey].diff;
            navigator.clipboard.writeText(diffText).then(() => {{
                alert('Diff copied to clipboard!');
            }});
        }}

        function escapeHtml(str) {{
            return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        }}

        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') closeSurgeryModal();
        }});

        function filterFiles() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const rows = document.querySelectorAll('.file-row');
            rows.forEach(row => {{
                const filePath = row.getAttribute('data-file');
                if (filePath.includes(query)) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}

        function filterGrade(grade, btn) {{
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const rows = document.querySelectorAll('.file-row');
            rows.forEach(row => {{
                const rowGrade = row.getAttribute('data-grade');
                if (grade === 'ALL' || rowGrade === grade) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    return html_template


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
    output_path.write_text(html_content, encoding="utf-8")
    log.info("html_report_exported", path=str(output_path), bytes=len(html_content))
    return output_path
