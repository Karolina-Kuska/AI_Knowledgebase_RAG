from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from src.rag.provider import get_llm, get_local_llm
from src.rag.retriever import retrieve

SYSTEM = """Jesteś asystentem Q&A. Odpowiadaj wyłącznie na podstawie dostarczonego kontekstu.
Jeśli brak odpowiedzi w kontekście, powiedz: „Nie wiem na podstawie posiadanych materiałów.”
Zawsze zwróć źródła (title/url)."""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("user", "Pytanie: {question}\n\nKontekst:\n{context}\n\nOdpowiedz z cytatami źródeł.")
])

def format_docs(docs):
    return "\n\n".join(
        f"[{i+1}] {d.metadata.get('title') or d.metadata.get('source')}\n{d.page_content}"
        for i, d in enumerate(docs)
    )

def answer_question(question: str) -> Dict[str, Any]:
    docs = retrieve(question, k=5)
    context = format_docs(docs)
    prompt = PROMPT.format(question=question, context=context)

    llm = get_llm()
    try:
        text = llm.invoke(prompt).content
    except Exception:
        fallback = get_local_llm()
        if not fallback:
            raise
        text = fallback.invoke(prompt).content  # opcjonalny fallback

    sources = [
        {
            "title": d.metadata.get("title"),
            "source": d.metadata.get("source"),
            "preview": d.page_content[:300],
        }
        for d in docs
    ]
    return {"answer": text, "sources": sources}
