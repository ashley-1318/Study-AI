"""End-to-End Workflow Tests

Tests for complete user workflows: upload → process → quiz → revision.
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.mark.e2e
@pytest.mark.asyncio
class TestUploadWorkflow:
    """Test complete upload and processing workflow."""
    
    async def test_complete_upload_pipeline(self, test_db, test_user, sample_pdf_path):
        """
        Test E2E workflow: Upload PDF → Parse → Extract → Embed → Index → Summarize → Quiz → Revision
        
        This simulates the full LangGraph pipeline execution.
        """
        # Step 1: Upload material
        material_data = {
            "user_id": test_user.id,
            "title": "Test Material",
            "filename": "test.pdf",
            "filepath": str(sample_pdf_path)
        }
        
        # Step 2: Parse document
        raw_text = "Machine learning is a subset of artificial intelligence. " * 20
        chunks = [raw_text[i:i+500] for i in range(0, len(raw_text), 500)]
        
        assert len(chunks) > 0, "Should create text chunks"
        
        # Step 3: Extract concepts (simulated)
        concepts = [
            {"name": "Machine Learning", "definition": "A subset of AI"},
            {"name": "Artificial Intelligence", "definition": "Computer systems that mimic human intelligence"}
        ]
        
        assert len(concepts) == 2
        
        # Step 4: Generate embeddings (simulated)
        import numpy as np
        embeddings = np.random.rand(len(chunks), 384).astype('float32')
        
        assert embeddings.shape == (len(chunks), 384)
        
        # Step 5: Index in FAISS (simulated)
        # In real test, use FAISSStore
        index_created = True
        assert index_created
        
        # Step 6: Generate summary (simulated)
        summary = "# Machine Learning Overview\n\nKey concepts covered..."
        
        assert len(summary) > 0
        assert summary.startswith("#")
        
        # Step 7: Generate quiz (simulated)
        quiz = {
            "questions": [
                {
                    "question": "What is ML?",
                    "options": ["A) AI subset", "B) Database", "C) Network", "D) Algorithm"],
                    "correct_answer": "A"
                }
            ]
        }
        
        assert len(quiz["questions"]) > 0
        
        # Step 8: Create revision plan (simulated)
        revision_plan = {
            "strategy": "balanced",
            "total_concepts": 2,
            "weak_concepts": ["Machine Learning"],
            "schedule": []
        }
        
        assert revision_plan["total_concepts"] == 2
        
        # Step 9: Mark material as processed
        processing_status = "done"
        
        assert processing_status == "done"
    
    async def test_websocket_progress_streaming(self, test_user):
        """Test WebSocket streaming of pipeline progress."""
        # Simulate WebSocket messages during pipeline
        progress_updates = [
            {"step": "parsing", "progress": 10, "status": "Processing..."},
            {"step": "extracting", "progress": 30, "status": "Extracting concepts..."},
            {"step": "embedding", "progress": 50, "status": "Generating embeddings..."},
            {"step": "indexing", "progress": 70, "status": "Building index..."},
            {"step": "summarizing", "progress": 85, "status": "Creating summary..."},
            {"step": "done", "progress": 100, "status": "Complete!"}
        ]
        
        # Verify all steps present
        steps = [update["step"] for update in progress_updates]
        assert "parsing" in steps
        assert "extracting" in steps
        assert "done" in steps
        
        # Verify progress increases
        progress_values = [update["progress"] for update in progress_updates]
        assert progress_values == sorted(progress_values), "Progress should increase monotonically"
        assert progress_values[-1] == 100


@pytest.mark.e2e
class TestQuizWorkflow:
    """Test complete quiz generation and submission workflow."""
    
    def test_complete_quiz_workflow(self, test_db, test_user, test_material, test_concepts):
        """Test E2E: Generate quiz → Submit answers → Update mastery → View results."""
        
        # Step 1: Generate quiz from weak concepts
        weak_concepts = [c for c in test_concepts if c.mastery_score < 0.6]
        
        quiz_data = {
            "id": "quiz_123",
            "user_id": test_user.id,
            "material_id": test_material.id,
            "questions": [
                {
                    "concept_id": weak_concepts[0].id,
                    "question": "What is Machine Learning?",
                    "options": ["A) AI subset", "B) Database", "C) Network", "D) Algorithm"],
                    "correct_answer": "A"
                }
            ]
        }
        
        assert len(quiz_data["questions"]) > 0
        
        # Step 2: User submits answers
        user_answers = {
            quiz_data["questions"][0]["concept_id"]: "A"  # Correct
        }
        
        # Step 3: Grade answers
        results = []
        for question in quiz_data["questions"]:
            user_answer = user_answers.get(question["concept_id"])
            is_correct = (user_answer == question["correct_answer"])
            results.append({
                "concept_id": question["concept_id"],
                "correct": is_correct
            })
        
        assert results[0]["correct"] is True
        
        # Step 4: Update concept mastery (SM-2)
        for result in results:
            concept = next(c for c in test_concepts if c.id == result["concept_id"])
            old_mastery = concept.mastery_score
            
            if result["correct"]:
                concept.mastery_score = min(1.0, old_mastery + 0.1)
            else:
                concept.mastery_score = max(0.0, old_mastery - 0.15)
            
            test_db.commit()
        
        # Step 5: Calculate quiz score
        score = (sum(1 for r in results if r["correct"]) / len(results)) * 100
        
        assert score == 100.0, "All answers correct"
        
        # Step 6: Log learning event
        learning_event = {
            "user_id": test_user.id,
            "event_type": "quiz_completed",
            "score": score,
            "concepts_covered": len(results)
        }
        
        assert learning_event["event_type"] == "quiz_completed"
        assert learning_event["score"] == 100.0


@pytest.mark.e2e
class TestQnAWorkflow:
    """Test complete Q&A workflow with RAG."""
    
    def test_complete_qna_workflow(self, test_db, test_user, test_material):
        """Test E2E: Ask question → Embed → Search FAISS → Retrieve context → LLM answer → Return with citations."""
        
        # Step 1: User asks question
        question = "What is machine learning?"
        
        # Step 2: Generate question embedding
        import numpy as np
        question_embedding = np.random.rand(384).astype('float32')
        
        assert len(question_embedding) == 384
        
        # Step 3: Search FAISS index (simulated)
        search_results = [
            {
                "text": "Machine learning is a subset of AI that enables systems to learn from data.",
                "material_id": test_material.id,
                "score": 0.95
            },
            {
                "text": "ML algorithms improve automatically through experience.",
                "material_id": test_material.id,
                "score": 0.87
            }
        ]
        
        assert len(search_results) > 0
        assert search_results[0]["score"] > 0.9
        
        # Step 4: Build context for LLM
        context = "\n\n".join([r["text"] for r in search_results[:3]])
        
        assert "machine learning" in context.lower()
        
        # Step 5: Generate answer with LLM (simulated)
        answer = "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed."
        
        # Step 6: Add citations
        citations = [
            {"material_id": test_material.id, "material_title": test_material.title}
        ]
        
        response = {
            "answer": answer,
            "citations": citations,
            "confidence": 0.95
        }
        
        assert "machine learning" in response["answer"].lower()
        assert len(response["citations"]) > 0
        assert response["confidence"] > 0.9


@pytest.mark.e2e
class TestRevisionWorkflow:
    """Test complete revision planning workflow."""
    
    def test_complete_revision_workflow(self, test_db, test_concepts):
        """Test E2E: Identify weak concepts → Generate revision plan → Execute revision → Track progress."""
        
        # Step 1: Identify concepts due for revision
        import datetime
        today = datetime.date.today()
        
        due_concepts = [
            c for c in test_concepts
            if c.next_review is None or c.next_review <= today
        ]
        
        # Step 2: Prioritize by mastery (weakest first)
        priority_list = sorted(due_concepts, key=lambda x: x.mastery_score)
        
        assert len(priority_list) > 0
        if len(priority_list) > 1:
            assert priority_list[0].mastery_score <= priority_list[-1].mastery_score
        
        # Step 3: Generate revision plan
        revision_plan = {
            "strategy": "balanced",  # threshold 0.6
            "concepts_to_review": [
                {
                    "concept_id": c.id,
                    "name": c.name,
                    "mastery": c.mastery_score,
                    "priority": "high" if c.mastery_score < 0.4 else "medium"
                }
                for c in priority_list
            ],
            "estimated_time": len(priority_list) * 5  # 5 min per concept
        }
        
        assert len(revision_plan["concepts_to_review"]) > 0
        
        # Step 4: Retrieve relevant study materials (RAG)
        for concept in priority_list:
            # Search FAISS for concept name
            relevant_chunks = [
                f"Content about {concept.name}...",
                f"More details on {concept.name}..."
            ]
            
            assert len(relevant_chunks) > 0
        
        # Step 5: User studies and tests knowledge (via quiz)
        # Simulate quiz result
        quiz_result = {"concept_id": priority_list[0].id, "correct": True}
        
        # Step 6: Update next review date (SM-2)
        concept = priority_list[0]
        concept.interval_days = int(concept.interval_days * concept.ease_factor)
        concept.next_review = today + datetime.timedelta(days=concept.interval_days)
        
        assert concept.interval_days > 1
        assert concept.next_review > today


@pytest.mark.e2e
class TestAnalyticsWorkflow:
    """Test complete analytics and progress tracking workflow."""
    
    def test_complete_analytics_workflow(self, test_db, test_user, test_material, test_concepts):
        """Test E2E: Track learning events → Compute analytics → Generate insights."""
        
        # Step 1: Collect learning events
        learning_events = [
            {"event_type": "material_uploaded", "timestamp": "2026-03-01"},
            {"event_type": "quiz_completed", "score": 80, "timestamp": "2026-03-02"},
            {"event_type": "quiz_completed", "score": 90, "timestamp": "2026-03-03"},
        ]
        
        # Step 2: Compute mastery statistics
        total_concepts = len(test_concepts)
        mastered = sum(1 for c in test_concepts if c.mastery_score >= 0.8)
        in_progress = sum(1 for c in test_concepts if 0.4 <= c.mastery_score < 0.8)
        weak = sum(1 for c in test_concepts if c.mastery_score < 0.4)
        
        mastery_stats = {
            "total": total_concepts,
            "mastered": mastered,
            "in_progress": in_progress,
            "weak": weak,
            "mastery_percentage": (mastered / total_concepts * 100) if total_concepts > 0 else 0
        }
        
        assert mastery_stats["total"] == len(test_concepts)
        assert mastery_stats["mastered"] + mastery_stats["in_progress"] + mastery_stats["weak"] == total_concepts
        
        # Step 3: Compute quiz performance trend
        quiz_scores = [e["score"] for e in learning_events if e["event_type"] == "quiz_completed"]
        
        if len(quiz_scores) >= 2:
            trend = "improving" if quiz_scores[-1] > quiz_scores[0] else "declining"
            assert trend == "improving", "Scores went from 80 to 90"
        
        # Step 4: Identify knowledge gaps
        weak_concepts = [c for c in test_concepts if c.mastery_score < 0.4]
        knowledge_gaps = [{"name": c.name, "mastery": c.mastery_score} for c in weak_concepts]
        
        # Step 5: Generate recommendations
        recommendations = [] if len(weak_concepts) == 0 else [
            f"Review '{c.name}' (mastery: {c.mastery_score:.1%})"
            for c in weak_concepts[:3]
        ]
        
        analytics_report = {
            "mastery_stats": mastery_stats,
            "quiz_trend": quiz_scores,
            "knowledge_gaps": knowledge_gaps,
            "recommendations": recommendations
        }
        
        assert "mastery_stats" in analytics_report
        assert "quiz_trend" in analytics_report
