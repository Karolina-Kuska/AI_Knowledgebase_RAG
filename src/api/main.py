from src.rag.chain import answer_question
from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="AI Knowledgebase RAG")

class Ask(BaseModel):
    question: str
    category: str | None = None
    product: str | None = None

@app.post("/ask")
def ask(q: Ask): 
    from src.rag.retriever import retrieve
    docs = retrieve(q.question, k=5, category=q.category, product=q.product)
 
    from src.rag.chain import PROMPT, format_docs, get_llm, get_local_llm
    if not docs:
        return {"answer": "Nie wiem na podstawie posiadanych materiałów.", "sources": []}
    prompt = PROMPT.format(question=q.question, context=format_docs(docs))
    try:
        text = get_llm().invoke(prompt).content
    except Exception:
        llm = get_local_llm()
        text = llm.invoke(prompt).content if llm else "Nie wiem na podstawie posiadanych materiałów."
 
    seen, sources = set(), []
    for d in docs:
        key = (d.metadata.get("source") or "", d.metadata.get("title") or "")
        if key in seen: continue
        seen.add(key)
        sources.append({"title": d.metadata.get("title"), "source": d.metadata.get("source"), "preview": d.page_content[:300]})
    return {"answer": text, "sources": sources}
