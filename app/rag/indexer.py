
from pathlib import Path

from psycopg.types.json import Jsonb

from app.rag.database import get_connection
from app.rag.document_processor import process_documents
from app.rag.embeddings import create_embedding


def index_documents(docs_dir: str | Path = "docs") -> list[dict]:
    """Dokümanları embedding ile PostgreSQL'e kaydeder."""
    chunks = process_documents(docs_dir)
    indexed_chunks = []

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for chunk in chunks:
                embedding = create_embedding(chunk["text"])

                cursor.execute(
                    """
                    INSERT INTO document_chunks
                        (document_id, source, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (document_id, chunk_index)
                    DO UPDATE SET
                        source = EXCLUDED.source,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        created_at = NOW()
                    """,
                    (
                        chunk["document_id"],
                        chunk["source"],
                        chunk["chunk_index"],
                        chunk["text"],
                        Jsonb(embedding),
                    ),
                )

                indexed_chunks.append({
                    **chunk,
                    "embedding": embedding,
                })

    return indexed_chunks
