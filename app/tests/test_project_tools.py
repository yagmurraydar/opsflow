
from app.tools.project_tools import get_project_info


def test_get_project_info():
    result = get_project_info()

    assert result["name"] == "Agentic DevOps Platform"
    assert result["version"] == "0.1.0"
    assert result["status"] == "development"


def test_project_version_format():
    result = get_project_info()

    assert isinstance(result["version"], str)
    assert result["version"].count(".") == 2
