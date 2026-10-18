
def analyze_workflow_run(
    status: str,
    conclusion: str | None,
    failed_step: str | None = None,
    error_message: str | None = None,
) -> dict:
    """CI/CD workflow sonucunu analiz eder; hiçbir sistemi değiştirmez."""

    allowed_statuses = {"queued", "in_progress", "completed"}
    allowed_conclusions = {
        "success",
        "failure",
        "cancelled",
        "timed_out",
        "action_required",
        "skipped",
        "neutral",
    }

    if status not in allowed_statuses:
        return {"ok": False, "error": "Geçersiz workflow durumu."}

    if status == "completed" and conclusion not in allowed_conclusions:
        return {
            "ok": False,
            "error": "Tamamlanan workflow için geçerli bir conclusion gerekli.",
        }

    if status != "completed" and conclusion is not None:
        return {
            "ok": False,
            "error": "Tamamlanmamış workflow için conclusion None olmalı.",
        }

    if failed_step is not None and not isinstance(failed_step, str):
        return {"ok": False, "error": "failed_step metin olmalı."}

    if error_message is not None and not isinstance(error_message, str):
        return {"ok": False, "error": "error_message metin olmalı."}

    if status == "queued":
        diagnosis = "Pipeline henüz çalışmaya başlamadı."
    elif status == "in_progress":
        diagnosis = "Pipeline çalışmaya devam ediyor."
    elif conclusion == "success":
        diagnosis = "Pipeline başarıyla tamamlandı."
    elif conclusion == "failure":
        diagnosis = "Pipeline başarısız oldu."
    elif conclusion == "cancelled":
        diagnosis = "Pipeline iptal edildi."
    elif conclusion == "timed_out":
        diagnosis = "Pipeline zaman aşımına uğradı."
    elif conclusion == "action_required":
        diagnosis = "Pipeline devam etmek için manuel işlem bekliyor."
    elif conclusion == "skipped":
        diagnosis = "Pipeline veya iş adımı atlandı."
    else:
        diagnosis = "Pipeline nötr sonuçla tamamlandı."

    if status == "completed" and conclusion == "failure":
        recommendation = (
            "Başarısız adımın loglarını incele; "
            "mevcut kanıt olmadan kesin hata nedeni varsayma."
        )
    else:
        recommendation = (
            "Yeni bir işlem gerekip gerekmediğini mevcut duruma göre değerlendir."
        )

    return {
        "ok": True,
        "status": status,
        "conclusion": conclusion,
        "diagnosis": diagnosis,
        "failed_step": failed_step,
        "error_message": error_message,
        "recommendation": recommendation,
    }
