"""StudyAI — Analytics agent node: finalize processing and log events."""
from datetime import datetime


async def analytics_node(state: dict) -> dict:
    """
    Compute final mastery analytics, mark material as 'done',
    and log a LearningEvent for this upload session.
    """
    user_id     = state.get("user_id")
    material_id = state.get("material_id")
    db          = state.get("db")
    concepts    = state.get("concepts", [])

    if not db:
        state["analytics"] = {}
        return state

    await _push(state, "analytics", "running", "Finalizing analytics…")

    from database import Concept, LearningEvent, StudyMaterial

    # Count mastery tiers from DB
    all_concepts = db.query(Concept).filter(Concept.user_id == user_id).all()
    total = len(all_concepts) or 1
    mastered = sum(1 for c in all_concepts if c.mastery_score >= 0.7)
    learning = sum(1 for c in all_concepts if 0.4 <= c.mastery_score < 0.7)
    weak     = sum(1 for c in all_concepts if c.mastery_score < 0.4)
    overall  = round(sum(c.mastery_score for c in all_concepts) / total, 2)

    analytics = {
        "mastered": mastered,
        "learning": learning,
        "weak":     weak,
        "overall":  overall,
        "total":    total,
    }

    # Mark material as done
    if material_id:
        mat = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
        if mat:
            mat.status     = "done"
            mat.updated_at = datetime.utcnow()

    # Log upload event
    event = LearningEvent(
        user_id    = user_id,
        event_type = "upload",
        result     = {
            "material_id": material_id,
            "concepts":    len(concepts),
            "analytics":   analytics,
        },
        timestamp  = datetime.utcnow(),
    )
    db.add(event)
    db.commit()

    state["analytics"] = analytics
    await _push(state, "analytics", "done", "✅ Processing complete!")
    return state


async def _push(state: dict, step: str, status: str, message: str):
    q = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})
