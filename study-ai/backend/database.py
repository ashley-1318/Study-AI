"""StudyAI — Database setup, models, and session factory."""
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, Float,
    ForeignKey, Index, Integer, JSON, String, Text,
    create_engine, event as sa_event,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./studyai.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


@sa_event.listens_for(engine, "connect")
def set_sqlite_pragmas(dbapi_conn, _):
    """Enable WAL mode, foreign keys, and normal sync for performance."""
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA foreign_keys=ON")
    cur.execute("PRAGMA synchronous=NORMAL")
    cur.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they do not exist, and apply any pending migrations."""
    Base.metadata.create_all(bind=engine)

    # ── Migration: add columns if they don't exist yet ──
    with engine.connect() as conn:
        for col, col_type in [("file_path", "VARCHAR"), ("connections", "JSON")]:
            try:
                conn.execute(
                    __import__("sqlalchemy").text(
                        f"ALTER TABLE study_materials ADD COLUMN {col} {col_type}"
                    )
                )
                conn.commit()
                print(f"✅ Migration applied: added {col} column")
            except Exception:
                pass  # column already exists

    print("✅ StudyAI database initialized:", DATABASE_URL)


# ──────────────────────────────────────────────────────────────────
# MODELS
# ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    google_id  = Column(String, unique=True, nullable=False, index=True)
    email      = Column(String, unique=True, nullable=False)
    name       = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    materials       = relationship("StudyMaterial",  back_populates="user", cascade="all, delete-orphan")
    concepts        = relationship("Concept",        back_populates="user", cascade="all, delete-orphan")
    quizzes         = relationship("Quiz",           back_populates="user", cascade="all, delete-orphan")
    revision_plans  = relationship("RevisionPlan",  back_populates="user", cascade="all, delete-orphan")
    learning_events = relationship("LearningEvent", back_populates="user", cascade="all, delete-orphan")


class StudyMaterial(Base):
    __tablename__ = "study_materials"
    __table_args__ = (
        CheckConstraint("status IN ('pending','processing','done','error')", name="ck_material_status"),
        Index("ix_material_user_status", "user_id", "status"),
    )

    id           = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename     = Column(String, nullable=False)
    file_path    = Column(String, nullable=True)   # absolute path to uploaded file on disk
    content_text = Column(Text, nullable=True)
    summary      = Column(Text, nullable=True)
    connections  = Column(JSON, default=list)  # Cross-material semantic links
    chunk_count  = Column(Integer, default=0)
    status       = Column(String, default="pending")
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user     = relationship("User", back_populates="materials")
    concepts = relationship("Concept", back_populates="material", cascade="all, delete-orphan")
    quizzes  = relationship("Quiz", back_populates="material")


class Concept(Base):
    __tablename__ = "concepts"
    __table_args__ = (
        CheckConstraint("mastery_score >= 0.0 AND mastery_score <= 1.0", name="ck_concept_mastery"),
        Index("ix_concept_user_review", "user_id", "next_review"),
        Index("ix_concept_material_mastery", "material_id", "mastery_score"),
    )

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    material_id      = Column(String(36), ForeignKey("study_materials.id", ondelete="CASCADE"), nullable=False)
    user_id          = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name             = Column(String, nullable=False)
    definition       = Column(Text, nullable=True)
    embedding_id     = Column(String, nullable=True)
    mastery_score    = Column(Float, default=0.0)
    related_concepts = Column(JSON, default=list)
    # SM-2 fields
    easiness_factor  = Column(Float, default=2.5)
    repetition_count = Column(Integer, default=0)
    interval_days    = Column(Integer, default=1)
    next_review      = Column(DateTime, default=datetime.utcnow)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    material        = relationship("StudyMaterial", back_populates="concepts")
    user            = relationship("User", back_populates="concepts")
    quiz_answers    = relationship("QuizAnswer", back_populates="concept")
    learning_events = relationship("LearningEvent", back_populates="concept")


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = (
        CheckConstraint("difficulty IN ('easy','medium','hard','adaptive')", name="ck_quiz_difficulty"),
        Index("ix_quiz_user_created", "user_id", "created_at"),
    )

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(String(36), ForeignKey("study_materials.id", ondelete="SET NULL"), nullable=True)
    questions   = Column(JSON, default=list)
    difficulty  = Column(String, default="adaptive")
    score       = Column(Float, nullable=True)
    taken_at    = Column(DateTime, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user     = relationship("User", back_populates="quizzes")
    material = relationship("StudyMaterial", back_populates="quizzes")
    answers  = relationship("QuizAnswer", back_populates="quiz", cascade="all, delete-orphan")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id     = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    concept_id  = Column(String(36), ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    question    = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    correct     = Column(Boolean, nullable=True)
    answered_at = Column(DateTime, default=datetime.utcnow)

    quiz    = relationship("Quiz", back_populates="answers")
    concept = relationship("Concept", back_populates="quiz_answers")


class RevisionPlan(Base):
    __tablename__ = "revision_plans"
    __table_args__ = (
        Index("ix_revision_user_review", "user_id", "next_review"),
    )

    id             = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id        = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_ids    = Column(JSON, default=list)
    schedule       = Column(JSON, default=dict)
    priority_score = Column(Float, default=0.0)
    next_review    = Column(DateTime, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="revision_plans")


class LearningEvent(Base):
    __tablename__ = "learning_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('upload','quiz','revision','search','summary_view')",
            name="ck_event_type"
        ),
        Index("ix_event_user_time", "user_id", "timestamp"),
    )

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    result     = Column(JSON, default=dict)
    timestamp  = Column(DateTime, default=datetime.utcnow)

    user    = relationship("User", back_populates="learning_events")
    concept = relationship("Concept", back_populates="learning_events")
