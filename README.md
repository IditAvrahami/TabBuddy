# TabBuddy

Medication scheduling companion that keeps drug reminders, meal-based dependencies, and dismissal/snooze workflows in sync across a FastAPI backend and a React frontend.

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Getting Started](#getting-started)
6. [Docker Compose](#docker-compose)
7. [Running Tests](#running-tests)
8. [Project Structure](#project-structure)
9. [API Surface](#api-surface)
10. [Future Planning](#future-planning)

## Overview
TabBuddy helps patients and caregivers coordinate complex medication plans. The backend models flexible dependencies (absolute times, relative to other drugs, or around meals), calculates when a dose is due, and surfaces actionable notifications. The frontend provides an opinionated UI for capturing regimens, editing schedules, and responding to reminders in real time.

## Features
- Unified schedule management: create, update, delete drug schedules with dosage, frequency, and dependency controls.
- Meal-aware dosing: define meal times and offsets so medications can be taken before or after specific meals.
- Drug-to-drug offsets: chain medications together with minute-based offsets for complex protocols.
- Real-time reminders: timeline calculator surfaces notifications that are due, with snooze/dismiss that respect overrides.
- React dashboard: responsive experience for managing drugs, editing schedules, and monitoring reminders.
- Tooling & scripts: reproducible Docker Compose stack, helper scripts under `tools/`, and automated tests for backend and frontend.

## Architecture
- **Backend (`backend/`)**
  - FastAPI application (`backend/main.py`) exposing `/drug`, `/meal-schedules`, and `/notifications` routes.
  - SQLAlchemy models (`backend/models.py`) representing drugs, schedules, meals, and notification overrides stored in PostgreSQL.
  - `TimelineCalculator` service (`backend/services/timeline_calculator.py`) computes due notifications and applies snooze/dismiss overrides.
  - Alembic migrations in `backend/alembic/` keep the schema in sync.
- **Frontend (`frontend/`)**
  - React + TypeScript single-page app (`frontend/src/App.tsx`) with tabs for drug management and settings.
  - Polls the backend `/notifications` endpoint, shows `ReminderModal`, and provides CRUD forms for schedules.
  - Shared primitives and form components under `frontend/src/components/`.
- **Infrastructure**
  - `docker-compose.yml` orchestrates PostgreSQL, backend, and frontend containers for a full-stack dev environment.
  - Helper scripts under `tools/` handle test database orchestration and debugging.

## Tech Stack
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, Uvicorn.
- Frontend: React 19, TypeScript 4.9, react-scripts 5, CSS modules.
- Tooling: pytest, httpx, Testing Library, Docker, Ruff, Black, Mypy, ESLint.

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- PostgreSQL 16 (or use Docker Compose)

### 1. Clone & Install
```bash
git clone <repo>
cd TabBuddy
```

#### Backend setup
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows; use source .venv/bin/activate on macOS/Linux
pip install -r backend/requirements.txt
```

Set your database connection (matches docker-compose defaults):
```bash
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/tabbuddy
```
(Use `export` instead of `set` on macOS/Linux.)

Run migrations if you are not letting FastAPI auto-create tables:
```bash
cd backend
alembic upgrade head
```

Start the API:
```bash
uvicorn backend.main:app --reload --port 8000
```

#### Frontend setup
```bash
cd frontend
npm install
npm start
```

The app runs at `http://localhost:3000` and talks to the backend at `http://localhost:8000`. Adjust `REACT_APP_API_URL` if your backend lives elsewhere.

## Docker Compose
To run everything with Docker:
```bash
docker compose up --build
```

Services:
- `db`: PostgreSQL 16 exposed on `5433`.
- `backend`: FastAPI on `8000`.
- `frontend`: React dev server on `3000` (proxies to backend via `REACT_APP_API_URL`).

Stop the stack with `docker compose down`. Named volume `pgdata` persists database state.

## Running Tests
- **Backend**: `python tools/run_tests.py` spins up a temporary PostgreSQL instance (port `5434`) and runs pytest in `backend/test/`. You can also run `pytest backend/test -v` if you manage the test DB yourself.
- **Frontend**: `npm test` (watch mode), or `npm run test:ci` for a single pass. Additional commands: `npm run lint`, `npm run type-check`.

## Project Structure
```text
backend/
  api/                # FastAPI routers for drugs, meals, notifications
  services/           # Timeline calculator and supporting utilities
  models.py           # SQLAlchemy ORM models
  main.py             # FastAPI entrypoint
frontend/
  src/                # React components, API layer, styles, utilities
  public/             # Static assets for CRA
tools/
  start_test_db.py    # Spins up local Postgres for tests
  run_tests.py        # Wraps pytest with test DB lifecycle
docker-compose.yml    # Full-stack orchestration
```

## API Surface
- `POST /drug`, `GET /drug`, `PUT /drug-id/{id}`, `DELETE /drug-id/{id}` – CRUD for drug schedules with dependency configuration.
- `GET/POST/PUT/DELETE /meal-schedules` – manage meal anchor times.
- `GET /notifications` – poll for notifications due within the current time window.
- `POST /notifications/{schedule_id}/snooze` – push a notification by N minutes.
- `POST /notifications/{schedule_id}/dismiss` – suppress a notification for the day.

See the FastAPI docs (auto-served at `http://localhost:8000/docs`) for schemas and try-it-out capabilities.

## Future Planning

Development is planned for native mobile applications supporting both iOS and Android. The current frontend architecture facilitates this migration through a clear separation of primitive components (`frontend/src/components/primitives/`) and shared components built as pure React without DOM references, enabling maximum code sharing.

**Migration Strategy**: The planned approach uses React Native, replacing primitive components with React Native alternatives (e.g., `Button` → `TouchableOpacity`) while reusing shared business logic components with minimal changes. The existing FastAPI backend supports multiple client types without architectural changes.

**Mobile Features**: Native push notifications, background processing for medication reminders, system notification center integration, and offline data synchronization capabilities.
