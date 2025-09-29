
from src.ingest.sql_loader import fetch_articles_since
from src.ingest.chunker import to_documents, split_docs
from src.rag.vectorstore import get_chroma

def main():

    rows = list(fetch_articles_since(None))
    if not rows:
        print("Brak danych do zindeksowania.")
        return

    docs = to_documents(rows)
    chunks = split_docs(docs)

    vs = get_chroma()

    try:
        vs.add_documents(chunks, ids=[c.metadata["chunk_id"] for c in chunks])
    except KeyError:
        vs.add_documents(chunks)

    print(f"Ingest OK: {len(chunks)} chunks zapisane do Chroma.")

if __name__ == "__main__":
    main()
