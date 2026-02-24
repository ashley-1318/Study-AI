"""StudyAI seed data — run once to populate the dev database."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from database import (
    SessionLocal, init_db,
    User, StudyMaterial, Concept, Quiz, QuizAnswer, RevisionPlan, LearningEvent,
)
import uuid


def seed():
    init_db()
    db = SessionLocal()
    try:
        # ── User ────────────────────────────────────────────────────
        user = User(
            id         = str(uuid.uuid4()),
            google_id  = "google-sub-studyai-001",
            email      = "test@studyai.dev",
            name       = "Alex Learner",
            avatar_url = "https://i.pravatar.cc/150?u=studyai",
            created_at = datetime.utcnow(),
            last_login = datetime.utcnow(),
        )
        db.add(user)
        db.flush()

        # ── Study Materials ─────────────────────────────────────────
        mat1 = StudyMaterial(
            id           = str(uuid.uuid4()),
            user_id      = user.id,
            filename     = "intro_machine_learning.pdf",
            status       = "done",
            chunk_count  = 24,
            summary      = (
                "## Machine Learning Fundamentals\n\n"
                "### Overview\nMachine learning enables systems to learn from data.\n\n"
                "### Key Topics\n- Supervised vs unsupervised learning\n"
                "- Model evaluation (precision, recall, F1)\n"
                "- Overfitting and regularization\n\n"
                "### Key Concepts\n- **Gradient Descent**: Iterative optimization algorithm\n"
                "- **Overfitting**: Model too closely fits training data\n"
                "- **Supervised Learning**: Learning with labeled data"
            ),
            created_at = datetime.utcnow() - timedelta(days=5),
        )
        mat2 = StudyMaterial(
            id           = str(uuid.uuid4()),
            user_id      = user.id,
            filename     = "deep_learning_fundamentals.pdf",
            status       = "done",
            chunk_count  = 31,
            summary      = (
                "## Deep Learning Overview\n\n"
                "### Neural Network Architecture\nLayers of interconnected neurons learn representations.\n\n"
                "### Training\n- Forward pass computes activations\n"
                "- Backpropagation computes gradients\n"
                "- Optimizer updates weights\n\n"
                "### Key Concepts\n- **Neural Networks**: Layered function approximators\n"
                "- **Backpropagation**: Gradient chain rule through layers\n"
                "- **Regularization**: Dropout, weight decay"
            ),
            created_at = datetime.utcnow() - timedelta(days=2),
        )
        db.add(mat1)
        db.add(mat2)
        db.flush()

        # ── Concepts ────────────────────────────────────────────────
        concepts_data = [
            dict(name="Supervised Learning",  mastery=0.80, mat=mat1, related=["Gradient Descent", "Overfitting"]),
            dict(name="Neural Networks",       mastery=0.50, mat=mat2, related=["Backpropagation"]),
            dict(name="Gradient Descent",      mastery=0.30, mat=mat1, related=["Supervised Learning", "Backpropagation"]),
            dict(name="Backpropagation",       mastery=0.20, mat=mat2, related=["Neural Networks", "Gradient Descent"]),
            dict(name="Overfitting",           mastery=0.65, mat=mat1, related=["Supervised Learning"]),
        ]
        concept_objs = []
        for cd in concepts_data:
            c = Concept(
                id               = str(uuid.uuid4()),
                material_id      = cd["mat"].id,
                user_id          = user.id,
                name             = cd["name"],
                definition       = f"Core concept: {cd['name']} in machine learning and deep learning.",
                mastery_score    = cd["mastery"],
                related_concepts = cd["related"],
                easiness_factor  = 2.5,
                repetition_count = 1 if cd["mastery"] > 0.5 else 0,
                interval_days    = 6 if cd["mastery"] > 0.5 else 1,
                next_review      = datetime.utcnow() + timedelta(days=1 if cd["mastery"] < 0.5 else 7),
                created_at       = datetime.utcnow() - timedelta(days=3),
            )
            db.add(c)
            concept_objs.append(c)
        db.flush()

        # ── Quizzes ─────────────────────────────────────────────────
        quiz1 = Quiz(
            id          = str(uuid.uuid4()),
            user_id     = user.id,
            material_id = mat1.id,
            difficulty  = "medium",
            score       = 72.0,
            taken_at    = datetime.utcnow() - timedelta(days=3),
            created_at  = datetime.utcnow() - timedelta(days=3),
            questions   = [
                {
                    "type": "mcq",
                    "question": "What is the purpose of gradient descent?",
                    "options": ["Increase the loss", "Minimize the loss", "Overfit the model", "Normalize inputs"],
                    "answer": "Minimize the loss",
                    "explanation": "Gradient descent iteratively adjusts weights to minimize the loss function.",
                    "concept": "Gradient Descent",
                }
            ],
        )
        quiz2 = Quiz(
            id          = str(uuid.uuid4()),
            user_id     = user.id,
            material_id = mat2.id,
            difficulty  = "adaptive",
            score       = None,
            taken_at    = None,
            created_at  = datetime.utcnow() - timedelta(days=1),
            questions   = [],
        )
        db.add(quiz1)
        db.add(quiz2)
        db.flush()

        # ── QuizAnswers for Quiz 1 ───────────────────────────────────
        qa1 = QuizAnswer(
            id          = str(uuid.uuid4()),
            quiz_id     = quiz1.id,
            concept_id  = concept_objs[2].id,  # Gradient Descent
            question    = "What is the purpose of gradient descent?",
            user_answer = "Minimize the loss",
            correct     = True,
            answered_at = datetime.utcnow() - timedelta(days=3),
        )
        qa2 = QuizAnswer(
            id          = str(uuid.uuid4()),
            quiz_id     = quiz1.id,
            concept_id  = concept_objs[0].id,  # Supervised Learning
            question    = "Which type of learning uses labeled data?",
            user_answer = "Reinforcement learning",
            correct     = False,
            answered_at = datetime.utcnow() - timedelta(days=3),
        )
        db.add(qa1)
        db.add(qa2)

        # ── Revision Plan ────────────────────────────────────────────
        weak_concept_ids = [concept_objs[2].id, concept_objs[3].id]  # Gradient Descent, Backprop
        rp = RevisionPlan(
            id             = str(uuid.uuid4()),
            user_id        = user.id,
            concept_ids    = weak_concept_ids,
            schedule       = {
                concept_objs[2].id: {"name": "Gradient Descent",  "next_review": concept_objs[2].next_review.isoformat(), "mastery": 0.30},
                concept_objs[3].id: {"name": "Backpropagation",   "next_review": concept_objs[3].next_review.isoformat(), "mastery": 0.20},
            },
            priority_score = 0.85,
            next_review    = concept_objs[3].next_review,
            created_at     = datetime.utcnow(),
        )
        db.add(rp)

        # ── Learning Events ───────────────────────────────────────────
        events = [
            LearningEvent(
                id=str(uuid.uuid4()), user_id=user.id, event_type="upload",
                result={"filename": "intro_machine_learning.pdf"},
                timestamp=datetime.utcnow() - timedelta(days=5),
            ),
            LearningEvent(
                id=str(uuid.uuid4()), user_id=user.id, event_type="quiz",
                result={"score": 72.0, "material": "ML intro"},
                timestamp=datetime.utcnow() - timedelta(days=3),
            ),
            LearningEvent(
                id=str(uuid.uuid4()), user_id=user.id, event_type="upload",
                result={"filename": "deep_learning_fundamentals.pdf"},
                timestamp=datetime.utcnow() - timedelta(days=2),
            ),
        ]
        for ev in events:
            db.add(ev)

        db.commit()
        print("✅ StudyAI seed data inserted successfully")
        print(f"   User: {user.email} (ID: {user.id})")
        print(f"   Materials: {mat1.filename}, {mat2.filename}")
        print(f"   Concepts: {[c.name for c in concept_objs]}")

    except IntegrityError:
        db.rollback()
        print("ℹ️  Already seeded, skipping — data already exists in studyai.db")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
