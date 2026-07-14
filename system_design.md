# Driving School Management — System Design

## Overview

A full-stack web application for managing a driving school: students, instructors, lessons, vehicles, and scheduling. The system is composed of a Django REST backend, a Vue.js SPA frontend, and a PostgreSQL database, all orchestrated via Docker Compose.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5, Django REST Framework |
| Frontend | Vue 3, Vite, Vue Router |
| Database | PostgreSQL 16 |
| Containerisation | Docker, Docker Compose |
| Environment | `.env` file at project root |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Docker Compose                  │
│                                                  │
│  ┌──────────────┐      ┌──────────────────────┐  │
│  │   frontend   │      │       backend        │  │
│  │  Vue 3/Vite  │─────▶│  Django + DRF        │  │
│  │  port: 3000  │      │  port: 8000          │  │
│  └──────────────┘      └──────────┬───────────┘  │
│                                   │               │
│                         ┌─────────▼───────────┐  │
│                         │        db           │  │
│                         │    PostgreSQL 16    │  │
│                         │    port: 5432       │  │
│                         └─────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Folder Structure

```
auto_road_mgmt/
├── system_design.md          # This document
├── .env                      # All environment variables
├── docker-compose.yml        # Docker Compose orchestration
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/               # Django project config
│   │   ├── __init__.py
│   │   ├── settings.py       # Reads all config from .env
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── management/           # Main Django app (all views here)
│       ├── __init__.py
│       ├── apps.py
│       ├── views.py
│       └── urls.py
│
└── frontend/
    ├── Dockerfile
    ├── .env                  # Frontend-specific env vars
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/
        │   └── index.js
        └── views/            # All Vue page components live here
            └── HomeView.vue
```

---

## Service Responsibilities

### `backend` (Django)
- Exposes a REST API consumed by the frontend
- Handles business logic: students, instructors, vehicles, lessons, scheduling
- All application views reside in `management/views.py`
- Reads configuration exclusively from environment variables

### `frontend` (Vue 3)
- Single-page application served by Vite dev server
- Communicates with backend via `VITE_API_URL`
- All page components reside in `src/views/`

### `db` (PostgreSQL)
- Persistent relational store for all application data
- Credentials and database name sourced from `.env`

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `POSTGRES_DB` | db, backend | Database name |
| `POSTGRES_USER` | db, backend | Database user |
| `POSTGRES_PASSWORD` | db, backend | Database password |
| `POSTGRES_HOST` | backend | DB hostname (`db` service name) |
| `POSTGRES_PORT` | backend | DB port (default `5432`) |
| `DJANGO_SECRET_KEY` | backend | Django secret key |
| `DJANGO_DEBUG` | backend | Debug mode (`True`/`False`) |
| `DJANGO_ALLOWED_HOSTS` | backend | Comma-separated allowed hosts |
| `VITE_API_URL` | frontend | Backend API base URL |

---

## Port Mapping

| Service | Container Port | Host Port |
|---|---|---|
| frontend | 3000 | 3000 |
| backend | 8000 | 8000 |
| db | 5432 | 5432 |

---

## Data Flow

```
Browser (localhost:3000)
  │
  │  HTTP requests (REST API calls via VITE_API_URL)
  ▼
Vue Router ──▶ src/views/*.vue
  │
  │  fetch / axios to http://localhost:8000/api/
  ▼
Django URL router (config/urls.py)
  │
  ▼
management/views.py (all view logic)
  │
  ▼
PostgreSQL (db service)
```
