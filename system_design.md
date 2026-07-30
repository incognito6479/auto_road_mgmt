# Driving School Management — System Design

## Overview

A full-stack web application for managing a driving school: branches, students, instructors, coordinators, agents, vehicles, groups, enrollments, payments, lessons, holidays, and notifications. The system is composed of a Django REST backend, a Vue.js SPA frontend, and a PostgreSQL database, all orchestrated via Docker Compose. The app is multi-branch and localized in Uzbek, with JWT-based phone-number login.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5.0.6, Django REST Framework 3.15 |
| Auth | djangorestframework-simplejwt (JWT, phone-based login) |
| Frontend | Vue 3.5, Vite 8, Vue Router 4, Pinia 3, Axios, Leaflet |
| Database | PostgreSQL 16 |
| Containerisation | Docker, Docker Compose |
| Environment | `.env` file at project root (backend), `frontend/.env` (frontend) |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
│                                                                │
│  ┌──────────────┐        ┌──────────────────────┐            │
│  │   frontend   │        │        backend        │            │
│  │  Vue 3/Vite  │───────▶│    Django + DRF        │            │
│  │  port: 3000  │  JWT   │    port: 8000          │            │
│  └──────────────┘        └──────────┬─────────────┘            │
│                                     │                          │
│                           ┌─────────▼───────────┐              │
│                           │         db           │              │
│                           │     PostgreSQL 16     │              │
│                           │     port: 5432         │              │
│                           └───────────────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
auto_road_mgmt/
├── system_design.md
├── .env                        # Root env vars (Postgres, Django, Vite)
├── docker-compose.yml
│
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh            # Runs makemigrations + migrate, then starts server
│   ├── requirements.txt
│   ├── manage.py
│   ├── media/                   # Uploaded files (cars/, passports/, users/)
│   ├── config/
│   │   ├── settings.py          # All config from env vars; AUTH_USER_MODEL, JWT, CORS
│   │   ├── urls.py              # /admin/, /api/, /api/auth/token/(-refresh)
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── management/              # Single Django app — all models/views/serializers
│       ├── models.py            # 12 models (see below)
│       ├── views.py             # ViewSets, soft-delete, branch filtering, role checks
│       ├── serializers.py
│       ├── admin.py
│       ├── middleware.py        # AppLanguageMiddleware (uz for app, en for /admin/)
│       ├── urls.py              # DRF DefaultRouter registrations
│       └── migrations/          # 33 migrations
│
└── frontend/
    ├── Dockerfile
    ├── .env                     # VITE_API_URL
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/index.js      # Auth guards, student self-redirect
        ├── services/api.js      # Axios instance, JWT + active-branch injection
        ├── stores/
        │   ├── auth.js          # Pinia: login/logout, role getters
        │   └── branch.js        # Pinia: active branch selection (multi-branch UI)
        ├── components/
        │   ├── AppLayout.vue
        │   └── HelloWorld.vue
        ├── utils/formatters.js
        └── views/
            ├── HomeView.vue, LoginView.vue
            ├── StudentsView.vue, StudentDetailView.vue
            ├── UsersView.vue, UserDetailView.vue
            ├── GroupsView.vue, GroupDetailView.vue
            ├── CategoriesView.vue, CategoryDetailView.vue
            ├── AgentsView.vue, AgentDetailView.vue
            ├── CarsView.vue, CarDetailView.vue
            ├── LearningPlacesView.vue, HolidaysView.vue
            ├── LessonsView.vue, NotificationsView.vue
            └── finances/
                ├── FinancesAcceptedView.vue, FinancesPaidView.vue
                ├── FinancesReturnedView.vue, FinancesBonusView.vue
                ├── FinancesBankView.vue, FinancesTeachersView.vue
                └── FinancesDebtsView.vue
