"""StudyAI — Revision planner agent node using SM-2."""
from datetime import datetime, timedelta


async def revision_node(state: dict) -> dict:
    """
    Build a spaced-repetition revision plan for the user's weak concepts.
    Upserts the RevisionPlan row and schedules next_review dates via SM-2.
    """
    user_id = state.get("user_id")
    db      = state.get("db")

    if not db or not user_id:
        state["revision"] = {}
        return state

    await _push(state, "revision", "running", "Building revision plan…")

    await _push(state, "revision", "running", "Building revision plan…")

    from revision_engine import generate_adaptive_plan
    schedule = await generate_adaptive_plan(db, user_id)

    state["revision"] = schedule
    await _push(state, "revision", "done", f"Planned {len(schedule)} concepts for review")
    return state


async def _push(state: dict, step: str, status: str, message: str):
    q = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})
