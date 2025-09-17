from typing import Dict, Any
from src.rag.history import get_history, append_turn
from src.rag.intents import classify
from src.rag.query_rewriter import rewrite
from src.rag.datetime import now_warsaw
from src.rag.chain import PROMPT, format_docs
from src.rag.provider import get_llm, get_local_llm
from src.rag.retriever import retrieve

def chat_once(session_id: str, message: str) -> Dict[str, Any]:
    hx = get_history(session_id)
    intent = classify(message, hx)["intent"]

    if intent == "GREETING":
        answer = "Cześć! W czym mogę pomóc?"
        append_turn(session_id, message, answer)
        return {"answer": answer, "intent": intent, "sources": []}

    if intent == "DATETIME":
        now = now_warsaw()
        answer = f"Dziś jest {now['date']} ({now['weekday_pl']}), godzina {now['time']} (Europe/Warsaw)."
        append_turn(session_id, message, answer)
        return {"answer": answer, "intent": intent, "sources": []}

    if intent in {"GIBBERISH","TEST"}:
        answer = "Nie rozumiem pytania. Sformułuj je proszę inaczej (krótko i precyzyjnie)."
        append_turn(session_id, message, answer)
        return {"answer": answer, "intent": intent, "sources": []}

    query = message
    if intent == "FOLLOW_UP":
        query = rewrite(session_id, message)

    docs = retrieve(query, k=5)
    if not docs:
        answer = "Nie wiem na podstawie posiadanych materiałów."
        append_turn(session_id, message, answer)
        return {"answer": answer, "intent": intent, "sources": []}

    context = format_docs(docs)
    llm = get_llm().bind(temperature=0)  
    text = llm.invoke(PROMPT.format(question=query, context=context)).content

    # deduplicate sources
    seen, sources = set(), []
    for d in docs:
        key = (d.metadata.get("source") or "", d.metadata.get("title") or "")
        if key in seen: continue
        seen.add(key)
        sources.append({"title": d.metadata.get("title"),
                        "source": d.metadata.get("source"),
                        "preview": d.page_content[:300]})

    append_turn(session_id, message, text)
    return {"answer": text, "intent": intent, "sources": sources}
