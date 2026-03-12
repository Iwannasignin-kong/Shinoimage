"""Chat / Q&A endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Note, Entity
from backend.services.ai_parser import AIParser
from backend.services.vector_store import VectorStore

router = APIRouter()
ai = AIParser()
vectors = VectorStore()


class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Answer a question using knowledge graph context."""
    # 1. Vector search for relevant notes
    relevant = vectors.search_notes(req.question, n_results=5)

    # 2. Fetch full note data
    note_ids = [r["id"] for r in relevant]
    notes = db.query(Note).filter(Note.id.in_(note_ids)).all()

    # 3. Build context
    context_parts = []
    for note in notes:
        context_parts.append(f"【笔记】{note.summary}\n{note.raw_text}")

    # 4. Also find relevant entities
    entity_results = vectors.search_entities(req.question, n_results=3)
    entity_ids = [e["id"] for e in entity_results]
    entities = db.query(Entity).filter(Entity.id.in_(entity_ids)).all()
    for entity in entities:
        context_parts.append(f"【概念】{entity.name}: {entity.description}")

    context = "\n\n".join(context_parts) if context_parts else "知识库中暂无相关内容。"

    # 5. AI answer
    answer = ai.chat_with_context(req.question, context)

    return {
        "answer": answer,
        "sources": [{"id": n.id, "summary": n.summary} for n in notes],
    }
