"""Notes CRUD endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Note, QAPair, Entity
from backend.services.ai_parser import AIParser
from backend.services.graph_builder import GraphBuilder
from backend.services.vector_store import VectorStore

logger = logging.getLogger(__name__)
router = APIRouter()

# Lazy singletons — initialized on first request, not at import time
_ai: AIParser | None = None
_vectors: VectorStore | None = None


def get_ai() -> AIParser:
    global _ai
    if _ai is None:
        _ai = AIParser()
    return _ai


def get_vectors() -> VectorStore:
    global _vectors
    if _vectors is None:
        _vectors = VectorStore()
    return _vectors


@router.post("/capture")
async def capture_note(
    image: UploadFile = File(None),
    text: str = Form(None),
    source_url: str = Form(""),
    source_title: str = Form(""),
    db: Session = Depends(get_db),
):
    """Capture a note from screenshot or selected text."""
    ai = get_ai()
    vectors = get_vectors()

    # Parse via AI
    if image:
        image_data = await image.read()
        parsed = ai.parse_image(image_data, media_type=image.content_type or "image/png")
    elif text:
        parsed = ai.parse_text(text)
    else:
        raise HTTPException(status_code=400, detail="Provide either image or text")

    # Create note
    note = Note(
        source_url=source_url,
        source_title=source_title,
        raw_text=parsed.get("raw_text", text or ""),
        summary=parsed.get("summary", ""),
    )
    db.add(note)
    db.flush()

    # Build knowledge graph (this also calls db.commit())
    builder = GraphBuilder(db)
    builder.ingest_parsed_note(note, parsed)

    # Index in vector store
    vectors.add_note(note.id, note.raw_text, {"source_url": source_url})
    for ent in parsed.get("entities", []):
        name = ent.get("name", "")
        desc = ent.get("description", "")
        if name:
            db_entity = db.query(Entity).filter(Entity.name == name).first()
            if db_entity:
                vectors.add_entity(db_entity.id, f"{name}: {desc}", {"category": ent.get("category", "")})

    return {
        "id": note.id,
        "summary": note.summary,
        "entities": parsed.get("entities", []),
        "qa_count": len(parsed.get("qa_pairs", [])),
    }


@router.get("/")
def list_notes(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    notes = db.query(Note).order_by(Note.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {"id": n.id, "summary": n.summary, "source_title": n.source_title, "created_at": str(n.created_at)}
        for n in notes
    ]


@router.get("/{note_id}")
def get_note(note_id: str, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "id": note.id,
        "raw_text": note.raw_text,
        "summary": note.summary,
        "source_url": note.source_url,
        "source_title": note.source_title,
        "created_at": str(note.created_at),
    }


@router.get("/{note_id}/qa")
def get_qa_pairs(note_id: str, db: Session = Depends(get_db)):
    pairs = db.query(QAPair).filter(QAPair.note_id == note_id).all()
    return [{"id": p.id, "question": p.question, "answer": p.answer} for p in pairs]
