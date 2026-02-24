"""StudyAI — Unified study history timeline API."""
from datetime import datetime
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from database import LearningEvent, User, get_db

router = APIRouter(tags=["history"])


@router.get("/history")
async def get_study_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return a unified, date-grouped timeline of all learning events.
    Events include uploads, quizzes, and revisions.
    """
    events = (
        db.query(LearningEvent)
        .filter(LearningEvent.user_id == current_user.id)
        .order_by(LearningEvent.timestamp.desc())
        .limit(100)
        .all()
    )

    # Group by date string (YYYY-MM-DD)
    timeline = defaultdict(list)
    for ev in events:
        date_str = ev.timestamp.strftime("%Y-%m-%d")
        
        # Format event data based on type
        event_data = {
            "id":         ev.id,
            "type":       ev.event_type,
            "timestamp":  ev.timestamp.isoformat(),
            "details":    ev.result or {},
        }
        
        # Add friendly descriptions
        if ev.event_type == "upload":
            filename = ev.result.get("filename", "document")
            event_data["description"] = f"Uploaded '{filename}'"
        elif ev.event_type == "quiz":
            score = ev.result.get("score", 0)
            event_data["description"] = f"Completed quiz with {score}% score"
        elif ev.event_type == "revision":
            # Attempt to get concept name if possible (would need a join or stored in result)
            # For now, use the result's quality
            quality = ev.result.get("quality", 0)
            event_data["description"] = f"Reviewed concept (Quality: {quality}/5)"
        else:
            event_data["description"] = f"Learned something new ({ev.event_type})"

        timeline[date_str].append(event_data)

    # Convert to list of objects: [{"date": "...", "events": [...]}, ...]
    formatted_timeline = []
    # Sort dates descending
    sorted_dates = sorted(timeline.keys(), reverse=True)
    
    for d in sorted_dates:
        formatted_timeline.append({
            "date":   d,
            "events": timeline[d]
        })

    return {
        "success": True,
        "data":    formatted_timeline,
        "error":   None,
    }
