# src/rag/retriever.py
from typing import List, Optional, Tuple
from langchain.schema import Document
from src.rag.vectorstore import get_chroma
from src.rag.synonyms import expand as expand_synonyms

def retrieve(question: str, k: int = 5,
             category: Optional[str] = None,
             product: Optional[str] = None) -> List[Document]:
    vs = get_chroma()
    where = {}
    if category: where["category"] = category
    if product:  where["product"]  = product

    queries = expand_synonyms(question)
    pool: list[Tuple[str, dict, float]] = []
    seen = set()

    for q in queries:
        res = vs._collection.query(
            query_texts=[q],
            n_results=30,  # większy koszyk
            where=(where or None),
            include=["documents","metadatas","distances"]
        )
        docs  = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for doc, meta, dist in zip(docs, metas, dists):
            cid = meta.get("chunk_id") or (meta.get("id"), meta.get("title"), meta.get("source"))
            if cid in seen:
                continue
            seen.add(cid)
            pool.append((doc, meta, dist if dist is not None else 0.0))

    if not pool:
        return []


    THRESH = 0.40
    pool = [t for t in pool if t[2] <= THRESH]
    pool.sort(key=lambda x: x[2])
    pool = pool[:max(k, 20)]  

    return [Document(page_content=d, metadata=m) for d, m, _ in pool]
