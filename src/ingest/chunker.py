from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List, Dict, Any

def to_documents(rows: List[Dict[str, Any]]) -> List[Document]:
    docs = []
    for r in rows:
        text = f"{r.get('Title','')}\n\n{r.get('Body','')}"
        meta = {
            "source": r.get("Url") or f"db://Articles/{r.get('Id')}",
            "title": r.get("Title"),
            "category": r.get("Category"),
            "id": r.get("Id"),
            "updated_at": str(r.get("UpdatedAt")) if r.get("UpdatedAt") else None,
        }
        docs.append(Document(page_content=text, metadata=meta))
    return docs

def split_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)
