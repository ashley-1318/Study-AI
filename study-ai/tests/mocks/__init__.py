"""Test Mocks Package

Provides mock objects and sample data for testing.
"""

from .sample_materials import (
    SAMPLE_MATERIALS,
    SAMPLE_QUIZZES,
    SAMPLE_EMBEDDINGS,
    SAMPLE_USERS,
    get_sample_material,
    get_sample_quiz,
    get_mock_llm_response
)

from .mock_groq_client import (
    MockGroqClient,
    MockGroqClientWithErrors,
    create_mock_groq_client
)

__all__ = [
    'SAMPLE_MATERIALS',
    'SAMPLE_QUIZZES',
    'SAMPLE_EMBEDDINGS',
    'SAMPLE_USERS',
    'get_sample_material',
    'get_sample_quiz',
    'get_mock_llm_response',
    'MockGroqClient',
    'MockGroqClientWithErrors',
    'create_mock_groq_client'
]
