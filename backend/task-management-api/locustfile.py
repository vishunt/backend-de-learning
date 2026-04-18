from locust import HttpUser, task, between
import random

class TaskAPIUser(HttpUser):
    """
    Simulates a real user interacting with the Task Management API.
    Each virtual user logs in, creates tasks, reads them, and deletes them.
    """
    wait_time = between(1, 3)  # wait 1-3 seconds between tasks
    token = None

    def on_start(self):
        """Runs once when each virtual user starts — registers and logs in."""
        username = f"user_{random.randint(1000, 9999)}"
        email = f"{username}@test.com"

        # Register
        self.client.post("/auth/register", json={
            "username": username,
            "email": email,
            "password": "TestPass123"
        })

        # Login and store token
        response = self.client.post("/auth/login", json={
            "username": username,
            "password": "TestPass123"
        })
        self.token = response.json().get("access_token")

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def get_tasks(self):
        """Most frequent action — list tasks (uses Redis cache)."""
        self.client.get("/tasks/", headers=self.get_headers())

    @task(2)
    def create_task(self):
        """Create a new task."""
        self.client.post("/tasks/", json={
            "title": f"Task {random.randint(1, 1000)}",
            "description": "Performance test task",
            "priority": random.choice(["low", "medium", "high"])
        }, headers=self.get_headers())

    @task(1)
    def get_health(self):
        """Health check endpoint — should always be fast."""
        self.client.get("/health")

    @task(1)
    def get_stats(self):
        """Task stats endpoint."""
        self.client.get("/tasks/stats/summary", headers=self.get_headers())