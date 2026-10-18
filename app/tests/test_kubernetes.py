
from unittest.mock import patch, Mock

from app.tools.kubernetes_tools import (
    get_pods,
    get_events,
    get_pod_logs,
)


@patch("app.tools.kubernetes_tools.subprocess.run")
def test_get_pods_uses_read_only_command(mock_run):
    mock_run.return_value = Mock(
        returncode=0,
        stdout='{"items": []}',
        stderr="",
    )

    result = get_pods("default")

    assert result == {"ok": True, "data": {"items": []}}
    command = mock_run.call_args.args[0]
    assert command[:3] == ["kubectl", "get", "pods"]
    assert "default" in command
    assert mock_run.call_args.kwargs["shell"] is False


@patch("app.tools.kubernetes_tools.subprocess.run")
def test_get_events_uses_read_only_command(mock_run):
    mock_run.return_value = Mock(
        returncode=0,
        stdout='{"items": []}',
        stderr="",
    )

    result = get_events("default")

    assert result == {"ok": True, "data": {"items": []}}
    command = mock_run.call_args.args[0]
    assert command[:3] == ["kubectl", "get", "events"]


@patch("app.tools.kubernetes_tools.subprocess.run")
def test_get_pod_logs_uses_requested_tail(mock_run):
    mock_run.return_value = Mock(
        returncode=0,
        stdout="Pod başladı",
        stderr="",
    )

    result = get_pod_logs("web-pod", namespace="default", tail=50)

    assert result == {"ok": True, "data": "Pod başladı"}
    command = mock_run.call_args.args[0]
    assert "web-pod" in command
    assert "--tail=50" in command


@patch("app.tools.kubernetes_tools.subprocess.run")
def test_invalid_namespace_does_not_run_command(mock_run):
    result = get_pods("invalid namespace!")

    assert result["ok"] is False
    assert "Geçersiz namespace" in result["error"]
    mock_run.assert_not_called()


@patch("app.tools.kubernetes_tools.subprocess.run")
def test_invalid_pod_name_does_not_run_command(mock_run):
    result = get_pod_logs("web pod")

    assert result["ok"] is False
    assert "Geçersiz pod" in result["error"]
    mock_run.assert_not_called()


@patch("app.tools.kubernetes_tools.subprocess.run")
def test_invalid_tail_does_not_run_command(mock_run):
    result = get_pod_logs("web-pod", tail=10000)

    assert result["ok"] is False
    assert "1 ile 500" in result["error"]
    mock_run.assert_not_called()


@patch("app.tools.kubernetes_tools.subprocess.run")
def test_kubectl_error_is_returned_safely(mock_run):
    mock_run.return_value = Mock(
        returncode=1,
        stdout="",
        stderr="No resources found",
    )

    result = get_pods()

    assert result["ok"] is False
    assert result["error"] == "No resources found"


@patch("app.tools.kubernetes_tools.subprocess.run")
def test_kubectl_timeout_is_handled(mock_run):
    import subprocess

    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd="kubectl",
        timeout=10,
    )

    result = get_pods()

    assert result["ok"] is False
    assert "zaman aşımına" in result["error"]
