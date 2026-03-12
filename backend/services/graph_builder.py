"""Knowledge graph construction and querying service."""

from sqlalchemy.orm import Session
from backend.models import Entity, Relation, Note, NoteEntity, QAPair


class GraphBuilder:
    def __init__(self, db: Session):
        self.db = db

    def ingest_parsed_note(self, note: Note, parsed: dict) -> None:
        """Take AI-parsed result and build/update knowledge graph."""
        # Upsert entities
        entity_map: dict[str, Entity] = {}
        for e in parsed.get("entities", []):
            existing = self.db.query(Entity).filter(Entity.name == e["name"]).first()
            if existing:
                existing.note_count += 1
                entity_map[e["name"]] = existing
            else:
                entity = Entity(
                    name=e["name"],
                    category=e.get("category", ""),
                    description=e.get("description", ""),
                )
                self.db.add(entity)
                self.db.flush()
                entity_map[e["name"]] = entity

        # Create note-entity links
        for name, entity in entity_map.items():
            link = self.db.query(NoteEntity).filter(
                NoteEntity.note_id == note.id,
                NoteEntity.entity_id == entity.id,
            ).first()
            if not link:
                self.db.add(NoteEntity(note_id=note.id, entity_id=entity.id))

        # Upsert relations
        for r in parsed.get("relations", []):
            src = entity_map.get(r["source"])
            tgt = entity_map.get(r["target"])
            if not src or not tgt:
                continue
            existing = self.db.query(Relation).filter(
                Relation.source_id == src.id,
                Relation.target_id == tgt.id,
                Relation.relation == r["relation"],
            ).first()
            if existing:
                existing.strength += 0.5
            else:
                self.db.add(Relation(
                    source_id=src.id,
                    target_id=tgt.id,
                    relation=r["relation"],
                    evidence=note.id,
                ))

        # Create QA pairs
        for qa in parsed.get("qa_pairs", []):
            self.db.add(QAPair(
                note_id=note.id,
                question=qa["question"],
                answer=qa["answer"],
            ))

        self.db.commit()

    def get_full_graph(self) -> dict:
        """Return the entire knowledge graph as nodes + edges."""
        entities = self.db.query(Entity).all()
        relations = self.db.query(Relation).all()
        return {
            "nodes": [
                {"id": e.id, "name": e.name, "category": e.category, "count": e.note_count}
                for e in entities
            ],
            "edges": [
                {
                    "source": r.source_id,
                    "target": r.target_id,
                    "relation": r.relation,
                    "strength": r.strength,
                }
                for r in relations
            ],
        }

    def get_related_entities(self, entity_id: str, depth: int = 2) -> list[dict]:
        """BFS traversal to find related entities up to given depth."""
        visited = set()
        queue = [(entity_id, 0)]
        results = []

        while queue:
            current_id, d = queue.pop(0)
            if current_id in visited or d > depth:
                continue
            visited.add(current_id)

            entity = self.db.query(Entity).filter(Entity.id == current_id).first()
            if entity:
                results.append({"id": entity.id, "name": entity.name, "depth": d})

            if d < depth:
                rels = self.db.query(Relation).filter(
                    (Relation.source_id == current_id) | (Relation.target_id == current_id)
                ).all()
                for rel in rels:
                    neighbor = rel.target_id if rel.source_id == current_id else rel.source_id
                    queue.append((neighbor, d + 1))

        return results
