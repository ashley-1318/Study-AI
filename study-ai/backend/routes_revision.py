"""StudyAI — Revision plan retrieval and completion routes."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from database import Concept, LearningEvent, RevisionPlan, User, get_db
from db_utils import get_concepts_due_today, get_weak_concepts, update_concept_mastery

router = APIRouter(tags=["revision"])


class CompleteRequest(BaseModel):
    concept_id: str
    quality:    int  # 0-5 SM-2 quality rating


class GeneratePlanRequest(BaseModel):
    strategy:           str = "balanced" # aggressive, balanced, light
    focus_material_ids: list[str] | None = None
    days_available:     int = 7


import os
import logging
from langchain_groq import ChatGroq

log = logging.getLogger(__name__)

_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
)

def generate_revision_tip(
    concept_name: str,
    definition: str,
    mastery_score: float,
    related_weak: list[str],
    review_chunks: list[str],
) -> str:
    """Generate specific actionable study tip using LLM."""
    return f"Re-read the definition of {concept_name} and practice one example from your notes."

@router.get("/revision/plan")
async def get_revision_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the user's revision plan and today's due concepts."""
    plan = db.query(RevisionPlan).filter(RevisionPlan.user_id == current_user.id).first()
    due_today = get_concepts_due_today(db, current_user.id)
    all_weak  = get_weak_concepts(db, current_user.id)
    
    schedule = plan.schedule if plan else {}
    weak_names = [c.name for c in all_weak[:5]]

    def _enrich(c, is_due=False):
        meta = schedule.get(c.id, {})
        chunks = meta.get("suggested_chunks", [])
        links  = meta.get("linked_concepts", [])
        
        tip = None
        if is_due:
            tip = generate_revision_tip(
                concept_name=c.name,
                definition=c.definition or "",
                mastery_score=c.mastery_score,
                related_weak=[w for w in weak_names if w != c.name],
                review_chunks=chunks
            )

        return {
            "id":            c.id,
            "name":          c.name,
            "mastery_score": c.mastery_score,
            "material_id":   c.material_id,
            "next_review":   c.next_review.isoformat() if c.next_review else None,
            "interval_days": c.interval_days,
            "filename":         meta.get("filename", "Unknown"),
            "suggested_chunks": chunks,
            "linked_concepts":  links,
            "scheduled_day":    meta.get("scheduled_day"),
            "ai_tip":           tip,
        }

    return {
        "success": True,
        "data": {
            "due_today": [_enrich(c, is_due=True) for c in due_today],
            "all_weak":  [_enrich(c) for c in all_weak],
        },
        "error": None,
    }


@router.post("/revision/generate")
async def generate_revision_plan(
    body: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Explicitly regenerate the revision plan with custom strategy.
    Adapts to current mastery and quiz history.
    """
    from revision_engine import generate_adaptive_plan
    
    schedule = await generate_adaptive_plan(
        db, 
        current_user.id, 
        strategy=body.strategy,
        focus_material_ids=body.focus_material_ids,
        days_available=body.days_available
    )
    
    return {
        "success": True,
        "data": {"planned_items": len(schedule), "schedule": schedule},
        "error": None
    }


@router.post("/revision/complete")
async def mark_complete(
    body: CompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a concept as reviewed with SM-2 quality score.
    Log a LearningEvent and return updated concept info.
    """
    if not 0 <= body.quality <= 5:
        raise HTTPException(400, "Quality must be 0-5")

    try:
        concept = update_concept_mastery(db, body.concept_id, body.quality)
    except ValueError as e:
        raise HTTPException(404, str(e))

    # Verify ownership
    if concept.user_id != current_user.id:
        raise HTTPException(403, "Not your concept")

    # Log revision event
    event = LearningEvent(
        user_id    = current_user.id,
        event_type = "revision",
        concept_id = body.concept_id,
        result     = {"quality": body.quality, "new_mastery": concept.mastery_score},
        timestamp  = datetime.utcnow(),
    )
    db.add(event)
    db.commit()

    return {
        "success": True,
        "data": {
            "concept_id":    concept.id,
            "name":          concept.name,
            "mastery_score": concept.mastery_score,
            "next_review":   concept.next_review.isoformat(),
            "interval_days": concept.interval_days,
        },
        "error": None,
    }
