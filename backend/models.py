"""SQLAlchemy models for ShinoGraph."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, Float, DateTime, Integer, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from backend.database import Base


def _uuid():
    return str(uuid.uuid4())


class Note(Base):
    __tablename__ = "notes"

    id = Column(Text, primary_key=True, default=_uuid)
    source_url = Column(Text)
    source_title = Column(Text)
    image_path = Column(Text)
    raw_text = Column(Text)
    summary = Column(Text)
    embedding = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    entities = relationship("Entity", secondary="note_entities", back_populates="notes")
    qa_pairs = relationship("QAPair", back_populates="note")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Text, primary_key=True, default=_uuid)
    name = Column(Text, unique=True, nullable=False)
    category = Column(Text)
    description = Column(Text)
    embedding = Column(LargeBinary, nullable=True)
    note_count = Column(Integer, default=1)

    notes = relationship("Note", secondary="note_entities", back_populates="entities")
    source_relations = relationship("Relation", foreign_keys="Relation.source_id", back_populates="source")
    target_relations = relationship("Relation", foreign_keys="Relation.target_id", back_populates="target")


class Relation(Base):
    __tablename__ = "relations"

    id = Column(Text, primary_key=True, default=_uuid)
    source_id = Column(Text, ForeignKey("entities.id"), nullable=False)
    target_id = Column(Text, ForeignKey("entities.id"), nullable=False)
    relation = Column(Text)  # contains / causes / contrasts / extends / similar
    strength = Column(Float, default=1.0)
    evidence = Column(Text)

    source = relationship("Entity", foreign_keys=[source_id], back_populates="source_relations")
    target = relationship("Entity", foreign_keys=[target_id], back_populates="target_relations")


class NoteEntity(Base):
    __tablename__ = "note_entities"

    note_id = Column(Text, ForeignKey("notes.id"), primary_key=True)
    entity_id = Column(Text, ForeignKey("entities.id"), primary_key=True)


class QAPair(Base):
    __tablename__ = "qa_pairs"

    id = Column(Text, primary_key=True, default=_uuid)
    note_id = Column(Text, ForeignKey("notes.id"))
    question = Column(Text)
    answer = Column(Text)
    next_review = Column(DateTime, nullable=True)
    ease_factor = Column(Float, default=2.5)

    note = relationship("Note", back_populates="qa_pairs")
