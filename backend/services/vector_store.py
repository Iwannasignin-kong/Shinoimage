"""Vector store service using ChromaDB for semantic search."""

import chromadb
from chromadb.config import Settings


class VectorStore:
    def __init__(self, persist_dir: str = "./chroma_data"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False,
        ))
        self.notes_collection = self.client.get_or_create_collection(
            name="notes",
            metadata={"hnsw:space": "cosine"},
        )
        self.entities_collection = self.client.get_or_create_collection(
            name="entities",
            metadata={"hnsw:space": "cosine"},
        )

    def add_note(self, note_id: str, text: str, metadata: dict | None = None):
        self.notes_collection.upsert(
            ids=[note_id],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def add_entity(self, entity_id: str, text: str, metadata: dict | None = None):
        self.entities_collection.upsert(
            ids=[entity_id],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def search_notes(self, query: str, n_results: int = 5) -> list[dict]:
        results = self.notes_collection.query(query_texts=[query], n_results=n_results)
        return [
            {"id": id_, "text": doc, "distance": dist}
            for id_, doc, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
            )
        ]

    def search_entities(self, query: str, n_results: int = 5) -> list[dict]:
        results = self.entities_collection.query(query_texts=[query], n_results=n_results)
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
        results = self.entities_collection.query(
            query_texts=[entity_text], n_results=3
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
