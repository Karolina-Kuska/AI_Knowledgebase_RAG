import re
from typing import Literal, TypedDict, Optional, List
from src.rag.provider import get_llm

Intent = Literal["GREETING","DATETIME","FOLLOW_UP","VALID","GIBBERISH","TEST"]
_POLITE = re.compile(r"\b(cześć|dzień dobry|hej|witam|dziękuję|dzieki)\b", re.I)
_DATE = re.compile(r"\b(która (jest )?godzina|jaka (jest )?data|dziś|dzisiaj|data|godzina|time|date)\b", re.I)

class Classification(TypedDict):
    intent: Intent
    reason: str

def _heuristics(msg: str, has_history: bool) -> Optional[Classification]:
    m = msg.strip()
    if _POLITE.search(m):
        return {"intent":"GREETING","reason":"greeting regex"}
    if _DATE.search(m):
        return {"intent":"DATETIME","reason":"datetime regex"}
    if len(m) > 3 and re.fullmatch(r"[^a-zA-Z0-9ąćęłńóśżź\s]+", m):
        return {"intent":"GIBBERISH","reason":"symbols only"}
    if has_history and re.search(r"\b(to|a co z|a jak|a on|a ona|a tamto|dlaczego|jak to)\b", m, re.I):
        return {"intent":"FOLLOW_UP","reason":"follow-up regex"}
    return None

def classify(msg: str, history: List[tuple[str,str]]) -> Classification:
    hx = history or []
    hhit = _heuristics(msg, has_history=bool(hx))
    if hhit: return hhit
  
    llm = get_llm()
    prompt = (
        "Zwróć tylko jedno słowo jako etykietę intencji z listy: "
        "GREETING, DATETIME, FOLLOW_UP, VALID, GIBBERISH, TEST.\n"
        "Kryteria:\n"
        "- GREETING: grzecznościowe powitanie/pożegnanie.\n"
        "- DATETIME: pytanie o bieżącą datę/godzinę/strefę.\n"
        "- FOLLOW_UP: pytanie zależne od poprzednich odpowiedzi; zaimki, nawiązania.\n"
        "- VALID: merytoryczne nowe pytanie do KB.\n"
        "- GIBBERISH: niezrozumiały ciąg znaków.\n"
        "- TEST: pytanie testowe o model, prompt, instrukcje, jailbreak itp.\n"
        f"Historia (ostatnie tury): {hx_to_str(hx)}\n"
        f"Pytanie: {msg}\n"
        "Etykieta:"
    )
    resp = llm.bind(temperature=0).invoke(prompt).content.strip().upper()
    intent = resp.split()[0] if resp else "VALID"
    if intent not in {"GREETING","DATETIME","FOLLOW_UP","VALID","GIBBERISH","TEST"}:
        intent = "VALID"
    return {"intent": intent, "reason": "llm"}

def hx_to_str(hx: List[tuple[str,str]]) -> str:
    return " | ".join([f"U:{u} / A:{a}" for u,a in hx[-10:]])
