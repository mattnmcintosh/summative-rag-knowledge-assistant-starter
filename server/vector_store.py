from typing import Any, List

import chromadb
import requests

from config import Config
from documents import DocumentChunk


def get_chroma_client():
    """
    Create and return a persistent Chroma client.
    """
    return chromadb.PersistentClient(path=Config.CHROMA_PATH)


def get_or_create_collection():
    """
    Get or create the Chroma collection for the knowledge assistant.
    """
    client = get_chroma_client()
    return client.get_or_create_collection(name=Config.COLLECTION_NAME)


def get_embedding(text: str) -> list[float]:
    """
    Create an embedding for a piece of text using the local model service.
    """
    url = f"{Config.OLLAMA_BASE_URL.rstrip('/')}/api/embeddings"
    payload = {
        "model": Config.EMBEDDING_MODEL,
        "prompt": text
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [])
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch embedding from Ollama: {e}")


def seed_vector_store(chunks: List[DocumentChunk]) -> int:
    """
    Add document chunks to the Chroma collection.
    """
    collection = get_or_create_collection()
    
    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for chunk in chunks:

        chunk_id = f"{chunk.source}_{chunk.chunk_index}"
        
        embedding = get_embedding(chunk.text)

        ids.append(chunk_id)
        documents.append(chunk.text)
        metadatas.append({
            "source": chunk.source,
            "title": chunk.title,
            "chunk_index": chunk.chunk_index
        })
        embeddings.append(embedding)

    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    return len(chunks)


def retrieve_relevant_chunks(question: str, top_k: int | None = None) -> list[dict[str, Any]]:
    """
    Retrieve relevant chunks for a user question.
    """
    if top_k is None:
        top_k = getattr(Config, "TOP_K", 3)

    collection = get_or_create_collection()
    question_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    formatted_chunks = []
    
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if "distances" in results else [None] * len(documents)

    for doc, meta, dist in zip(documents, metadatas, distances):
        chunk_data = {
            "text": doc,
            "source": meta.get("source", ""),
            "title": meta.get("title", ""),
            "chunk_index": meta.get("chunk_index", 0)
        }
        if dist is not None:
            chunk_data["distance"] = dist
            
        formatted_chunks.append(chunk_data)

    return formatted_chunks
