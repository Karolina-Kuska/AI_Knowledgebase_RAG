from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from src.rag.synonyms import expand as expand_synonyms
from typing import List, Dict, Any
import hashlib

def content_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def _alias_line(meta: dict) -> str:
    parts = []
    for key in ("title", "category", "product"):
        v = meta.get(key)
        if v:
            alts = expand_synonyms(v, title_hint=v)
            alts = [a for a in alts if len(a.split()) <= 5]
            parts.extend(alts[:8])
    if not parts:
        return ""
    return "\n\nAliasy / słowa kluczowe: " + ", ".join(sorted(set(parts)))

def to_documents(rows: List[Dict[str, Any]]) -> List[Document]:
    docs: List[Document] = []
    for r in rows:
        created_at = r.get("CreatedAt")
        updated_at = r.get("UpdatedAt")
        meta = {
            "source": r.get("Url") or f"db://Article/{r.get('Id')}",
            "title": r.get("Title"),
            "category": r.get("CategoryName"),
            "product": r.get("ProductName"),
            "product_group": r.get("ProductGroupName"),
            "id": r.get("Id"),
            "created_at": str(created_at) if created_at is not None else None,
            "updated_at": str(updated_at) if updated_at is not None else None,
        }
        alias = _alias_line(meta)
        text = f"{r.get('Title','')}\n\n{r.get('Content','')}"
        if alias:
            text += "\n\n" + alias
        docs.append(Document(page_content=text, metadata=meta))
    return docs

def split_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks: List[Document] = []
    for doc in docs:
        sub_docs = splitter.split_documents([doc])
        for idx, c in enumerate(sub_docs):
            h = content_hash(c.page_content)
            c.metadata["chunk_id"] = f"article:{c.metadata['id']}:chunk:{idx}:{h}"
            c.metadata["content_hash"] = h
            chunks.append(c)
    return chunks
