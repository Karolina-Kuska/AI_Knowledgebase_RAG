from src.ingest.sql_loader import fetch_articles
from src.ingest.chunker import to_documents, split_docs
from src.rag.vectorstore import get_chroma

def main():
    rows = list(fetch_articles())
    docs = to_documents(rows)
    chunks = split_docs(docs)

    vs = get_chroma()
    vs.add_documents(chunks)
 
    print(f"Ingest OK: {len(chunks)} chunks saved to Chroma.")

if __name__ == "__main__":
    main()
