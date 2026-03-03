"""Load Testing with Locust

Simulates concurrent users uploading materials, generating quizzes, and asking questions.
Tests StudyAI performance under realistic load.
"""

from locust import HttpUser, task, between, events
import random
import json
from pathlib import Path


class StudyAIUser(HttpUser):
    """Simulates a student using StudyAI."""
    
    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks
    
    def on_start(self):
        """Initialize user session (login)."""
        # Simulate login
        self.user_id = f"user_{random.randint(1, 1000)}"
        self.token = f"mock_token_{self.user_id}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.material_ids = []
    
    @task(3)
    def view_dashboard(self):
        """View dashboard with mastery stats."""
        with self.client.get(
            f"/api/v1/analytics/mastery?user_id={self.user_id}",
            headers=self.headers,
            catch_response=True  # type: ignore
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")
    
    @task(2)
    def upload_material(self):
        """Upload a study material."""
        # Simulate file upload
        material_data = {
            "title": f"Material {random.randint(1, 100)}",
            "content": "Machine learning is a subset of AI. " * 100
        }
        
        with self.client.post(
            "/api/v1/materials/upload",
            headers=self.headers,
            json=material_data,
            catch_response=True  # type: ignore
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.material_ids.append(data.get("material_id"))
                    response.success()
                except:
                    response.failure("No material_id in response")
            else:
                response.failure(f"Upload failed: {response.status_code}")
    
    @task(5)
    def generate_quiz(self):
        """Generate a quiz."""
        if not self.material_ids:
            return  # Skip if no materials uploaded yet
        
        material_id = random.choice(self.material_ids)
        
        with self.client.post(
            "/api/v1/quiz/generate",
            headers=self.headers,
            json={
                "material_id": material_id,
                "num_questions": 5,
                "difficulty": random.choice(["easy", "medium", "hard"])
            },
            catch_response=True  # type: ignore
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Quiz generation failed: {response.status_code}")
    
    @task(4)
    def submit_quiz(self):
        """Submit quiz answers."""
        # Simulate quiz submission
        quiz_data = {
            "quiz_id": f"quiz_{random.randint(1, 100)}",
            "answers": {
                f"q{i}": random.choice(["A", "B", "C", "D"])
                for i in range(5)
            }
        }
        
        with self.client.post(
            f"/api/v1/quiz/{quiz_data['quiz_id']}/submit",
            headers=self.headers,
            json=quiz_data,
            catch_response=True  # type: ignore
        ) as response:
            if response.status_code in [200, 404]:  # 404 if quiz doesn't exist
                response.success()
            else:
                response.failure(f"Submission failed: {response.status_code}")
    
    @task(3)
    def ask_question(self):
        """Ask a question using Q&A."""
        questions = [
            "What is machine learning?",
            "Explain neural networks.",
            "How does deep learning work?",
            "What is supervised learning?",
            "Define artificial intelligence."
        ]
        
        with self.client.post(
            "/api/v1/qna/ask",
            headers=self.headers,
            json={"question": random.choice(questions)},
            catch_response=True  # type: ignore
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Q&A failed: {response.status_code}")
    
    @task(2)
    def get_revision_plan(self):
        """Get revision plan."""
        with self.client.get(
            f"/api/v1/revision/plan?user_id={self.user_id}&strategy=balanced",
            headers=self.headers,
            catch_response=True  # type: ignore
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Revision plan failed: {response.status_code}")
    
    @task(1)
    def view_concepts(self):
        """View extracted concepts."""
        if not self.material_ids:
            return
        
        material_id = random.choice(self.material_ids)
        
        with self.client.get(
            f"/api/v1/concepts?material_id={material_id}",
            headers=self.headers,
            catch_response=True  # type: ignore
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Concepts fetch failed: {response.status_code}")


# Event handlers for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test start message."""
    print("\n" + "="*60)
    print("StudyAI Load Test Starting...")
    print(f"Target: {environment.host}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary after test."""
    print("\n" + "="*60)
    print("StudyAI Load Test Complete")
    print("="*60)
    
    stats = environment.stats
    print(f"\nRequests: {stats.total.num_requests}")
    print(f"Failures: {stats.total.num_failures}")
    print(f"Median Response Time: {stats.total.median_response_time}ms")
    print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95)}ms")
    print(f"Requests/sec: {stats.total.current_rps:.2f}")
    print()


# Custom shape for gradual ramp-up
from locust import LoadTestShape

class StudyAILoadShape(LoadTestShape):
    """
    Custom load pattern:
    - Ramp up to 50 users over 5 minutes
    - Maintain 50 users for 10 minutes
    - Ramp down over 2 minutes
    """
    
    stages = [
        {"duration": 300, "users": 50, "spawn_rate": 2},   # 0-5 min: ramp to 50 users
        {"duration": 900, "users": 50, "spawn_rate": 0},   # 5-15 min: maintain 50 users
        {"duration": 1020, "users": 10, "spawn_rate": 5},  # 15-17 min: ramp down to 10
    ]
    
    def tick(self):
        """Return user count and spawn rate for current time."""
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        
        return None  # Test complete


# Usage:
# locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 2 --run-time 10m
# 
# Or with UI:
# locust -f locustfile.py --host=http://localhost:8000
# Then open http://localhost:8089
