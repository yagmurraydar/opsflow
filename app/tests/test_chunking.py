
import pytest

from app.rag.chunking import chunk_text


def test_chunk_text_splits_long_text():
    text = "abcdefghijklmnopqrst"

    chunks = chunk_text(
        text,
        chunk_size=10,
        overlap=3,
    )

    assert chunks == [
        "abcdefghij",
        "hijklmnopq",
        "opqrst",
    ]


def test_chunk_text_returns_empty_list_for_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_returns_short_text_as_one_chunk():
    text = "Merhaba dünya"

    assert chunk_text(text, chunk_size=100) == [text]


def test_chunk_text_rejects_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("Merhaba", chunk_size=0)


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("Merhaba", chunk_size=10, overlap=-1)

    with pytest.raises(ValueError):
        chunk_text("Merhaba", chunk_size=10, overlap=10)

def test_chunk_document_includes_source_metadata():
    from app.rag.chunking import chunk_document

    result = chunk_document(
        text="Kubernetes pod loglarını kontrol et.",
        document_id="k8s-001",
        source="docs/kubernetes-runbook.md",
        chunk_size=100,
    )

    assert len(result) == 1
    assert result[0]["document_id"] == "k8s-001"
    assert result[0]["source"] == "docs/kubernetes-runbook.md"
    assert result[0]["chunk_index"] == 0
    assert result[0]["text"] == "Kubernetes pod loglarını kontrol et."


def test_chunk_document_assigns_sequential_indexes():
    from app.rag.chunking import chunk_document

    result = chunk_document(
        text="abcdefghijklmnopqrst",
        document_id="doc-001",
        source="docs/example.txt",
        chunk_size=10,
        overlap=3,
    )

    assert [chunk["chunk_index"] for chunk in result] == [0, 1, 2]


def test_chunk_document_rejects_empty_metadata():
    from app.rag.chunking import chunk_document

    with pytest.raises(ValueError):
        chunk_document(
            text="Example text",
            document_id="",
            source="docs/example.txt",
        )

    with pytest.raises(ValueError):
        chunk_document(
            text="Example text",
            document_id="doc-001",
            source="",
        )
