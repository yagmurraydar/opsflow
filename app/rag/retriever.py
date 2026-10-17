
import math

from app.rag.database import get_connection
from app.rag.embeddings import create_embedding

def decode_text(value):
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value
def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError("Vektörlerin boyutları aynı olmalıdır.")

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def retrieve_documents(
    query: str,
    docs_dir: str = "docs",
    top_k: int = 2,
) -> list[dict]:
    """Sorguya en yakın kayıtlı doküman parçalarını getirir."""
    if not query or not query.strip():
        raise ValueError("Arama sorgusu boş olamaz.")

    if top_k <= 0:
        raise ValueError("top_k pozitif olmalıdır.")

    query_embedding = create_embedding(query)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT source, chunk_index, content, embedding
                FROM document_chunks
                """
            )
            rows = cursor.fetchall()

    if not rows:
        raise RuntimeError(
            "Veritabanında doküman bulunamadı. "
            "Önce index_documents() çalıştırın."
        )

    results = []

    for source, chunk_index, content, embedding in rows:
        score = cosine_similarity(query_embedding, embedding)

        results.append({
    "source": decode_text(source),
    "chunk_index": chunk_index,
    "text": decode_text(content),
    "score": score,
})

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]
