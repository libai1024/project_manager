# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Outsourcing Project Management System (外包项目管理系统) - A full-stack application for managing outsourcing projects, clients, platforms, tasks, attachments, and billing.

**Tech Stack:**
- Backend: FastAPI + SQLModel + SQLite (PostgreSQL planned)
- Frontend: Vue 3 + TypeScript + Vite + Element Plus + Pinia

## Development Commands

### Start Everything (Recommended)
```bash
# macOS/Linux
./start_all.sh

# Windows
start_all.bat
```
This starts both backend (port 8000) and frontend (port 5173).

### Backend Only
```bash
cd fastapi_back
./start.sh           # macOS/Linux
start.bat            # Windows
```

First run creates virtual environment, installs dependencies, and initializes SQLite database.

### Frontend Only
```bash
cd project_manager_vue3
./start.sh           # macOS/Linux
start.bat            # Windows
```

### Build Frontend
```bash
cd project_manager_vue3
npm run build
```

## Key URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc

## Backend Architecture

```
fastapi_back/
├── main.py              # App entry point, route registration, middleware
├── requirements.txt     # Python dependencies
├── app/
│   ├── api/             # FastAPI routers (HTTP layer)
│   ├── core/            # Config, database, security, dependencies
│   ├── models/          # SQLModel ORM + Pydantic DTOs (mixed)
│   ├── repositories/    # Database access layer
│   ├── services/        # Business logic orchestration
│   └── exceptions/      # Exception handlers
└── uploads/             # File storage directory
```

### Layered Architecture
- **API Layer** (`app/api/`): Route handlers, request/response binding, auth dependencies
- **Service Layer** (`app/services/`): Business logic, cross-entity orchestration
- **Repository Layer** (`app/repositories/`): Database CRUD operations
- **Models** (`app/models/`): SQLModel classes (ORM + Pydantic schemas in same file)

### Authentication
- JWT access tokens (15 min default) + refresh tokens (30 days)
- Token blacklist for revocation
- Password hashing with bcrypt
- Configurable in `app/core/config.py` via environment variables

### Current API Modules
`auth`, `platforms`, `projects`, `dashboard`, `users`, `attachments`, `attachment_folders`, `todos`, `project_logs`, `step_templates`, `project_parts`, `github_commits`, `video_playbacks`, `historical_projects`, `system_settings`, `tags`

## Frontend Architecture

```
project_manager_vue3/src/
├── main.ts              # App entry, Pinia/Vue Router/Element Plus setup
├── App.vue
├── router/index.ts      # Vue Router with auth guards
├── stores/user.ts       # Pinia store for auth state
├── api/                 # Axios API client modules
│   └── request.ts       # Axios instance with interceptors
├── composables/         # Vue composition functions
├── services/            # Frontend service layer
├── views/               # Page components
├── components/          # Reusable components
├── layouts/             # Layout components
├── styles/              # Global styles
├── types/               # TypeScript type definitions
└── utils/               # Utility functions
```

### State Management
- Pinia store in `stores/user.ts` manages authentication state
- Token stored in localStorage, synced with store
- Route guards check `meta.requiresAuth` and `meta.requiresAdmin`

### API Communication
- Axios instance in `api/request.ts`
- Auto-adds Bearer token to requests
- Handles 401 by redirecting to login
- File upload requests have 30-minute timeout

## Configuration

### Backend (.env)
Create `fastapi_back/.env` for custom settings:
```
DATABASE_URL=sqlite:///./project_manager.db
SECRET_KEY=your-secret-key
CORS_ALLOW_ALL=True
FRONTEND_URL=http://localhost:5173
```

### Frontend
Vite proxy forwards `/api` requests to backend at `localhost:8000`. See `vite.config.ts` for proxy configuration.

## Important Conventions

### Code Style (from .cursorrules)
- Follow PEP 8 for Python
- Use Python 3 type hints
- Use Pydantic for data validation
- Write docstrings and comments
- Modular design with clear separation of concerns

### Backend Patterns
- Dependency injection for auth: `get_current_user` in `app/core/dependencies.py`
- Exception handling centralized in `app/exceptions/handlers.py`
- Models combine ORM table definition and Pydantic DTOs in same file

### Refactoring Roadmap (see 重构.md)
Planned improvements:
1. Introduce Alembic for database migrations
2. Migrate to PostgreSQL as primary database
3. Extract DTOs to `app/schemas/` directory
4. Implement application factory pattern (`create_app()`)
5. Complete API -> Service -> Repository layer separation

## File Storage

Uploaded files stored in `fastapi_back/uploads/`. Database tracks:
- `filename`, `content_type`, `size_bytes`
- `storage_path` for file location
- `project_id`, `folder_id` for organization
