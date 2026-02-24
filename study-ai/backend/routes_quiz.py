"""StudyAI — Quiz generation and submission routes."""
from datetime import datetime
from difflib import SequenceMatcher

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from database import (
    Concept, LearningEvent, Quiz, QuizAnswer,
    StudyMaterial, User, get_db,
)
from db_utils import get_quiz_history, get_weak_concepts, update_concept_mastery

router = APIRouter(tags=["quiz"])


class GenerateRequest(BaseModel):
    material_id:    str | None = None
    difficulty:     str = "adaptive"
    question_count: int = 10


class AnswerItem(BaseModel):
    question_index: int
    answer:         str


class SubmitRequest(BaseModel):
    answers: list[AnswerItem]


@router.post("/quiz/generate")
async def generate_quiz(
    body: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a quiz prioritizing weak concepts.
    Returns questions without answer/explanation fields.
    """
    from tools.quiz_tool import generate_questions

    # Select concepts: weak first, then all from material
    if body.material_id:
        concepts = db.query(Concept).filter(
            Concept.material_id == body.material_id,
            Concept.user_id     == current_user.id,
        ).order_by(Concept.mastery_score.asc()).limit(body.question_count // 2 + 2).all()
    else:
        concepts = get_weak_concepts(db, current_user.id)[:body.question_count // 2 + 2]

    if not concepts:
        raise HTTPException(400, "No concepts available to generate a quiz")

    all_questions = []
    per_concept = max(1, body.question_count // max(len(concepts), 1))

    for concept in concepts:
        qs = await generate_questions(
            concept_name = concept.name,
            concept_def  = concept.definition or "",
            difficulty   = body.difficulty,
            count        = per_concept,
        )
        # Tag each question with concept_id
        for q in qs:
            q["concept_id"] = concept.id
        all_questions.extend(qs)

    all_questions = all_questions[:body.question_count]

    # Persist quiz with full data (including answers) server-side
    quiz = Quiz(
        user_id     = current_user.id,
        material_id = body.material_id,
        questions   = all_questions,
        difficulty  = body.difficulty,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return {
        "success": True,
        "data": {"quiz_id": quiz.id, "questions": all_questions},
        "error": None,
    }


@router.post("/quiz/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: str,
    body: SubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Grade submitted answers, update SM-2 mastery, log events.
    Returns per-question breakdown with explanations.
    """
    quiz = db.query(Quiz).filter(
        Quiz.id      == quiz_id,
        Quiz.user_id == current_user.id,
    ).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")

    questions = quiz.questions or []
    answers_map = {a.question_index: a.answer for a in body.answers}

    correct_count = 0
    breakdown = []

    for i, q in enumerate(questions):
        user_ans  = answers_map.get(i, "").strip().lower()
        correct_ans = str(q.get("answer", "")).strip().lower()
        q_type    = q.get("type", "mcq")

        # Grade
        if q_type == "fillblank":
            # Fuzzy match with 85% threshold
            ratio = SequenceMatcher(None, user_ans, correct_ans).ratio()
            is_correct = ratio >= 0.85
        else:
            is_correct = user_ans == correct_ans

        if is_correct:
            correct_count += 1

        quality = 5 if is_correct else 2
        concept_id = q.get("concept_id")

        # Update mastery via SM-2
        if concept_id:
            try:
                update_concept_mastery(db, concept_id, quality)
            except ValueError:
                pass  # concept may have been deleted

        # Save QuizAnswer
        qa = QuizAnswer(
            quiz_id     = quiz_id,
            concept_id  = concept_id,
            question    = q.get("question", ""),
            user_answer = answers_map.get(i, ""),
            correct     = is_correct,
            answered_at = datetime.utcnow(),
        )
        db.add(qa)

        breakdown.append({
            "index":       i,
            "question":    q.get("question"),
            "user_answer": answers_map.get(i, ""),
            "correct_ans": q.get("answer"),
            "is_correct":  is_correct,
            "explanation": q.get("explanation", ""),
            "concept":     q.get("concept", ""),
        })

    score = round((correct_count / max(len(questions), 1)) * 100, 1)

    # Update quiz record
    quiz.score    = score
    quiz.taken_at = datetime.utcnow()
    db.commit()

    # Log learning event
    event = LearningEvent(
        user_id    = current_user.id,
        event_type = "quiz",
        result     = {"quiz_id": quiz_id, "score": score, "correct": correct_count, "total": len(questions)},
        timestamp  = datetime.utcnow(),
    )
    db.add(event)
    db.commit()

    return {
        "success": True,
        "data": {
            "score":     score,
            "correct":   correct_count,
            "total":     len(questions),
            "breakdown": breakdown,
        },
        "error": None,
    }


@router.get("/quiz/history")
async def quiz_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return last 20 quizzes for the current user."""
    quizzes = get_quiz_history(db, current_user.id)
    result = []
    for q in quizzes:
        mat_name = None
        if q.material_id:
            mat = db.query(StudyMaterial).filter(StudyMaterial.id == q.material_id).first()
            mat_name = mat.filename if mat else None
        result.append({
            "id":            q.id,
            "difficulty":    q.difficulty,
            "score":         q.score,
            "taken_at":      q.taken_at.isoformat() if q.taken_at else None,
            "created_at":    q.created_at.isoformat() if q.created_at else None,
            "material_name": mat_name,
            "question_count": len(q.questions or []),
        })

    return {"success": True, "data": result, "error": None}
