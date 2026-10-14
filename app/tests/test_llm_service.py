import app.services.llm_service as llm_service
from unittest.mock import patch, MagicMock
import ollama
from app.services.llm_service import generate_response


@patch("app.services.llm_service.ollama.chat")
def test_generate_response_without_tool_call(mock_chat):
    mock_message = MagicMock()
    mock_message.content = "Merhaba!"
    mock_message.tool_calls = []

    mock_chat.return_value.message = mock_message

    result = generate_response("Merhaba")

    assert result == "Merhaba!"
    mock_chat.assert_called_once()


@patch.dict(
    "app.services.llm_service.TOOL_REGISTRY",
    {"get_project_info": lambda: {
        "name": "Agentic DevOps Platform",
        "version": "0.1.0",
        "description": "LLM-powered Agentic AI platform",
        "status": "development",
    }},
)
@patch("app.services.llm_service.ollama.chat")
def test_generate_response_with_tool_call(mock_chat):


    tool_message = MagicMock()
    tool_message.content = ""
    tool_message.tool_calls = [
        MagicMock(
            function=MagicMock(
                name="get_project_info",
                arguments={},
            )
        )
    ]

    final_message = MagicMock()
    final_message.content = "Projenin sürümü 0.1.0."
    final_message.tool_calls = []

    mock_chat.side_effect = [
        MagicMock(message=tool_message),
        MagicMock(message=final_message),
    ]

    result = generate_response("Projenin sürümü nedir?")

    assert result == "Projenin sürümü 0.1.0."
    assert mock_chat.call_count == 2


import ollama


@patch("app.services.llm_service.ollama.chat")
def test_generate_response_when_ollama_fails(mock_chat):
    mock_chat.side_effect = ollama.ResponseError(
        "Model yanıt hatası",
        status_code=500,
    )

    try:
        generate_response("Merhaba")
        assert False, "Ollama hatası yeniden yükseltilmeliydi."
    except ollama.ResponseError as error:
        assert error.status_code == 500

@patch("app.services.llm_service.ollama.chat")
def test_generate_response_with_unknown_tool(mock_chat):
    tool_message = MagicMock()
    tool_message.content = ""
    tool_message.tool_calls = [
        MagicMock(
            function=MagicMock(
                name="delete_everything",
                arguments={},
            )
        )
    ]

    final_message = MagicMock()
    final_message.content = "İşlem tamamlandı."
    final_message.tool_calls = []

    mock_chat.side_effect = [
        MagicMock(message=tool_message),
        MagicMock(message=final_message),
    ]

    result = generate_response("Her şeyi sil.")

    assert result == "İşlem tamamlandı."
    assert mock_chat.call_count == 2
