
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping character-based chunks.

    Args:
        text: The source text to split.
        chunk_size: Maximum number of characters in each chunk.
        overlap: Number of characters shared by consecutive chunks.

    Returns:
        A list of text chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size pozitif bir sayı olmalıdır.")

    if overlap < 0:
        raise ValueError("overlap negatif olamaz.")

    if overlap >= chunk_size:
        raise ValueError("overlap, chunk_size değerinden küçük olmalıdır.")

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks

def chunk_document(
    text: str,
    document_id: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """
    Split a document into chunks and attach source metadata.
    """

    if not document_id.strip():
        raise ValueError("document_id boş olamaz.")

    if not source.strip():
        raise ValueError("source boş olamaz.")

    chunks = chunk_text(
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return [
        {
            "document_id": document_id,
            "source": source,
            "chunk_index": index,
            "text": chunk,
        }
        for index, chunk in enumerate(chunks)
    ]
