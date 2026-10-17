
import json
import logging

import ollama

from app.tools.project_tools import get_project_info
from app.rag.knowledge_tool import search_knowledge_base

MODEL_NAME = "qwen3:0.6b"
MAX_TOOL_CALLS = 3

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Sen Agentic DevOps Platform projesinin AI asistanısın.
Türkçe, açık ve anlaşılır cevap ver.
Proje hakkında güncel bilgi gerektiğinde get_project_info aracını kullan.
Teknik sorularda verilen RAG kanıtlarına dayan.
Kanıtlarda bulunmayan bilgileri uydurma.
Yanıtında kullandığın kaynak dosyasının adını belirt.
Yanıtını gereksiz ayrıntıya girmeden ver.
"""

TOOL_REGISTRY = {
    "get_project_info": get_project_info,
}

TECHNICAL_KEYWORDS = (
    "kubernetes", "kubectl", "pod", "crashloopbackoff",
    "docker", "container", "devops", "deployment",
    "runbook", "log", "hata", "linux", "pipeline",
    "ci/cd", "aws", "postgres", "veritabanı",
    "teknik doküman", "servis",
)


def requires_rag(message: str) -> bool:
    text = message.casefold()
    return any(keyword in text for keyword in TECHNICAL_KEYWORDS)


def generate_response(message: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    try:
        if requires_rag(message):
            logger.info("RAG araması başlıyor.")

            try:
                evidence = search_knowledge_base(message)
            except Exception:
                logger.exception("RAG araması başarısız oldu.")
                return (
                    "Teknik bilgi tabanına şu anda erişemiyorum. "
                    "Lütfen PostgreSQL bağlantısını ve RAG aramasını kontrol edin."
                )

            logger.info("RAG araması tamamlandı.")


            if not evidence or "İlgili teknik doküman bulunamadı." in evidence:
               return "Teknik dokümanlarda ilgili kanıt bulunamadı."

            logger.info("RAG kanıtları bulundu; kaynaklı yanıt döndürülüyor.")

            return (
                "Teknik dokümanlardan bulunan kanıtlar:\n\n"
                 + evidence
)
            
            messages.append({
                "role": "system",
                "content": (
                    "Aşağıdaki metin teknik bilgi tabanından getirilmiştir. "
                    "Yalnızca ilgili kanıtlara dayan. "
                    "Komutları ve kaynak adını doğru aktar. "
                    "Kanıtta bulunmayan bilgileri uydurma.\n\n"
                    + evidence
                ),
            })

        messages.append({"role": "user", "content": message})

        tool_call_count = 0

        while True:
            logger.info("Ollama yanıtı bekleniyor.")

            response = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                tools=[get_project_info],
                options={
                    "num_predict": 180,
                    "temperature": 0.2,
                },
            )

            logger.info("Ollama yanıtı alındı.")

            assistant_message = response.message
            messages.append(assistant_message)

            tool_calls = assistant_message.tool_calls or []

            if not tool_calls:
                answer = assistant_message.content
                return answer or "Model boş yanıt üretti."

            if tool_call_count + len(tool_calls) > MAX_TOOL_CALLS:
                return "Güvenlik sınırı nedeniyle araç çağrısı durduruldu."

            for tool_call in tool_calls:
                name = tool_call.function.name
                arguments = tool_call.function.arguments or {}

                logger.info("Agent araç çağırdı: %s", name)

                function = TOOL_REGISTRY.get(name)

                if function is None:
                    result = {"error": f"İzin verilmeyen araç: {name}"}
                elif arguments:
                    result = {"error": "Bu araç parametre kabul etmiyor."}
                else:
                    try:
                        result = function()
                    except Exception:
                        logger.exception("Proje bilgisi aracı başarısız oldu.")
                        result = {"error": "Proje bilgisi alınamadı."}

                tool_call_count += 1

                messages.append({
                    "role": "tool",
                    "tool_name": name,
                    "content": json.dumps(result, ensure_ascii=False),
                })

    except ollama.ResponseError:
        logger.exception("Ollama model yanıt hatası.")
        raise
    except Exception:
        logger.exception("Agent çalışırken beklenmeyen hata oluştu.")
        raise
