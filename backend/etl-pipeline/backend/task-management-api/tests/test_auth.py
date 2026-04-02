class TestRegister:

    def test_register_success(self, client):
        response = client.post("/auth/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, registered_user):
        response = client.post("/auth/register", json={
            "username": "different",
            "email": "test@example.com",
            "password": "TestPass123"
        })
        assert response.status_code == 400

    def test_register_duplicate_username(self, client, registered_user):
        response = client.post("/auth/register", json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "TestPass123"
        })
        assert response.status_code == 400


class TestLogin:

    def test_login_success(self, client, registered_user):
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "TestPass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "WrongPassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/auth/login", json={
            "username": "ghost",
            "password": "DoesntMatter"
        })
        assert response.status_code == 401


class TestRefreshToken:

    def test_refresh_success(self, client, registered_user):
        login = client.post("/auth/login", json={
            "username": "testuser",
            "password": "TestPass123"
        })
        refresh_token = login.json()["refresh_token"]

        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_refresh_invalid_token(self, client):
        response = client.post("/auth/refresh", json={
            "refresh_token": "this.is.fake"
        })
        assert response.status_code == 401