# AI_Knowledgebase_RAG

Aplikacja typu **RAG (Retrieval-Augmented Generation)** w Pythonie +
FastAPI.\
Pozwala zadawać pytania o oprogramowanie Producenta Systemów ERP (np. Kadry i
Płace, eBiuro, KIP) i otrzymywać odpowiedzi na podstawie lokalnej bazy
wiedzy.

## Zawartość projektu

### Główne katalogi

  -----------------------------------------------------------------------
  Ścieżka         Opis
  --------------- -------------------------------------------------------
  `src/api/`      FastAPI: definicja endpointów REST (`main.py`).

  `src/rag/`      Główna logika RAG -- obsługa historii, intencji,
                  zapytań, pobierania dokumentów itp.

  `src/utils/`    Konfiguracja (`settings.py`) i pomocnicze narzędzia.

  `.chroma/`      Lokalna baza wektorowa Chroma z zaindeksowanymi
                  artykułami producenta.
  -----------------------------------------------------------------------

### Kluczowe pliki Pythona

  ----------------------------------------------------------------------------------------
  Plik                              Rola
  --------------------------------- ------------------------------------------------------
  **`src/api/main.py`**             Aplikacja FastAPI. Definiuje endpoint `POST /chat`
                                    (główny czat) i ewentualny `GET /healthz` do
                                    diagnostyki.

  **`src/rag/chain_chat.py`**       Główna pętla zapytań. Łączy historię rozmowy,
                                    klasyfikację intencji, retrieval i wywołanie LLM.
                                    Zwraca JSON z odpowiedzią oraz nazwą użytego silnika
                                    (`engine`).

  **`src/rag/provider.py`**         Konfiguracja i **fallback** modeli: `<br/>`{=html}•
                                    Azure OpenAI (chat + embeddings) `<br/>`{=html}•
                                    lokalny **Ollama**. `<br/>`{=html}Obsługuje aktywny
                                    test zdrowia dla embeddingów i przełączenie na lokalny
                                    model, jeśli Azure jest niedostępny.

  **`src/rag/intents.py`**          Klasyfikacja intencji pytania (`GREETING`, `DATETIME`,
                                    `VALID` itd.). Używa heurystyk regex + modelu LLM (z
                                    fallbackiem).

  **`src/rag/query_rewriter.py`**   Przepisuje zapytania follow-up tak, aby były
                                    samodzielne.

  **`src/rag/datetime.py`**         Zwraca aktualną datę/godzinę w strefie
                                    `Europe/Warsaw`.

  **`src/rag/history.py`**          Proste przechowywanie i odczyt historii konwersacji w
                                    pamięci.

  **`src/rag/chain.py`**            Szablon promptu (`PROMPT`) i formatowanie kontekstu
                                    dokumentów (`format_docs`).

  **`src/rag/retriever.py`**        Wyszukiwanie podobnych dokumentów w bazie Chroma
                                    (`similarity_search`).

  **`src/rag/vectorstore.py`**      Tworzenie/ładowanie instancji bazy wektorowej Chroma
                                    przy użyciu `get_embeddings()` z providera.

  **`src/utils/settings.py`**       Odczyt zmiennych środowiskowych `.env` -- klucze
                                    Azure, konfiguracja Ollama, itp.
  ----------------------------------------------------------------------------------------

## Działanie aplikacji

1.  **Przyjęcie zapytania** -- `POST /chat` z JSON:

    ``` json
    { "session_id": "u1", "message": "jak zainstalować kip" }
    ```

2.  **Klasyfikacja intencji** -- `intents.py` rozpoznaje np. powitanie,
    pytanie o datę, itp.

3.  **Retrieval** -- `retriever.py` wyszukuje najbardziej podobne
    dokumenty (embeddingi w Chroma).

4.  **Generacja odpowiedzi** -- `chain_chat.py` buduje kontekst i
    wywołuje LLM:

    -   Najpierw próbuje **Azure OpenAI**.
    -   Jeśli Azure jest niedostępny (błędny klucz, brak sieci, błąd
        401), automatycznie przełącza się na **lokalny Ollama**.

5.  **Zwrot JSON** z polami:

    -   `answer` -- treść odpowiedzi,
    -   `intent` -- wykryta intencja,
    -   `sources` -- lista źródłowych artykułów,
    -   `engine` -- użyty silnik (`azure-openai`, `ollama`, `builtin`,
        itp.).

## Dane i indeks wektorowy

-   W bazie Chroma znajduje się **23 artykuły** pobrane ręcznie ze
    strony producenta oprogramowania **Symfonia ERP**\
    (np. Kadry i Płace, eBiuro, KIP).\
-   Artykuły zostały ręcznie skopiowane do tabel SQL, a następnie
    zindeksowane w Chroma z wykorzystaniem embeddingów (Azure OpenAI lub
    Ollama -- w zależności od konfiguracji).

## Przykładowe pytania do testów

Możesz pytać m.in.:

-   „Jak zainstalować KIP?"
-   „Kadry i Płace -- przydatne skróty klawiszowe"
-   „Jak wystawiać i wysyłać faktury w programie eBiuro?"
-   „Co to jest SSO?"

Wywołanie API (przykład):

``` bash
curl -X POST http://localhost:8000/chat   -H "Content-Type: application/json"   -d '{"session_id":"u1","message":"Jak zainstalować KIP"}'
```

Otrzymasz JSON z odpowiedzią, listą źródeł oraz informacją z jakiego
silnika LLM korzysta czat.
