"""Vector store service using ChromaDB for semantic search."""

import logging
import chromadb

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, persist_dir: str = "./chroma_data"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.notes_collection = self.client.get_or_create_collection(
            name="notes",
            metadata={"hnsw:space": "cosine"},
        )
        self.entities_collection = self.client.get_or_create_collection(
            name="entities",
            metadata={"hnsw:space": "cosine"},
        )

    def add_note(self, note_id: str, text: str, metadata: dict | None = None):
        if not text or not text.strip():
            return
        self.notes_collection.upsert(
            ids=[note_id],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def add_entity(self, entity_id: str, text: str, metadata: dict | None = None):
        if not text or not text.strip():
            return
        self.entities_collection.upsert(
            ids=[entity_id],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def search_notes(self, query: str, n_results: int = 5) -> list[dict]:
        if self.notes_collection.count() == 0:
            return []
        n = min(n_results, self.notes_collection.count())
        results = self.notes_collection.query(query_texts=[query], n_results=n)
        return [
            {"id": id_, "text": doc, "distance": dist}
            for id_, doc, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
            )
        ]

    def search_entities(self, query: str, n_results: int = 5) -> list[dict]:
        if self.entities_collection.count() == 0:
            return []
        n = min(n_results, self.entities_collection.count())
        results = self.entities_collection.query(query_texts=[query], n_results=n)
        return [
            {"id": id_, "text": doc, "distance": dist}
            for id_, doc, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
            )
        ]

    def find_similar_entities(self, entity_text: str, threshold: float = 0.3) -> list[dict]:
        """Find entities similar to given text, for deduplication."""
        if self.entities_collection.count() == 0:
            return []
        n = min(3, self.entities_collection.count())
        results = self.entities_collection.query(
            query_texts=[entity_text], n_results=n
        )
        return [
            {"id": id_, "text": doc, "distance": dist}
            for id_, doc, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
            )
            if dist <= threshold
        ]
