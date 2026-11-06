"""Build/refresh the persistent Chroma index from menu and curated documents.

Run from the repository root with: python -m rag.ingest
"""

from __future__ import annotations

import hashlib
import os

from rag.chatbot import COLLECTION_NAME, VECTOR_STORE_DIR, _load_documents


def rebuild_index() -> int:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY in the process environment before indexing.")

    try:
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
    except ImportError as error:
        raise RuntimeError(
            "RAG dependencies are missing. Install the project requirements first."
        ) from error

    records = _load_documents()
    if not records:
        raise RuntimeError("There are no menu or knowledge documents to index.")

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001"),
        google_api_key=api_key,
    )

    store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_STORE_DIR),
        embedding_function=embeddings,
    )
    try:
        store.delete_collection()
    except Exception:
        # A first-time build has no collection to remove.
        pass

    store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_STORE_DIR),
        embedding_function=embeddings,
    )
    langchain_documents = [
        Document(page_content=record["page_content"], metadata=record["metadata"])
        for record in records
    ]
    document_ids = [
        hashlib.sha256(
            (record["metadata"].get("source", "") + record["page_content"]).encode("utf-8")
        ).hexdigest()
        for record in records
    ]
    store.add_documents(langchain_documents, ids=document_ids)
    return len(langchain_documents)


if __name__ == "__main__":
    count = rebuild_index()
    print(f"Indexed {count} NutriOrder document chunks into {VECTOR_STORE_DIR}.")
