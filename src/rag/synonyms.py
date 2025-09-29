import re
import unicodedata

def _norm(s: str) -> str:

    s = s.lower()
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )

FAMILIES = {
    "fkf": {
        "fkf", "f50", "finanse ksiegowe forte",
        "symfonia finanse i ksiegowosc", "symfonia fkf", "symfonia f50"
    },
    "kip": {
        "kip", "kadry i place", "symfonia kadry i place", "symfonia kip"
    },
    "handel": {
        "handel", "h50", "hmf", "hmp", "fap", "hml", "fal", "symfonia handel"
    },
    "ebiuro": {
        "ebiuro", "e biuro", "szybkafaktura", "szybkafaktura.pl", "kokpit biura", "symfonia ebiuro"
    },
    "ebok": {
        "ebok", "e bok", "elektroniczne biuro obslugi klienta", "symfonia id", "konto symfonia"
    },
    "r2platnik": {
        "r2platnik", "r2 platnik", "platnik", "symfonia r2platnik"
    },

    "fiskalizacja": {"fiskalizacja", "fiskalizuj", "drukarka fiskalna"},
    "automatyzacja": {"automatyzacja", "skroty klawiszowe", "przeksiegiwania", "rmk"},
    "instalacja": {"instalacja", "wymagania systemowe", "baza danych"},
    "deklaracje": {"deklaracje", "pit", "jpk", "jpk_v7", "jpk v7k", "jpk_v7k"},
}

SLOTS = {
    "potwierdzenia sald": {"potwierdzenie salda", "uzgodnienie sald", "saldo potwierdzenie"},
    "wydruk": {"druk", "raport", "generuj wydruk"},
}

def _extract_codes_from_text(text: str) -> set[str]:
    """Z tytułów w stylu [F50/FKF] wyciągamy: f50, fkf."""
    codes = set()
    for m in re.findall(r"\[([^\]]+)\]", text or ""):
        for part in m.split("/"):
            p = _norm(part.strip())
            if p:
                codes.add(p)
    return codes

def expand(query: str, title_hint: str | None = None,
           category: str | None = None,
           product: str | None = None) -> list[str]:
    """
    Zwraca listę wariantów zapytania: [oryginał + synonimy domenowe].
    """
    base = {query}
    qn = _norm(query)

    for canon, alts in FAMILIES.items():
        if any(tok in qn for tok in alts | {canon}):
            base.update(alts)


    for key, alts in SLOTS.items():
        if _norm(key) in qn:
            base.update(alts)

    for t in (title_hint, category, product):
        if t:
            codes = _extract_codes_from_text(t)
            for code in codes:
                if code in {"fkf", "f50"}:
                    base.update(FAMILIES["fkf"])
                elif code in {"kip"}:
                    base.update(FAMILIES["kip"])
                elif code in {"h50", "hmf", "hmp", "fap", "hml", "fal"}:
                    base.update(FAMILIES["handel"])
                elif code in {"ebiuro"}:
                    base.update(FAMILIES["ebiuro"])
                elif code in {"ebok"}:
                    base.update(FAMILIES["ebok"])
                elif code in {"r2platnik"}:
                    base.update(FAMILIES["r2platnik"])
                else:
                    base.add(code)
    base.add(_norm(query))

    return [q for q in sorted(base) if q]
