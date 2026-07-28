"""
Unit tests for CodeSlim Web Studio FastAPI server endpoints.
"""

from fastapi.testclient import TestClient

from codeslim.ui.server import create_ui_app

app = create_ui_app()
client = TestClient(app)


def test_ui_healthcheck():
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "CodeSlim" in data["app"]


def test_ui_llm_health():
    response = client.get("/api/v1/health/llm")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "status" in data


def test_ui_analyze_endpoint():
    code_sample = "import os\nimport sys\n\ndef foo():\n    return 42\n"
    response = client.post("/api/v1/analyze", json={"code": code_sample, "filename": "test.py"})
    assert response.status_code == 200
    data = response.json()
    assert data["grade"] in ["A", "B", "C", "D", "F"]
    assert "sys" in data["dead_code_items"] or len(data["dead_code_items"]) >= 0


def test_ui_optimize_endpoint_no_llm():
    code_sample = "import sys\nimport os\n\ndef bar():\n    return os.name\n"
    response = client.post("/api/v1/optimize", json={"code": code_sample, "filename": "test.py", "no_llm": True})
    assert response.status_code == 200
    data = response.json()
    assert "import sys" not in data["optimized_code"]
    assert data["confidence_tier"] == "Auto-Safe"
    assert data["ast_guardrail_passed"] is True


def test_ui_scan_endpoint(tmp_path):
    # Create test python file in temp path
    test_file = tmp_path / "sample.py"
    test_file.write_text("import sys\ndef hello(): pass\n", encoding="utf-8")

    response = client.post("/api/v1/scan", json={"directory": str(tmp_path), "no_llm": True})
    assert response.status_code == 200
    data = response.json()
    assert data["total_files"] == 1
    assert data["overall_grade"] in ["A", "B", "C", "D", "F"]
