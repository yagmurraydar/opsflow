
import json
import logging

import ollama

from app.tools.project_tools import get_project_info

MODEL_NAME = "qwen3:0.6b"
MAX_TOOL_CALLS = 3

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Sen Agentic DevOps Platform projesinin AI asistanısın.
Türkçe, açık ve anlaşılır cevap ver.
Proje hakkında güncel bilgi gerektiğinde get_project_info aracını kullan.
Araçtan gelen bilgileri esas al; bilmediğin bilgileri uydurma.
"""


# Agent'ın kullanmasına izin verilen araçlar.
TOOL_REGISTRY = {
    "get_project_info": get_project_info,
}


def generate_response(message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    tool_call_count = 0

    try:
        while True:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                tools=[get_project_info],
            )

            assistant_message = response.message
            messages.append(assistant_message)

            tool_calls = assistant_message.tool_calls or []

            # Model araç çağrısı üretmediyse yanıtı döndür.
            if not tool_calls:
                return assistant_message.content or "Yanıt üretilemedi."

            # Sınırsız araç çağrısını önle.
            if tool_call_count + len(tool_calls) > MAX_TOOL_CALLS:
                return "Güvenlik sınırı nedeniyle araç çağrısı durduruldu."

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                logger.info("Agent araç çağırdı: %s", tool_name)
                arguments = tool_call.function.arguments or {}

                # Yalnızca kayıtlı araçlara izin ver.
                tool_function = TOOL_REGISTRY.get(tool_name)

                if tool_function is None:
                    tool_result = {
                        "error": f"İzin verilmeyen araç: {tool_name}"
                    }
                elif arguments:
                    # get_project_info parametre kabul etmez.
                    tool_result = {
                        "error": "Bu araç parametre kabul etmiyor."
                    }
                else:
                    try:
                        tool_result = tool_function()
                    except Exception:
                        logger.exception("Araç çalıştırılırken hata oluştu.")
                        tool_result = {
                            "error": "Araç çalıştırılamadı."
                        }

                tool_call_count += 1

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": json.dumps(
                            tool_result,
                            ensure_ascii=False,
                        ),
                    }
                )

    except ollama.ResponseError:
        logger.exception("Ollama model yanıt hatası.")
        raise

    except Exception:
        logger.exception("Agent çalışırken beklenmeyen hata oluştu.")
        raise

