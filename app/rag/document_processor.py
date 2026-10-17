
from pathlib import Path

from app.rag.chunking import chunk_document
from app.rag.document_loader import load_documents


def process_documents(
    docs_dir: str | Path,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """
    Load documents and split them into source-aware chunks.
    """

    documents = load_documents(docs_dir)
    processed_chunks = []

    for document in documents:
        source = document["source"]

        chunks = chunk_document(
            text=document["text"],
            document_id=source,
            source=source,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        processed_chunks.extend(chunks)

    return processed_chunks
