"""StudyAI — Core engine for adaptive revision planning."""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Concept, RevisionPlan, StudyMaterial, LearningEvent
from tools.faiss_store import FAISSStore
from tools.embedder import generate_embedding
from db_utils import get_weak_concepts

log = logging.getLogger(__name__)

async def generate_adaptive_plan(
    db: Session,
    user_id: str,
    strategy: str = "balanced",
    focus_material_ids: list = None,
    days_available: int = 7
):
    """
    Core logic to build a day-by-day revision schedule.
    Adapts to mastery scores, recent quiz history, and user's strategy.
    
    Strategies:
    - 'aggressive': lower threshold for weak concepts, more items per day.
    - 'balanced': standard SM-2 intervals.
    - 'light': only most critical concepts, longer intervals.
    """
    # 1. Determine threshold based on strategy
    threshold = 0.6 # default balanced
    if strategy == "aggressive": threshold = 0.8
    if strategy == "light":      threshold = 0.4

    # 2. Get concepts (optionally filtered by material)
    query = db.query(Concept).filter(Concept.user_id == user_id)
    if focus_material_ids:
        query = query.filter(Concept.material_id.in_(focus_material_ids))
    
    all_concepts = query.all()
    # Prioritize: weak ones (threshold) + those due soon
    weak = [c for c in all_concepts if c.mastery_score < threshold or (c.next_review and c.next_review <= datetime.utcnow() + timedelta(days=days_available))]
    
    if not weak:
        return {}

    # Sort by urgency (mastery DESC, next_review ASC)
    weak.sort(key=lambda c: (c.mastery_score, c.next_review if c.next_review else datetime.utcnow()))

    # 3. RAG & Links (Intelligent Meta)
    store = FAISSStore(user_id)
    try:
        store.load()
    except:
        pass # fallback if search fails

    schedule = {}
    weak_names = {c.id: c.name for c in weak}

    for concept in weak[:50]: # Cap at 50 for performance
        suggested = []
        try:
            emb = generate_embedding(concept.name)
            results = store.search(query_embedding=emb, top_k=2)
            suggested = [r.get("chunk_text", "") for r in results if r.get("material_id") == concept.material_id]
            if not suggested: suggested = [r.get("chunk_text", "") for r in results[:2]]
        except:
            pass

        linked = []
        for w_id, w_name in weak_names.items():
            if w_id != concept.id and w_name.lower() in (concept.definition or "").lower():
                linked.append(w_name)

        mat = db.query(StudyMaterial).filter(StudyMaterial.id == concept.material_id).first()
        
        # Calculate a 'Day' for the study timeline
        # Distribute concepts over the 'days_available'
        # This is a simple distribution; we could be smarter based on mastery
        item_index = len(schedule)
        day_offset = item_index // max(1, (len(weak) // days_available))
        study_date = (datetime.utcnow().date() + timedelta(days=day_offset)).isoformat()

        schedule[concept.id] = {
            "name":             concept.name,
            "next_review":      concept.next_review.isoformat() if concept.next_review else datetime.utcnow().isoformat(),
            "mastery":          concept.mastery_score,
            "interval_days":    concept.interval_days,
            "filename":         mat.filename if mat else "Unknown",
            "suggested_chunks": suggested,
            "linked_concepts":  linked,
            "scheduled_day":    study_date,
            "strategy_used":    strategy
        }

    # 4. Persistence
    plan = db.query(RevisionPlan).filter(RevisionPlan.user_id == user_id).first()
    if plan:
        plan.concept_ids    = [c.id for c in weak]
        plan.schedule       = schedule
        plan.priority_score = round(1.0 - (sum(c.mastery_score for c in weak) / max(len(weak), 1)), 2)
        plan.updated_at     = datetime.utcnow()
    else:
        plan = RevisionPlan(
            user_id        = user_id,
            concept_ids    = [c.id for c in weak],
            schedule       = schedule,
            priority_score = round(1.0 - (sum(c.mastery_score for c in weak) / max(len(weak), 1)), 2),
        )
        db.add(plan)
    
    db.commit()
    return schedule
