
import json
import logging

import ollama

from app.tools.project_tools import get_project_info
from app.rag.knowledge_tool import search_knowledge_base
from app.tools.kubernetes_tools import get_pods, get_events, get_pod_logs
from app.tools.cicd_tools import analyze_workflow_run

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
    "get_pods": get_pods,
    "get_events": get_events,
    "get_pod_logs": get_pod_logs,
    "analyze_workflow_run": analyze_workflow_run,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_project_info",
            "description": "Projenin güncel adı, sürümü ve durumunu getirir.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pods",
            "description": "Belirtilen Kubernetes namespace içindeki pod listesini okur.",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace adı. Varsayılan: default.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_events",
            "description": "Belirtilen Kubernetes namespace içindeki olayları okur.",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace adı. Varsayılan: default.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pod_logs",
            "description": "Bir Kubernetes podunun son loglarını okur; pod içinde komut çalıştırmaz.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pod_name": {
                        "type": "string",
                        "description": "Logları okunacak podun adı.",
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace adı. Varsayılan: default.",
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Okunacak son log satırı sayısı; 1-500 arası.",
                    },
                },
                "required": ["pod_name"],
            },
        },
    },
    
    {
    "type": "function",
    "function": {
        "name": "analyze_workflow_run",
        "description": (
            "CI/CD workflow durumunu analiz eder. "
            "Pipeline sonucu, başarısız adım ve hata mesajını değerlendirir. "
            "Gerçek CI/CD sisteminde değişiklik yapmaz."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["queued", "in_progress", "completed"],
                    "description": "Workflow durumudur.",
                },
                "conclusion": {
                    "type": ["string", "null"],
                    "enum": [
                        "success",
                        "failure",
                        "cancelled",
                        "timed_out",
                        "action_required",
                        "skipped",
                        "neutral",
                        None,
                    ],
                    "description": (
                        "Workflow tamamlandıysa sonucu; "
                        "henüz tamamlanmadıysa null."
                    ),
                },
                "failed_step": {
                    "type": ["string", "null"],
                    "description": "Başarısız olan adımın adı, biliniyorsa.",
                },
                "error_message": {
                    "type": ["string", "null"],
                    "description": "Hata mesajı, biliniyorsa.",
                },
            },
            "required": ["status", "conclusion"],
        },
    },
},
    
]


def execute_tool(name: str, arguments: dict) -> dict:
    """Run only registered tools with explicitly allowed arguments."""

    if name not in TOOL_REGISTRY:
        return {"ok": False, "error": f"İzin verilmeyen araç: {name}"}

    if not isinstance(arguments, dict):
        return {
            "ok": False,
            "error": "Araç argümanları sözlük biçiminde olmalı.",
        }

    allowed_arguments = {
        "get_project_info": set(),
        "get_pods": {"namespace"},
        "get_events": {"namespace"},
        "get_pod_logs": {"pod_name", "namespace", "tail"},
        "analyze_workflow_run": {
            "status",
            "conclusion",
            "failed_step",
            "error_message",
        },
    }

    if set(arguments) - allowed_arguments[name]:
        return {
            "ok": False,
            "error": "İzin verilmeyen araç parametresi.",
        }

    if name == "get_project_info":
        return get_project_info()

    if name == "get_pods":
        return get_pods(**arguments)

    if name == "get_events":
        return get_events(**arguments)

    if name == "get_pod_logs":
        if not arguments.get("pod_name"):
            return {
                "ok": False,
                "error": "pod_name parametresi gerekli.",
            }
        return get_pod_logs(**arguments)

    if name == "analyze_workflow_run":
        return analyze_workflow_run(**arguments)

    return {"ok": False, "error": "Araç desteklenmiyor."}



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
                tools=TOOL_SCHEMAS,
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

                try:
                    result = execute_tool(name, arguments)
                except Exception:
                    logger.exception("Agent aracı başarısız oldu.")
                    result = {
                        "ok": False,
                        "error": "Araç çalıştırılırken hata oluştu.",
                    }

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