```

---

## Data Model (`management/models.py`)

All models except `User` inherit `BaseModel` (`created_at`, `updated_at`, `is_active`, `notes`) and are soft-deleted (`is_active=False`) rather than removed from the DB.

| Model | Purpose | Key relations |
|---|---|---|
| `Branch` | Filial / school location | referenced by nearly every other model |
| `User` | Custom user, phone-number login (`AbstractUser` with `username` removed). Roles: `superuser`, `admin`, `mechanic`, `instructor`, `coordinator`, `student` | `branch` |
| `Holidays` | Official days off | `branch` |
| `Category` | License category (A, B, BC…) with price and duration | `branch` |
| `Group` | Class group of students, schedule (`working_weekends`), status | `branch`, `category` |
| `LearningPlace` | Physical/online learning location | `branch` |
| `Agent` | Student recruiter/referral | `branch` |
| `Enrollment` | Student ↔ Category link within a group | `branch`, `student` (User), `category`, `group`, `instructor` (User), `coordinator` (User), `agent`, `learning_place` |
| `Payment` | Payment record; statuses accepted/returned/paid/bonus/bank; methods cash/card/qr/transfer | `branch`, `user`, `enrollment`, `agent` |
| `Car` | Vehicle fleet; status available/repairing/not_available; insurance & inspection dates | — |
| `DrivingLessons` | Practical driving lesson confirmations | `branch`, `student`, `instructor`, `car` |
| `Notification` | System notifications (driving lesson, certificate upload, payment, agent payment) | `branch`, `user` (nullable = admin broadcast) |

`User.save()` auto-derives `full_name` from first/last name (or vice versa), and defaults the password to the user's `jshshr` (national ID) if unset.

---

## API (`backend/config/urls.py` + `management/urls.py`)

Base path: `/api/`

| Endpoint | ViewSet |
|---|---|
| `/api/branches/` | `BranchViewSet` |
| `/api/categories/` | `CategoryViewSet` |
| `/api/users/` (+ `/users/me/`) | `UserViewSet` |
| `/api/students/` | `StudentViewSet` (User filtered to role=student) |
| `/api/enrollments/` | `EnrollmentViewSet` |
| `/api/payments/` | `PaymentViewSet` |
| `/api/groups/` | `GroupViewSet` |
| `/api/learning-places/` | `LearningPlaceViewSet` |
| `/api/agents/` | `AgentViewSet` |
| `/api/holidays/` | `HolidaysViewSet` |
| `/api/cars/` | `CarViewSet` |
| `/api/driving-lessons/` | `DrivingLessonsViewSet` |
| `/api/notifications/` (+ `/unread_count/`, `/mark_as_read/`, `/mark_all_read/`) | `NotificationViewSet` |
| `/api/auth/token/` | JWT obtain (login by `phone` + password) |
| `/api/auth/token/refresh/` | JWT refresh |
| `/admin/` | Django admin (English locale) |

Cross-cutting behavior in `views.py`:
- **Soft delete**: `SoftDeleteModelViewSet.destroy()` sets `is_active=False` instead of deleting rows.
- **Branch scoping**: `filter_by_branch()` lets any list endpoint be filtered via `?branch=<id|name>`, always including branch-less rows.
- **Role-gated writes**: creation of holidays/categories/students/groups/learning-places/agents/payments and all user writes require `admin`/`superuser`/`is_superuser` (`is_admin_or_superuser()` helper); user CRUD is superuser-only.
- **Pagination**: `StandardPagination` — 50/page, up to 1000 via `page_size`.
- Rich query filters per resource (search, status, category, instructor/coordinator/agent, date range, jshshr, etc.).

---

## Auth Flow

1. Frontend posts `{ phone, password }` to `/api/auth/token/` (SimpleJWT, `AUTH_FIELD_NAME="phone"`).
2. Access token (1h) + refresh token (7d, rotated) stored in `localStorage` (if "remember me") or `sessionStorage`.
3. `services/api.js` axios interceptor attaches `Authorization: Bearer <token>` to every request, and injects the active branch as a `?branch=` query param on GET requests.
4. `stores/auth.js` (Pinia) exposes `isAuthenticated`, `isSuperuser`, `isAdminOrSuperuser`, `isStaff`, `isMechanic`, `isStudent` getters and calls `/users/me/` to hydrate the current user.
5. Router guard (`router/index.js`) redirects unauthenticated users to `/login`, and force-redirects authenticated `student` role users to their own `student-detail` page regardless of navigation target.

---

## Multi-Branch Handling

`stores/branch.js` holds the active branch (persisted to `localStorage`, default `"autoroad school"`), fetched from `/api/branches/`. The active branch is auto-appended to outbound GET requests by the axios interceptor, and the backend's `filter_by_branch()` always includes branch-less (`branch=null`) records alongside the matched branch so shared/global data stays visible.

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

CORS is restricted to `http://localhost:3000` / `http://127.0.0.1:3000` with credentials allowed. Localization: Uzbek (`uz`) for the app, English for `/admin/`, via `AppLanguageMiddleware`.

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
  │  HTTP requests, JWT bearer + active-branch query param
  ▼
Vue Router (auth guard) ──▶ src/views/*.vue ──▶ Pinia stores (auth, branch)
  │
  │  axios (services/api.js) → http://localhost:8000/api/
  ▼
Django URL router (config/urls.py → management/urls.py)
  │
  ▼
management/views.py (ViewSets: soft-delete, branch filter, role checks, pagination)
  │
  ▼
PostgreSQL (db service)
```

---

## Notable Implementation Details

- **No hard deletes**: every resource is soft-deleted via `is_active`; list endpoints filter `is_active=True`.
- **Uploaded media**: served from `/media/` in debug mode; car photos (`media/cars/`), user photos (`media/users/`), passport scans (`media/passports/`).
- **Dev-mode entrypoint**: `backend/entrypoint.sh` runs `makemigrations` + `migrate` on every container start before launching the dev server — fine for development, but should be replaced with a controlled migration step for production.
- **Password defaulting**: if a `User` is created without a password, it defaults to their `jshshr` (national ID number) — a convenience for bulk-importing students that should be revisited before production use.
