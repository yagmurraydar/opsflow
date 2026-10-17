
from pathlib import Path


def load_documents(docs_dir: str | Path) -> list[dict[str, str]]:
    """
    Load Markdown documents from a directory.

    Each document contains its source path and text content.
    """

    docs_path = Path(docs_dir)

    if not docs_path.exists():
        raise FileNotFoundError(
            f"Doküman klasörü bulunamadı: {docs_path}"
        )

    if not docs_path.is_dir():
        raise NotADirectoryError(
            f"Belirtilen yol bir klasör değil: {docs_path}"
        )

    documents = []

    for file_path in sorted(docs_path.rglob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        documents.append(
            {
                "source": file_path.as_posix(),
                "text": content,
            }
        )

    return documents
