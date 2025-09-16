import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from src.rag.chain import answer_question

load_dotenv()
app = FastAPI(title="AI Knowledgebase RAG")

class Ask(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Ask):
    return answer_question(q.question)

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
