# src/rag/retriever.py
from typing import List, Optional, Set
from langchain.schema import Document
from src.rag.vectorstore import get_chroma
from src.rag.synonyms import expand as expand_synonyms


def retrieve(
    question: str,
    k: int = 5,
    category: Optional[str] = None,
    product: Optional[str] = None
) -> List[Document]:
    vs = get_chroma()
    queries = expand_synonyms(question)

    results: List[Document] = []
    seen: Set[str] = set()

    for q in queries:
        docs = vs.similarity_search(q, k=max(k, 20))
        for d in docs:
            # proste filtry meta
            if category and d.metadata.get("category") != category:
                continue
            if product and d.metadata.get("product") != product:
                continue
            cid = d.metadata.get("chunk_id") or d.metadata.get("id")
            if cid in seen:
                continue
            seen.add(cid)
            results.append(d)


    THRESH = 0.40
    filtered = []
    for d in results:
        dist = d.metadata.get("distance") or d.metadata.get("score")
        if dist is None or dist <= THRESH:
            filtered.append(d)


    filtered.sort(key=lambda x: x.metadata.get("distance", 0.0))
    return filtered[:k]
