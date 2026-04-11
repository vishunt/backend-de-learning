# Task Management API

A production-grade REST API built with FastAPI, PostgreSQL, Redis, and Celery. Features JWT authentication, Redis caching, rate limiting, background task processing, and a comprehensive pytest test suite with 94% coverage.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | Web framework |
| PostgreSQL | Primary database |
| SQLAlchemy + Alembic | ORM and migrations |
| Redis | Caching and rate limiting |
| Celery | Background task queue |
| Docker Compose | Container orchestration |
| pytest | Testing (94% coverage) |
| JWT | Authentication |

## Features

- Full CRUD for task management
- JWT authentication with access and refresh tokens
- Redis caching on task list endpoints
- Rate limiting (60 requests/minute per IP)
- Celery background notifications on task create/complete
- Request/response logging middleware
- Docker Compose with health checks and dependency ordering
- 21 pytest tests covering auth, CRUD, pagination, and data isolation

## Project Structure
task-management-api/
├── routers/
│   ├── auth.py        # Register, login, refresh token
│   └── tasks.py       # CRUD endpoints with caching
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic request/response schemas
├── middleware/        # Rate limiting, logging
├── utils/             # JWT helpers, password hashing
├── tests/             # pytest suite (94% coverage)
├── docker-compose.yml # PostgreSQL, Redis, API, Celery
└── main.py            # App entry point with retry loop

## Quick Start

```bash
# Clone and navigate
git clone https://github.com/vishunt/backend-de-learning.git
cd backend/task-management-api

# Start all services
docker compose up -d

# Run tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=term-missing
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login, returns JWT tokens |
| POST | /auth/refresh | Refresh access token |
| GET | /tasks/ | List tasks (paginated, cached) |
| POST | /tasks/ | Create task |
| GET | /tasks/{id} | Get task by ID |
| PATCH | /tasks/{id} | Update task |
| DELETE | /tasks/{id} | Delete task |
| GET | /tasks/stats/summary | Task statistics |
| GET | /health | Health check |

## Key Design Decisions

**Why Redis for caching?** Task list queries are the most frequent operation. Caching them with a 60-second TTL reduces database load significantly.

**Why Celery for notifications?** Notifications are fire-and-forget — the API should return immediately without waiting for the notification to be sent. Celery handles this asynchronously.

**Why 404 instead of 403 for other users' tasks?** Returning 403 leaks the information that a resource exists. 404 is safer — it neither confirms nor denies existence.

**Why health checks in Docker Compose?** Without them, the API container starts before PostgreSQL is ready and crashes. Health checks ensure correct startup ordering.

## Test Coverage

Running `pytest --cov=. --cov-report=term-missing` produces:

- **513** total lines measured
- **31** lines not covered
- **94% coverage** across the entire codebase

Tests cover: user registration, login, token refresh, task CRUD, data isolation between users, pagination, and error cases.