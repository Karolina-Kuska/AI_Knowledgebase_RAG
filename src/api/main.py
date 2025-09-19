from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from src.rag.retriever import retrieve
from src.rag.chain import PROMPT, format_docs, get_llm, get_local_llm

from src.rag.chain_chat import chat_once
from src.rag.history import clear_history

load_dotenv()

app = FastAPI(title="AI Knowledgebase RAG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
API_KEY = os.getenv("API_KEY")

def verify_key(x_api_key: str = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
class Ask(BaseModel):
    question: str
    category: str | None = None
    product: str | None = None

@app.post("/ask")
def ask(q: Ask):
    docs = retrieve(q.question, k=5, category=q.category, product=q.product)
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
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "title": d.metadata.get("title"),
            "source": d.metadata.get("source"),
            "preview": d.page_content[:300]
        })
    return {"answer": text, "sources": sources}


class ChatReq(BaseModel):
    session_id: str 
    message: str

@app.post("/chat")
def chat(req: ChatReq, _: None = Depends(verify_key)):
    return chat_once(req.session_id, req.message)


class ClearReq(BaseModel):
    session_id: str

@app.post("/chat/clear")
def chat_clear(req: ClearReq):
    clear_history(req.session_id)
    return {"ok": True}

@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
    
    
