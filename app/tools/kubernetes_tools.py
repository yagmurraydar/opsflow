
import json
import re
import subprocess


_RESOURCE_NAME_PATTERN = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")


def _is_valid_resource_name(value: str) -> bool:
    """Validate Kubernetes namespace and pod names."""
    return (
        isinstance(value, str)
        and len(value) <= 63
        and _RESOURCE_NAME_PATTERN.fullmatch(value) is not None
    )


def _run_read_only_command(command: list[str]) -> dict:
    """Run an explicitly constructed kubectl read-only command."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            check=False,
            shell=False,
        )

        if result.returncode != 0:
            return {
                "ok": False,
                "error": result.stderr.strip() or "kubectl komutu başarısız oldu.",
            }

        output = result.stdout.strip()

        try:
            return {"ok": True, "data": json.loads(output)}
        except json.JSONDecodeError:
            return {"ok": True, "data": output}

    except FileNotFoundError:
        return {"ok": False, "error": "kubectl bulunamadı."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Kubernetes isteği zaman aşımına uğradı."}
    except OSError:
        return {"ok": False, "error": "Kubernetes komutu çalıştırılamadı."}


def get_pods(namespace: str = "default") -> dict:
    """List pods in a namespace; does not modify cluster state."""
    if not _is_valid_resource_name(namespace):
        return {"ok": False, "error": "Geçersiz namespace adı."}

    return _run_read_only_command(
        ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
    )


def get_events(namespace: str = "default") -> dict:
    """List events in a namespace; does not modify cluster state."""
    if not _is_valid_resource_name(namespace):
        return {"ok": False, "error": "Geçersiz namespace adı."}

    return _run_read_only_command(
        ["kubectl", "get", "events", "-n", namespace, "-o", "json"]
    )


def get_pod_logs(
    pod_name: str,
    namespace: str = "default",
    tail: int = 100,
) -> dict:
    """Read the latest pod logs without executing commands inside the pod."""
    if not _is_valid_resource_name(namespace):
        return {"ok": False, "error": "Geçersiz namespace adı."}

    if not _is_valid_resource_name(pod_name):
        return {"ok": False, "error": "Geçersiz pod adı."}

    if type(tail) is not int or not 1 <= tail <= 500:
        return {"ok": False, "error": "tail değeri 1 ile 500 arasında olmalı."}

    return _run_read_only_command(
        [
            "kubectl",
            "logs",
            pod_name,
            "-n",
            namespace,
            f"--tail={tail}",
        ]
    )
