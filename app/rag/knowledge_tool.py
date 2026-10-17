
from app.rag.retriever import retrieve_documents


def search_knowledge_base(query: str) -> str:
    """Search technical runbooks and return relevant evidence with sources."""
    results = retrieve_documents(query=query, top_k=3)

    if not results:
        return "İlgili teknik doküman bulunamadı."

    evidence = []

    for result in results:
        evidence.append(
            f"Kaynak: {result['source']}\n"
            f"Benzerlik skoru: {result['score']:.3f}\n"
            f"İçerik:\n{result['text']}"
        )

    return "\n\n---\n\n".join(evidence)
