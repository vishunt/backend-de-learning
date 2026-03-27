import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
from database import Base, get_db
from main import app

# Use SQLite for tests — fast, no Docker needed
TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Replace real DB with test DB
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once before tests, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    

@pytest.fixture(scope="function")
def client():
    """Fresh TestClient per test. Mocks Redis and Celery so tests don't need them."""
    with patch("routers.tasks.redis_client") as mock_redis, \
         patch("routers.tasks.send_task_created_notification") as mock_created, \
         patch("routers.tasks.send_task_completed_notification") as mock_completed:
        
        mock_redis.get.return_value = None   # always cache miss
        mock_redis.setex.return_value = True
        mock_created.delay.return_value = None
        mock_completed.delay.return_value = None
        
        yield TestClient(app)


@pytest.fixture(scope="function")
def registered_user(client):
    """Creates a test user via the register endpoint."""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    return response.json()


@pytest.fixture(scope="function")
def auth_headers(client, registered_user):
    """Logs in and returns auth headers with valid JWT."""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}