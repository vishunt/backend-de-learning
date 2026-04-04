class TestCreateTask:

    def test_create_task_success(self, client, auth_headers):
        response = client.post("/tasks/", json={
            "title": "Buy groceries",
            "description": "Milk and eggs",
            "priority": "medium"
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["priority"] == "medium"
        assert "id" in data

    def test_create_task_requires_auth(self, client):
        response = client.post("/tasks/", json={
            "title": "Unauthorized task"
        })
        assert response.status_code == 401

    def test_create_task_missing_title(self, client, auth_headers):
        response = client.post("/tasks/", json={
            "description": "No title"
        }, headers=auth_headers)
        assert response.status_code == 422


class TestGetTasks:

    def test_get_tasks_success(self, client, auth_headers):
        response = client.get("/tasks/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_tasks_requires_auth(self, client):
        response = client.get("/tasks/")
        assert response.status_code == 401

    def test_get_tasks_only_own(self, client):
        # Create user A
        client.post("/auth/register", json={
            "username": "userA", "email": "a@test.com", "password": "PassA1234"
        })
        login_a = client.post("/auth/login", json={
            "username": "userA", "password": "PassA1234"
        })
        headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

        # Create user B
        client.post("/auth/register", json={
            "username": "userB", "email": "b@test.com", "password": "PassB1234"
        })
        login_b = client.post("/auth/login", json={
            "username": "userB", "password": "PassB1234"
        })
        headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

        # A creates a task
        client.post("/tasks/", json={"title": "User A secret task"}, headers=headers_a)

        # B should not see A's task
        tasks_b = client.get("/tasks/", headers=headers_b).json()
        titles = [t["title"] for t in tasks_b]
        assert "User A secret task" not in titles


class TestGetSingleTask:

    def test_get_task_by_id(self, client, auth_headers):
        task_id = client.post("/tasks/", json={
            "title": "Find me"
        }, headers=auth_headers).json()["id"]

        response = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Find me"

    def test_get_nonexistent_task(self, client, auth_headers):
        response = client.get("/tasks/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateTask:

    def test_update_task(self, client, auth_headers):
        task_id = client.post("/tasks/", json={
            "title": "Original"
        }, headers=auth_headers).json()["id"]

        response = client.patch(f"/tasks/{task_id}", json={
            "title": "Updated",
            "completed": True
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
        assert response.json()["completed"] is True

    def test_update_nonexistent_task(self, client, auth_headers):
        response = client.patch("/tasks/99999", json={
            "title": "Ghost"
        }, headers=auth_headers)
        assert response.status_code == 404


class TestDeleteTask:

    def test_delete_task(self, client, auth_headers):
        task_id = client.post("/tasks/", json={
            "title": "Delete me"
        }, headers=auth_headers).json()["id"]

        response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 204

        # Confirm it's gone
        get_response = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_nonexistent_task(self, client, auth_headers):
        response = client.delete("/tasks/99999", headers=auth_headers)
        assert response.status_code == 404


class TestTaskStats:

    def test_stats_returns_correct_counts(self, client, auth_headers):
        # Create 2 tasks, complete 1
        t1 = client.post("/tasks/", json={"title": "Task 1"}, headers=auth_headers).json()["id"]
        client.post("/tasks/", json={"title": "Task 2"}, headers=auth_headers)
        client.patch(f"/tasks/{t1}", json={"completed": True}, headers=auth_headers)

        response = client.get("/tasks/stats/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert data["completed"] >= 1
        assert data["pending"] >= 1