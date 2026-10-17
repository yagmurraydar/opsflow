
import ollama


EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    """
    Convert text into a numerical vector using Ollama.
    """

    if not text or not text.strip():
        raise ValueError("Embedding üretmek için metin boş olamaz.")

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response["embeddings"][0]
