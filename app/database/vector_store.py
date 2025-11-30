# app/database/vector_store.py

import os
from typing import List, Optional

import pandas as pd
from openai import OpenAI
from pinecone.grpc import PineconeGRPC as Pinecone

from app.config import (
    OPENAI_API_KEY,
    OPENAI_EMBED_MODEL,
    PINECONE_API_KEY,
    PINECONE_INDEX_HOST,
    PINECONE_INDEX_NAME,
    PINECONE_NAMESPACE,
)

# simple lazy objects so we don't reconnect again and again
_pinecone_client = None
_pinecone_index = None
_openai_client = None


def get_openai_client():
    """
    return openai client instance
    """
    global _openai_client
    if _openai_client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set")
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def get_pinecone_index():
    """
    connect to pinecone index using host
    """
    global _pinecone_client, _pinecone_index
    if _pinecone_index is None:
        if not PINECONE_API_KEY:
            raise RuntimeError("PINECONE_API_KEY not set")
        if not PINECONE_INDEX_HOST:
            raise RuntimeError("PINECONE_INDEX_HOST not set")

        _pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        _pinecone_index = _pinecone_client.Index(host=PINECONE_INDEX_HOST)

    return _pinecone_index


def _split_text_simple(text: str, max_chars: int = 1000) -> List[str]:
    """
    text splitter
    """
    text = (text or "").strip()
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end

    return chunks


def store_document_for_session(session_id: str, raw_text: str, doc_id: Optional[str] = None):
    """
    main entry point for now

    - take raw_text from pdf
    - split into chunks
    - create embeddings using openai
    - upsert into pinecone in single namespace

    metadata.session_id = session_id
    metadata.doc_id = doc_id or "default"
    """

    raw_text = (raw_text or "").strip()
    if not raw_text:
        print("[WARN] store_document_for_session got empty text")
        return

    chunks = _split_text_simple(raw_text, max_chars=1000)
    if not chunks:
        print("[WARN] no chunks generated from text")
        return

    # fallback doc id if not provided
    if not doc_id:
        doc_id = "default"

    client = get_openai_client()
    index = get_pinecone_index()

    print(f"[EMBED] creating embeddings for {len(chunks)} chunks, session={session_id}, doc={doc_id}")

    resp = client.embeddings.create(
        model=OPENAI_EMBED_MODEL,
        input=chunks,
    )

    vectors = []
    for i, data in enumerate(resp.data):
        embedding = data.embedding
        vector_id = f"{session_id}-{doc_id}-chunk-{i}"

        metadata = {
            "session_id": session_id,
            "doc_id": doc_id,
            "chunk_index": i,
        }

        vectors.append((vector_id, embedding, metadata))

    print(
        f"[PINECONE] upserting {len(vectors)} vectors "
        f"into index={PINECONE_INDEX_NAME}, namespace={PINECONE_NAMESPACE}"
    )

    index.upsert(
        vectors=vectors,
        namespace=PINECONE_NAMESPACE,
    )

    print("[OK] document stored in vector index for session:", session_id)


def delete_vectors_for_session(session_id: str):
    """
    helper to delete all vectors belonging to a session
    """
    index = get_pinecone_index()

    print(
        f"[PINECONE] deleting vectors for session={session_id} "
        f"in namespace={PINECONE_NAMESPACE}"
    )

    index.delete(
        filter={"session_id": session_id},
        namespace=PINECONE_NAMESPACE,
    )

    print("[OK] deleted vectors for session:", session_id)
