
from app.tools.cicd_tools import analyze_workflow_run


def test_successful_workflow():
    result = analyze_workflow_run("completed", "success")
    assert result["ok"] is True
    assert result["diagnosis"] == "Pipeline başarıyla tamamlandı."


def test_failed_workflow():
    result = analyze_workflow_run(
        "completed",
        "failure",
        failed_step="Run tests",
        error_message="3 tests failed",
    )
    assert result["ok"] is True
    assert result["failed_step"] == "Run tests"
    assert result["error_message"] == "3 tests failed"
    assert "loglarını incele" in result["recommendation"]


def test_running_workflow():
    result = analyze_workflow_run("in_progress", None)
    assert result["ok"] is True
    assert result["diagnosis"] == "Pipeline çalışmaya devam ediyor."


def test_invalid_status():
    result = analyze_workflow_run("unknown", None)
    assert result["ok"] is False


def test_completed_workflow_requires_conclusion():
    result = analyze_workflow_run("completed", None)
    assert result["ok"] is False


def test_running_workflow_rejects_conclusion():
    result = analyze_workflow_run("in_progress", "success")
    assert result["ok"] is False


def test_failed_step_must_be_text():
    result = analyze_workflow_run(
        "completed", "failure", failed_step=123
    )
    assert result["ok"] is False
