"""StudyAI — Database utility functions including SM-2 algorithm."""
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Concept, LearningEvent, Quiz, RevisionPlan, StudyMaterial


def get_weak_concepts(db: Session, user_id: str, threshold: float = 0.6) -> List[Concept]:
    """Return concepts below mastery threshold, ordered by next_review then mastery."""
    return (
        db.query(Concept)
        .filter(Concept.user_id == user_id, Concept.mastery_score < threshold)
        .order_by(Concept.next_review.asc(), Concept.mastery_score.asc())
        .all()
    )


def get_analytics_overview(db: Session, user_id: str) -> dict:
    """Aggregate stats for the user's analytics dashboard."""
    material_count = (
        db.query(func.count(StudyMaterial.id))
        .filter(StudyMaterial.user_id == user_id)
        .scalar() or 0
    )
    concept_count = (
        db.query(func.count(Concept.id))
        .filter(Concept.user_id == user_id)
        .scalar() or 0
    )
    quiz_count = (
        db.query(func.count(Quiz.id))
        .filter(Quiz.user_id == user_id, Quiz.taken_at.isnot(None))
        .scalar() or 0
    )
    avg_score_result = (
        db.query(func.avg(Quiz.score))
        .filter(Quiz.user_id == user_id, Quiz.score.isnot(None))
        .scalar()
    )
    avg_score = round(float(avg_score_result), 1) if avg_score_result else 0.0

    overall_mastery_result = (
        db.query(func.avg(Concept.mastery_score))
        .filter(Concept.user_id == user_id)
        .scalar()
    )
    overall_mastery = round(float(overall_mastery_result) * 100, 1) if overall_mastery_result else 0.0

    # Calculate streak: count consecutive days back from today with >= 1 event
    events = (
        db.query(func.date(LearningEvent.timestamp).label("day"))
        .filter(LearningEvent.user_id == user_id)
        .distinct()
        .order_by(func.date(LearningEvent.timestamp).desc())
        .all()
    )
    event_days = {str(e.day) for e in events}
    streak = 0
    check_day = datetime.utcnow().date()
    while str(check_day) in event_days:
        streak += 1
        check_day -= timedelta(days=1)

    return {
        "material_count": material_count,
        "concept_count": concept_count,
        "quiz_count": quiz_count,
        "avg_score": avg_score,
        "overall_mastery": overall_mastery,
        "study_streak_days": streak,
    }


def get_concepts_due_today(db: Session, user_id: str) -> List[Concept]:
    """Return concepts whose spaced-repetition review is due now or overdue."""
    return (
        db.query(Concept)
        .filter(Concept.user_id == user_id, Concept.next_review <= datetime.utcnow())
        .order_by(Concept.mastery_score.asc())
        .all()
    )


def get_quiz_history(db: Session, user_id: str, limit: int = 20) -> List[Quiz]:
    """Return recent quizzes for a user, most recent first."""
    return (
        db.query(Quiz)
        .filter(Quiz.user_id == user_id)
        .order_by(Quiz.created_at.desc())
        .limit(limit)
        .all()
    )


def get_concepts_by_material(db: Session, material_id: str) -> List[Concept]:
    """Return all concepts for a material ordered by mastery ascending."""
    return (
        db.query(Concept)
        .filter(Concept.material_id == material_id)
        .order_by(Concept.mastery_score.asc())
        .all()
    )


def update_concept_mastery(db: Session, concept_id: str, quality: int) -> Concept:
    """
    Apply the full SM-2 spaced repetition algorithm to a concept.

    quality: 0-5 rating of recall quality
      0-2 → failure (restart repetitions)
      3-5 → success (advance interval)
    """
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise ValueError(f"Concept {concept_id} not found")

    ef = concept.easiness_factor
    reps = concept.repetition_count
    interval = concept.interval_days

    if quality < 3:
        # Failed recall: restart repetition count, reset to 1-day interval
        reps = 0
        interval = 1
    else:
        # Successful recall: advance interval based on repetition count
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * ef)
        reps += 1

    # Update easiness factor (EF can never go below 1.3)
    ef = max(1.3, ef + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # Update mastery score from quality (0→0.0, 5→1.0)
    mastery = min(1.0, round(quality / 5.0, 2))

    # Synchronize mastery across all documents for this user
    # If I master "Backpropagation" in Material A, I master it in Material B too.
    all_same_concepts = db.query(Concept).filter(
        Concept.user_id == concept.user_id,
        func.lower(Concept.name) == func.lower(concept.name)
    ).all()

    for c in all_same_concepts:
        c.easiness_factor  = ef
        c.repetition_count = reps
        c.interval_days    = interval
        c.next_review      = datetime.utcnow() + timedelta(days=interval)
        c.mastery_score    = mastery
        c.updated_at       = datetime.utcnow()

    db.commit()
    db.refresh(concept)
    return concept
