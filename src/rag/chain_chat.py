from typing import Dict, Any
from src.rag.history import get_history, append_turn
from src.rag.intents import classify
from src.rag.query_rewriter import rewrite
from src.rag.datetime import now_warsaw
from src.rag.chain import PROMPT, format_docs
from src.rag.provider import get_llm_with_name, get_local_llm
from src.rag.retriever import retrieve


def _bind_zero_temp(llm_obj):
    if not hasattr(llm_obj, "bind"):
        return llm_obj
    if llm_obj.__class__.__module__.startswith("langchain_ollama"):
        return llm_obj.bind(options={"temperature": 0})
    return llm_obj.bind(temperature=0)


def chat_once(session_id: str, message: str) -> Dict[str, Any]:
    hx = get_history(session_id)
    intent = classify(message, hx)["intent"]

    if intent == "GREETING":
        answer = "Cześć! W czym mogę pomóc?"
        append_turn(session_id, message, answer)
        return {"answer": answer, "intent": intent, "sources": [], "engine": "builtin"}

    if intent == "DATETIME":
        now = now_warsaw()
        answer = f"Dziś jest {now['date']} ({now['weekday_pl']}), godzina {now['time']} (Europe/Warsaw)."
        append_turn(session_id, message, answer)
        return {"answer": answer, "intent": intent, "sources": [], "engine": "builtin"}

    if intent in {"GIBBERISH", "TEST"}:
        answer = "Nie rozumiem pytania. Sformułuj je proszę inaczej (krótko i precyzyjnie)."
        append_turn(session_id, message, answer)
        return {"answer": answer, "intent": intent, "sources": [], "engine": "builtin"}

    query = message
    if intent == "FOLLOW_UP":
        query = rewrite(session_id, message)

    docs = retrieve(query, k=5)
    if not docs:
        answer = "Nie wiem na podstawie posiadanych materiałów."
        append_turn(session_id, message, answer)
        return {"answer": answer, "intent": intent, "sources": [], "engine": "builtin"}

    context = format_docs(docs)

    llm, engine = get_llm_with_name()
    llm = _bind_zero_temp(llm)

    prompt = PROMPT.format(question=query, context=context)

    try:
        text = llm.invoke(prompt).content
    except Exception:
        local = get_local_llm()
        if not local:
            answer = "Usługa LLM jest chwilowo niedostępna (brak działającego providera)."
            append_turn(session_id, message, answer)
            return {"answer": answer, "intent": intent, "sources": [], "engine": "none"}
        llm = _bind_zero_temp(local)
        engine = "ollama"
        text = llm.invoke(prompt).content

    seen, sources = set(), []
    for d in docs:
        key = (d.metadata.get("source") or "", d.metadata.get("title") or "")
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "title": d.metadata.get("title"),
            "source": d.metadata.get("source"),
            "preview": d.page_content[:300],
        })

    append_turn(session_id, message, text)
    return {"answer": text, "intent": intent, "sources": sources, "engine": engine}
