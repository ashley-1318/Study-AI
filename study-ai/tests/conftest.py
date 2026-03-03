"""Pytest Configuration and Shared Fixtures

This module provides shared test fixtures and configuration for the entire test suite.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock
import pytest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database import Base, User, StudyMaterial, Concept, Quiz, QuizAnswer  # type: ignore

# Initialize faker
fake = Faker()


# ─── Database Fixtures ───────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    engine.dispose()
    os.unlink(db_path)


@pytest.fixture
def test_user(test_db: Session) -> User:
    """Create a test user."""
    user = User(
        id=str(fake.uuid4()),
        google_id=f"google_{fake.uuid4()}",
        email=fake.email(),
        name=fake.name(),
        avatar_url=fake.image_url()
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_material(test_db: Session, test_user: User) -> StudyMaterial:
    """Create a test study material."""
    material = StudyMaterial(
        id=str(fake.uuid4()),
        user_id=test_user.id,
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        content_text="This is test content about machine learning.",
        summary="Test summary",
        status="done"
    )
    test_db.add(material)
    test_db.commit()
    test_db.refresh(material)
    return material


@pytest.fixture
def test_concepts(test_db: Session, test_material: StudyMaterial, test_user: User) -> list[Concept]:
    """Create test concepts."""
    concepts = [
        Concept(
            id=str(fake.uuid4()),
            material_id=test_material.id,
            user_id=test_user.id,
            name="Machine Learning",
            definition="A subset of AI that enables systems to learn from data.",
            mastery_score=0.5,
            easiness_factor=2.5,
            repetition_count=0,
            interval_days=1
        ),
        Concept(
            id=str(fake.uuid4()),
            material_id=test_material.id,
            user_id=test_user.id,
            name="Neural Network",
            definition="A computing system inspired by biological neural networks.",
            mastery_score=0.3,
            easiness_factor=2.5,
            repetition_count=0,
            interval_days=1
        )
    ]
    for concept in concepts:
        test_db.add(concept)
    test_db.commit()
    for concept in concepts:
        test_db.refresh(concept)
    return concepts


# ─── FAISS Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def mock_faiss_store():
    """Mock FAISS store for testing without actual vector operations."""
    mock_store = MagicMock()
    mock_store.add_embeddings.return_value = None
    mock_store.search.return_value = [
        {"text": "Sample chunk 1", "material_id": "123", "score": 0.95},
        {"text": "Sample chunk 2", "material_id": "123", "score": 0.85}
    ]
    return mock_store


@pytest.fixture
def temp_faiss_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for FAISS indexes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ─── Groq LLM Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def mock_groq_client():
    """Mock Groq client for testing without API calls."""
    mock_client = MagicMock()
    
    # Mock concept extraction response
    mock_extraction_response = Mock()
    mock_extraction_response.choices = [Mock()]
    mock_extraction_response.choices[0].message.content = '''
    {
        "concepts": [
            {"name": "Test Concept", "definition": "A concept for testing."}
        ]
    }
    '''
    
    # Mock summary response
    mock_summary_response = Mock()
    mock_summary_response.choices = [Mock()]
    mock_summary_response.choices[0].message.content = "# Test Summary\n\nThis is a test summary."
    
    # Mock quiz generation response
    mock_quiz_response = Mock()
    mock_quiz_response.choices = [Mock()]
    mock_quiz_response.choices[0].message.content = '''
    {
        "questions": [
            {
                "question": "What is machine learning?",
                "options": ["A) AI subset", "B) Database", "C) Network", "D) Algorithm"],
                "correct_answer": "A",
                "explanation": "ML is a subset of AI."
            }
        ]
    }
    '''
    
    mock_client.chat.completions.create.side_effect = [
        mock_extraction_response,
        mock_summary_response,
        mock_quiz_response
    ]
    
    return mock_client


@pytest.fixture
def mock_groq_env(monkeypatch):
    """Set mock Groq API key in environment."""
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")


# ─── Test Data Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    """Create a sample PDF file for testing."""
    # Note: This creates a text file as placeholder. In real tests, use actual PDF.
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("Sample PDF content for testing document parsing.")
    return pdf_path


@pytest.fixture
def sample_text_chunks() -> list[str]:
    """Provide sample text chunks for testing."""
    return [
        "Machine learning is a subset of artificial intelligence.",
        "Neural networks are computing systems inspired by biological networks.",
        "Deep learning uses multiple layers to progressively extract features.",
        "Supervised learning requires labeled training data.",
        "Unsupervised learning finds patterns in unlabeled data."
    ]


@pytest.fixture
def sample_embeddings() -> list[list[float]]:
    """Provide sample 384-dim embeddings (simplified to 5-dim for testing)."""
    import random
    random.seed(42)
    return [[random.random() for _ in range(384)] for _ in range(5)]


# ─── API Testing Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def api_headers(test_user: User) -> Dict[str, str]:
    """Generate API headers with mock JWT token."""
    # In real implementation, generate actual JWT
    return {
        "Authorization": f"Bearer mock_jwt_token_for_{test_user.id}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def mock_jwt_token(test_user: User) -> str:
    """Generate a mock JWT token."""
    return f"mock_jwt_{test_user.id}"


# ─── Pytest Configuration ────────────────────────────────────────────────────


def pytest_configure(config):
    """Pytest configuration hook."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "benchmark: marks tests as performance benchmarks"
    )
