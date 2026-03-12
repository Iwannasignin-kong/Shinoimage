"""Knowledge graph query endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.graph_builder import GraphBuilder

router = APIRouter()


@router.get("/")
def get_graph(db: Session = Depends(get_db)):
    """Return full knowledge graph for visualization."""
    builder = GraphBuilder(db)
    return builder.get_full_graph()


@router.get("/entity/{entity_id}/related")
def get_related(entity_id: str, depth: int = 2, db: Session = Depends(get_db)):
    """Get entities related to a given entity within N hops."""
    builder = GraphBuilder(db)
    return builder.get_related_entities(entity_id, depth)
