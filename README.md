# AI_Knowledgebase_RAG

Aplikacja typu **RAG (Retrieval-Augmented Generation)** w Pythonie z
FastAPI oraz **frontendem w Blazor WebAssembly**. Pozwala zadawać
pytania o oprogramowanie producenta systemów ERP (np. Kadry i Płace,
eBiuro, KIP) i otrzymywać odpowiedzi na podstawie lokalnej bazy wiedzy.

## Zawartość projektu

### Struktura katalogów

  -----------------------------------------------------------------------
  Ścieżka                                            Opis
  -------------------------------------------------- --------------------
  `src/api/`                                         FastAPI -- definicja
                                                     endpointów REST
                                                     (`main.py`).

  `src/rag/`                                         Główna logika RAG:
                                                     obsługa historii,
                                                     intencji, zapytań i
                                                     pobierania
                                                     dokumentów.

  `src/utils/`                                       Konfiguracja
                                                     (`settings.py`) i
                                                     narzędzia
                                                     pomocnicze.

  `frontend/`                                        **Blazor
                                                     WebAssembly** --
                                                     interfejs
                                                     użytkownika
                                                     komunikujący się z
                                                     API.

  `.chroma/`                                         Lokalna baza
                                                     wektorowa Chroma z
                                                     zaindeksowanymi
                                                     artykułami
                                                     producenta.
  -----------------------------------------------------------------------

### Kluczowe pliki

  -----------------------------------------------------------------------
  Plik                                   Rola
  -------------------------------------- --------------------------------
  **`src/api/main.py`**                  Aplikacja FastAPI. Endpoint
                                         `POST /chat` (główny czat) i
                                         `GET /healthz` do diagnostyki.

  **`src/rag/chain_chat.py`**            Główna pętla zapytań: łączy
                                         historię rozmowy, klasyfikację
                                         intencji, retrieval i wywołanie
                                         LLM.

  **`src/rag/provider.py`**              Konfiguracja i fallback modeli:
                                         Azure OpenAI (chat + embeddings)
                                         oraz lokalny Ollama. Obsługuje
                                         test zdrowia i automatyczne
                                         przełączenie w razie awarii.

  **`src/rag/intents.py`**               Klasyfikacja intencji pytania
                                         (`GREETING`, `DATETIME`, `VALID`
                                         itd.). Wykorzystuje regex i
                                         model LLM.

  **`src/rag/query_rewriter.py`**        Przepisuje zapytania follow‑up
                                         na samodzielne.

  **`src/rag/datetime.py`**              Zwraca aktualną datę/godzinę w
                                         strefie `Europe/Warsaw`.

  **`src/rag/history.py`**               Przechowywanie i odczyt historii
                                         konwersacji w pamięci.

  **`src/rag/chain.py`**                 Szablon promptu (`PROMPT`) i
                                         formatowanie kontekstu
                                         dokumentów.

  **`src/rag/retriever.py`**             Wyszukiwanie podobnych
                                         dokumentów w bazie Chroma
                                         (`similarity_search`).

  **`src/rag/vectorstore.py`**           Tworzenie/ładowanie instancji
                                         bazy wektorowej Chroma przy
                                         użyciu `get_embeddings()`.

  **`src/utils/settings.py`**            Odczyt zmiennych środowiskowych
                                         `.env` (klucze Azure,
                                         konfiguracja Ollama itp.).

  **`frontend/`**                        Projekt Blazor WebAssembly --
                                         komponenty UI, logika
                                         komunikacji z API czatu.
  -----------------------------------------------------------------------

## Działanie aplikacji

1.  **Przyjęcie zapytania** -- `POST /chat` z JSON:

    ``` json
    { "session_id": "u1", "message": "jak zainstalować kip" }
    ```

2.  **Klasyfikacja intencji** -- `intents.py` rozpoznaje np. powitanie,
    pytanie o datę itp.

3.  **Retrieval** -- `retriever.py` wyszukuje najbardziej podobne
    dokumenty (embeddingi w Chroma).

4.  **Generacja odpowiedzi** -- `chain_chat.py` buduje kontekst i
    wywołuje LLM:

    -   Najpierw próbuje **Azure OpenAI**.
    -   Jeśli Azure jest niedostępny, przełącza się na **lokalny
        Ollama**.

5.  **Zwrot JSON** z polami:

    -   `answer` -- treść odpowiedzi,
    -   `intent` -- wykryta intencja,
    -   `sources` -- lista źródłowych artykułów,
    -   `engine` -- użyty silnik (`azure-openai`, `ollama`, `builtin`).

Frontend Blazor korzysta z endpointu `/chat` wyświetlając odpowiedzi w
przeglądarce w czasie rzeczywistym.

## Dane i indeks wektorowy

-   W bazie Chroma znajduje się **23 artykuły** pobrane ręcznie ze
    strony producenta oprogramowania **Symfonia ERP** (np. Kadry i
    Płace, eBiuro, KIP).
-   Artykuły zostały zindeksowane w Chroma z wykorzystaniem embeddingów
    (Azure OpenAI lub Ollama -- w zależności od konfiguracji).

## Przykładowe pytania

-   „Jak zainstalować KIP?"
-   „Kadry i Płace -- przydatne skróty klawiszowe"
-   „Jak wystawiać i wysyłać faktury w programie eBiuro?"
-   „Co to jest SSO?"

Przykład wywołania API:

``` bash
curl -X POST http://localhost:8000/chat      -H "Content-Type: application/json"      -d '{"session_id":"u1","message":"Jak zainstalować KIP"}'
```

Otrzymasz JSON z odpowiedzią, listą źródeł oraz informacją o użytym
silniku LLM.
