from src.rag.provider import get_llm
from src.rag.history import get_history

SYSTEM = (
"Jesteś modułem przepisywania zapytań. "
"Na podstawie historii dialogu masz przepisać ostatnie pytanie na samodzielną, jednozdaniową wersję, "
"bez zaimków wskazujących i odniesień typu 'to', 'tamto'. "
"Nie dodawaj informacji nieobecnych w historii."
)

def rewrite(session_id: str, user_msg: str) -> str:
    hx = get_history(session_id)
    hx_text = "\n".join([f"U: {u}\nA: {a}" for u,a in hx[-10:]])
    user = (
        f"Historia (ostatnie 10 tur):\n{hx_text}\n\n"
        f"Ostatnie pytanie użytkownika:\n{user_msg}\n\n"
        "Zwróć tylko przepisane pytanie jako samodzielne zdanie:"
    )
    llm = get_llm().bind(temperature=0)
    return llm.invoke([("system", SYSTEM), ("user", user)]).content.strip()
