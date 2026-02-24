"""StudyAI — Concept listing and semantic search routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import Concept, User, get_db

router = APIRouter(tags=["concepts"])


@router.get("/concepts/")
async def list_concepts(
    material_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all concepts for the user, optionally filtered by material."""
    q = db.query(Concept).filter(Concept.user_id == current_user.id)
    if material_id:
        q = q.filter(Concept.material_id == material_id)
    concepts = q.order_by(Concept.mastery_score.asc()).all()

    return {
        "success": True,
        "data": [
            {
                "id":               c.id,
                "name":             c.name,
                "definition":       c.definition,
                "mastery_score":    c.mastery_score,
                "related_concepts": c.related_concepts or [],
                "next_review":      c.next_review.isoformat() if c.next_review else None,
                "material_id":      c.material_id,
            }
            for c in concepts
        ],
        "error": None,
    }


@router.get("/concepts/related")
async def related_concepts(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Semantic search: embed the query and find top-5 similar chunks
    from the user's FAISS index.
    """
    from tools.embedder import generate_embedding
    from tools.faiss_store import FAISSStore

    embedding = generate_embedding(query)
    store = FAISSStore(current_user.id)
    store.load()
    results = store.search(embedding, top_k=5)

    return {
        "success": True,
        "data": [
            {
                "chunk_text":   r.get("chunk_text", "")[:500],
                "material_id":  r.get("material_id"),
                "score":        round(r.get("score", 0.0), 3),
                "chunk_index":  r.get("chunk_index"),
            }
            for r in results
        ],
        "error": None,
    }


@router.get("/concepts/{concept_id}")
async def get_concept(
    concept_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a single concept with its related concepts list."""
    concept = db.query(Concept).filter(
        Concept.id      == concept_id,
        Concept.user_id == current_user.id,
    ).first()
    if not concept:
        raise HTTPException(404, "Concept not found")

    return {
        "success": True,
        "data": {
            "id":               concept.id,
            "name":             concept.name,
            "definition":       concept.definition,
            "mastery_score":    concept.mastery_score,
            "related_concepts": concept.related_concepts or [],
            "easiness_factor":  concept.easiness_factor,
            "interval_days":    concept.interval_days,
            "next_review":      concept.next_review.isoformat() if concept.next_review else None,
            "material_id":      concept.material_id,
        },
        "error": None,
    }
