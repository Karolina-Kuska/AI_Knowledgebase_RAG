from langchain.schema.document import Document
from typing import List
from src.rag.vectorstore import get_chroma

def retrieve(question: str, k: int = 5) -> List[Document]:
    vs = get_chroma()
    return vs.similarity_search(question, k=k)
