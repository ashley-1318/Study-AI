"""Mock Test Fixtures

Provides sample test data and mock objects for testing without external dependencies.
"""

# Sample study materials
SAMPLE_MATERIALS = {
    "ml_basics": {
        "title": "Machine Learning Basics",
        "content": """
        Machine Learning is a subset of artificial intelligence that enables 
        systems to learn and improve from experience without being explicitly programmed.
        
        Key Concepts:
        1. Supervised Learning - Learning from labeled data
        2. Unsupervised Learning - Finding patterns in unlabeled data
        3. Reinforcement Learning - Learning through trial and error
        
        Neural networks are computing systems inspired by biological neural networks.
        They consist of layers of neuron connected nodes that process information.
        
        Deep learning uses multiple layers to progressively extract higher-level features.
        """,
        "concepts": [
            {
                "name": "Machine Learning",
                "definition": "A subset of AI that enables systems to learn from data"
            },
            {
                "name": "Supervised Learning",
                "definition": "Learning from labeled training data"
            },
            {
                "name": "Neural Network",
                "definition": "Computing systems inspired by biological neural networks"
            },
            {
                "name": "Deep Learning",
                "definition": "ML using multiple layers to extract features"
            }
        ]
    },
    
    "ai_fundamentals": {
        "title": "AI Fundamentals",
        "content": """
        Artificial Intelligence (AI) refers to computer systems capable of performing 
        tasks that typically require human intelligence.
        
        Types of AI:
        - Narrow AI: Specialized in one task
        - General AI: Human-level intelligence across tasks
        - Super AI: Surpasses human intelligence
        
        Common AI applications include natural language processing, computer vision,
        and robotics. Machine learning is the primary method for building AI systems.
        """,
        "concepts": [
            {
                "name": "Artificial Intelligence",
                "definition": "Computer systems that mimic human intelligence"
            },
            {
                "name": "Natural Language Processing",
                "definition": "AI for understanding and generating human language"
            },
            {
                "name": "Computer Vision",
                "definition": "AI for interpreting visual information"
            }
        ]
    }
}


# Sample quiz questions
SAMPLE_QUIZZES = {
    "ml_quiz": {
        "questions": [
            {
                "question": "What is machine learning?",
                "type": "multiple_choice",
                "options": [
                    "A) A subset of AI that learns from data",
                    "B) A database management system",
                    "C) A type of neural network",
                    "D) A programming language"
                ],
                "correct_answer": "A",
                "explanation": "Machine learning is a subset of AI that enables systems to learn from experience."
            },
            {
                "question": "___ learning uses labeled training data.",
                "type": "fill_blank",
                "correct_answer": "Supervised",
                "explanation": "Supervised learning requires labeled data to train models."
            },
            {
                "question": "Deep learning uses multiple layers of neurons.",
                "type": "true_false",
                "correct_answer": "True",
                "explanation": "Deep learning architectures consist of multiple layers."
            }
        ]
    }
}


# Sample embeddings (simplified 5-dim instead of 384)
SAMPLE_EMBEDDINGS = [
    [0.12, 0.34, 0.56, 0.78, 0.90],
    [0.11, 0.33, 0.55, 0.77, 0.89],
    [0.89, 0.67, 0.45, 0.23, 0.01],
    [0.50, 0.50, 0.50, 0.50, 0.50],
]


# Sample user data
SAMPLE_USERS = [
    {
        "id": "user_001",
        "username": "alice_student",
        "email": "alice@example.com",
        "created_at": "2026-01-01"
    },
    {
        "id": "user_002",
        "username": "bob_learner",
        "email": "bob@example.com",
        "created_at": "2026-01-15"
    }
]


# Sample learning events
SAMPLE_LEARNING_EVENTS = [
    {
        "user_id": "user_001",
        "event_type": "material_uploaded",
        "material_id": "mat_001",
        "timestamp": "2026-03-01T10:00:00"
    },
    {
        "user_id": "user_001",
        "event_type": "quiz_completed",
        "quiz_id": "quiz_001",
        "score": 85.0,
        "timestamp": "2026-03-01T11:00:00"
    },
    {
        "user_id": "user_001",
        "event_type": "concept_mastered",
        "concept_id": "concept_001",
        "mastery_score": 0.85,
        "timestamp": "2026-03-01T11:05:00"
    }
]


# Mock LLM responses
MOCK_LLM_RESPONSES = {
    "extract_concepts": {
        "response": """
        {
            "concepts": [
                {
                    "name": "Machine Learning",
                    "definition": "A subset of AI that enables systems to learn from data"
                },
                {
                    "name": "Neural Network",
                    "definition": "Computing systems inspired by biological neural networks"
                }
            ]
        }
        """
    },
    
    "generate_summary": {
        "response": """
        # Machine Learning Overview
        
        ## Key Concepts
        
        Machine learning is a fundamental technique in artificial intelligence that enables
        systems to improve their performance through experience.
        
        ### Types of Learning
        
        1. **Supervised Learning**: Uses labeled data
        2. **Unsupervised Learning**: Finds patterns in unlabeled data
        3. **Reinforcement Learning**: Learns through trial and error
        
        ## Neural Networks
        
        Neural networks form the foundation of deep learning, using interconnected layers
        of nodes to process information.
        """
    },
    
    "generate_quiz": {
        "response": """
        {
            "questions": [
                {
                    "question": "What is machine learning?",
                    "options": [
                        "A) AI technique for learning from data",
                        "B) Database system",
                        "C) Programming language",
                        "D) Operating system"
                    ],
                    "correct_answer": "A",
                    "explanation": "ML is an AI technique that learns from data."
                }
            ]
        }
        """
    },
    
    "answer_question": {
        "response": """
        Machine learning is a subset of artificial intelligence that focuses on developing
        systems that can learn and improve from experience without being explicitly programmed.
        It uses algorithms to analyze data, identify patterns, and make decisions with minimal
        human intervention.
        """
    }
}


# Sample revision plans
SAMPLE_REVISION_PLANS = {
    "balanced": {
        "strategy": "balanced",
        "threshold": 0.6,
        "concepts_to_review": [
            {
                "concept_id": "concept_001",
                "name": "Machine Learning",
                "mastery": 0.45,
                "priority": "high",
                "next_review": "2026-03-04"
            },
            {
                "concept_id": "concept_002",
                "name": "Neural Networks",
                "mastery": 0.58,
                "priority": "medium",
                "next_review": "2026-03-05"
            }
        ],
        "estimated_time_minutes": 30
    }
}


def get_sample_material(material_type="ml_basics"):
    """Get a sample study material by type."""
    return SAMPLE_MATERIALS.get(material_type, SAMPLE_MATERIALS["ml_basics"])


def get_sample_quiz(quiz_type="ml_quiz"):
    """Get a sample quiz by type."""
    return SAMPLE_QUIZZES.get(quiz_type, SAMPLE_QUIZZES["ml_quiz"])


def get_mock_llm_response(response_type):
    """Get a mock LLM response by type."""
    return MOCK_LLM_RESPONSES.get(response_type, {}).get("response", "")
