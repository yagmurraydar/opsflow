
from unittest.mock import patch

from app.services.llm_service import execute_tool


@patch("app.services.llm_service.get_pods")
def test_execute_tool_get_pods_with_namespace(mock_get_pods):
    mock_get_pods.return_value = {"ok": True, "data": []}

    result = execute_tool("get_pods", {"namespace": "default"})

    assert result == {"ok": True, "data": []}
    mock_get_pods.assert_called_once_with(namespace="default")


@patch("app.services.llm_service.get_events")
def test_execute_tool_get_events_with_namespace(mock_get_events):
    mock_get_events.return_value = {"ok": True, "data": []}

    result = execute_tool("get_events", {"namespace": "production"})

    assert result == {"ok": True, "data": []}
    mock_get_events.assert_called_once_with(namespace="production")


@patch("app.services.llm_service.get_pod_logs")
def test_execute_tool_get_pod_logs_with_arguments(mock_get_logs):
    mock_get_logs.return_value = {"ok": True, "data": "Application started"}

    result = execute_tool(
        "get_pod_logs",
        {"pod_name": "web-pod", "namespace": "default", "tail": 50},
    )

    assert result == {"ok": True, "data": "Application started"}
    mock_get_logs.assert_called_once_with(
        pod_name="web-pod",
        namespace="default",
        tail=50,
    )


def test_execute_tool_rejects_unknown_tool():
    result = execute_tool("delete_cluster", {})

    assert result["ok"] is False
    assert "İzin verilmeyen araç" in result["error"]


def test_execute_tool_rejects_unexpected_argument():
    result = execute_tool("get_pods", {"namespace": "default", "command": "delete"})

    assert result["ok"] is False
    assert "parametresi" in result["error"]


def test_execute_tool_requires_pod_name():
    result = execute_tool("get_pod_logs", {})

    assert result["ok"] is False
    assert "pod_name" in result["error"]


def test_execute_tool_rejects_non_dict_arguments():
    result = execute_tool("get_pods", ["default"])

    assert result["ok"] is False
    assert "sözlük" in result["error"]

def test_execute_tool_analyze_workflow_run():
    result = execute_tool(
        "analyze_workflow_run",
        {
            "status": "completed",
            "conclusion": "failure",
            "failed_step": "Run tests",
        },
    )

    assert result["ok"] is True
    assert result["diagnosis"] == "Pipeline başarısız oldu."
    assert result["failed_step"] == "Run tests"


def test_execute_tool_analyze_workflow_run_rejects_extra_argument():
    result = execute_tool(
        "analyze_workflow_run",
        {
            "status": "completed",
            "conclusion": "success",
            "command": "some-command",
        },
    )

    assert result["ok"] is False
    assert "parametresi" in result["error"]


def test_execute_tool_analyze_workflow_run_rejects_invalid_status():
    result = execute_tool(
        "analyze_workflow_run",
        {
            "status": "unknown",
            "conclusion": None,
        },
    )

    assert result["ok"] is False
