# Driving School Management — System Design

## Overview

A full-stack web application for managing a driving school: branches, students, instructors, coordinators, agents, vehicles (with maintenance/wash tracking), groups, enrollments, payments, driving lessons, course-completion certificates, teacher reviews, holidays, and notifications. The system is composed of a Django REST backend, a Vue.js SPA frontend, a PostgreSQL database, and a Redis-backed Celery worker/beat pair for background jobs, all orchestrated via Docker Compose. The app is multi-branch and localized in Uzbek, with JWT-based phone-number login.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5.0.6, Django REST Framework 3.15 |
| Auth | djangorestframework-simplejwt (JWT, phone-based login) |
| Background jobs | Celery (worker + beat), Redis (broker/result backend) |
| Frontend | Vue 3.5, Vite 8, Vue Router 4, Pinia 3, Axios, Leaflet |
| Database | PostgreSQL 16 |
| Containerisation | Docker, Docker Compose |
| Environment | `.env` file at project root (backend/celery), `frontend/.env` (frontend) |

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                            Docker Compose                              │
│                                                                          │
│  ┌──────────────┐        ┌──────────────────────┐                      │
│  │   frontend   │        │        backend        │                      │
│  │  Vue 3/Vite  │───────▶│    Django + DRF        │                      │
│  │  port: 3000  │  JWT   │    port: 8000          │                      │
│  └──────────────┘        └──────────┬─────────────┘                      │
│                                     │                                    │
│                    ┌────────────────┼─────────────────┐                  │
│                    ▼                ▼                 ▼                  │
│           ┌───────────────┐ ┌──────────────┐ ┌──────────────────┐        │
│           │      db        │ │    redis      │ │  celery_worker /  │      │
│           │  PostgreSQL 16 │ │  (broker +    │ │   celery_beat      │      │
│           │  port: 5432    │ │  result store) │ │  (scheduled jobs)  │      │
│           └───────────────┘ └──────────────┘ └──────────────────┘        │
└────────────────────────────────────────────────────────────────────────┘
```

`celery_worker` and `celery_beat` share the backend image/codebase (mounted the same way) but run as separate containers/processes; they have no exposed host ports and talk to Postgres directly and to each other via Redis.

---

## Folder Structure

```
auto_road_mgmt/
├── system_design.md
├── .env                        # Root env vars (Postgres, Django, Vite, Celery)
├── docker-compose.yml           # db, backend, redis, celery_worker, celery_beat, frontend
│
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh            # Runs makemigrations + migrate, then starts server
│   ├── requirements.txt
│   ├── manage.py
│   ├── celerybeat-schedule       # Runtime state file written by celery beat (not source)
│   ├── media/                   # Uploaded files (cars/, passports/, users/, certificates/)
│   ├── config/
│   │   ├── settings.py          # All config from env vars; AUTH_USER_MODEL, JWT, CORS, CELERY_*
│   │   ├── celery.py             # Celery app + beat_schedule (finish_expired_groups, daily)
│   │   ├── urls.py              # /admin/, /api/, /api/auth/token/(-refresh)
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── management/              # Single Django app — all models/views/serializers
│       ├── models.py            # 16 models (see below)
│       ├── views.py             # ViewSets, soft-delete, branch filtering, role checks
│       ├── serializers.py
│       ├── admin.py
│       ├── middleware.py        # AppLanguageMiddleware (uz for app, en for /admin/)
│       ├── tasks.py              # Celery shared_task: finish_expired_groups
│       ├── urls.py              # DRF DefaultRouter registrations
│       └── migrations/          # 47 migrations
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
        │   ├── ConfirmDeleteModal.vue
        │   └── HelloWorld.vue
        ├── composables/
        │   ├── useGroupSelect.js          # Shared group-search-select state (group→student cascades)
        │   ├── useSearchSelectKeyboard.js # Arrow/enter keyboard nav for searchable dropdowns
        │   └── useFillViewportHeight.js   # Measures real available height (getBoundingClientRect) so a
        │                                   #   page's table can fill to the viewport bottom without drifting
        │                                   #   like a hardcoded calc(100vh - Npx) would
        ├── utils/formatters.js
        ├── assets/stickyTable.css         # Shared sticky-header table styling
        └── views/
            ├── HomeView.vue, LoginView.vue
            ├── StudentsView.vue, StudentDetailView.vue
            ├── UsersView.vue, UserDetailView.vue
            ├── GroupsView.vue, GroupDetailView.vue
            ├── CategoriesView.vue, CategoryDetailView.vue
            ├── AgentsView.vue, AgentDetailView.vue
            ├── CarsView.vue, CarDetailView.vue
            ├── LearningPlacesView.vue, LearningPlaceDetailView.vue
            ├── HolidaysView.vue, CertificatesView.vue
            ├── LessonsView.vue, NotificationsView.vue, PaymentsView.vue
            └── finances/
                ├── FinancesAcceptedView.vue, FinancesPaidView.vue
                ├── FinancesReturnedView.vue, FinancesBonusView.vue
                ├── FinancesBankView.vue, FinancesTeachersView.vue
                ├── FinancesInstructorsView.vue
                └── FinancesDebtsView.vue
```

---

## Data Model (`management/models.py`)

All models except `User` inherit `BaseModel` (`created_at`, `updated_at`, `is_active`, `notes`) and are soft-deleted (`is_active=False`) rather than removed from the DB.

| Model | Purpose | Key relations |
|---|---|---|
| `Branch` | Filial / school location | referenced by nearly every other model |
| `User` | Custom user, phone-number login (`AbstractUser` with `username` removed). Roles: `superuser`, `admin`, `mechanic`, `instructor`, `coordinator`, `student`. Also carries the course-completion certificate fields directly (`certificate_series`, `certificate_number`, `certificate_added_date`) | `branch` |
| `Holidays` | Official days off | `branch` |
| `Category` | License category (A, B, BC…) with price and duration | `branch` |
| `Group` | Class group of students, schedule (`working_weekends` / `selected_weekdays`), status | `branch`, `category` |
| `LearningPlace` | Physical/online learning location | `branch` |
| `Agent` | Student recruiter/referral | `branch` |
| `Enrollment` | Student ↔ Category link within a group | `branch`, `student` (User), `category`, `group`, `instructor` (User), `coordinator` (User), `agent`, `learning_place` |
| `Payment` | Payment record; statuses accepted/returned/paid/bonus/bank/**bonus_teacher**; methods cash/card/qr_code/click/transfer | `branch`, `user`, `enrollment`, `agent` |
| `Car` | Vehicle fleet; status available/repairing/not_available; insurance, inspection & oil-change tracking (`oil_change_date`, `oil_change_mileage`, `oil_change_interval_km`), currently-assigned `instructor`, `last_washed_at` | `instructor` (User) |
| `CarAssignmentHistory` | Full history of instructor↔car assignments, including oil-service state snapshot at unassignment | `car`, `instructor` (User) |
| `CarWash` | One record per car wash; `washed_at` always set server-side (never backdatable by clients) | `car`, `instructor` (User) |
| `DrivingLessons` | Practical driving lesson confirmations; also covers Avtodrom (autodrome) practice via `lesson_type` + `hours` (capped at 6h total per student) | `branch`, `student`, `instructor`, `car` |
| `Notification` | System notifications: driving lesson, certificate upload, payment, agent payment, **review** | `branch`, `user` (nullable = admin broadcast) |
| `TeacherReview` | Rating/comment a student leaves for their coordinator or instructor | `branch`, `student` (User), `teacher` (User) |
| `StudentCertificate` | Exam-pass certificate **photo** an instructor uploads for a student (distinct from `User.certificate_*`, which is the course-completion series/number) — can link to a `bonus_payment` once the instructor's bonus is paid | `branch`, `student` (User), `instructor` (User), `bonus_payment` (Payment) |

`User.save()` auto-derives `full_name` from first/last name (or vice versa), and defaults the password to the user's `jshshr` (national ID) if unset.

---

## API (`backend/config/urls.py` + `management/urls.py`)

Base path: `/api/`

| Endpoint | ViewSet | Notable custom actions |
|---|---|---|
| `/api/branches/` | `BranchViewSet` | — |
| `/api/categories/` | `CategoryViewSet` | — |
| `/api/users/` | `UserViewSet` | `/me/`, `/change-password/`; create/update/destroy restricted to superuser |
| `/api/students/` | `StudentViewSet` (User filtered to role=student) | — |
| `/api/enrollments/` | `EnrollmentViewSet` | — |
| `/api/payments/` | `PaymentViewSet` | `/{id}/pay-bonus/` — fills in the real amount on a placeholder `bonus_teacher` payment created when a certificate is uploaded (admin/superuser only) |
| `/api/groups/` | `GroupViewSet` | — |
| `/api/learning-places/` | `LearningPlaceViewSet` | — |
| `/api/agents/` | `AgentViewSet` | — |
| `/api/holidays/` | `HolidaysViewSet` | — |
| `/api/cars/` | `CarViewSet` | `/{id}/mark_washed/` — records a `CarWash`; restricted to the car's assigned instructor, a mechanic, or admin/superuser |
| `/api/driving-lessons/` | `DrivingLessonsViewSet` | — |
| `/api/notifications/` | `NotificationViewSet` | `/unread_count/`, `/{id}/mark_as_read/`, `/mark_all_read/` |
| `/api/teacher-reviews/` | `TeacherReviewViewSet` | — |
| `/api/student-certificates/` | `StudentCertificateViewSet` | — |
| `/api/auth/token/` | JWT obtain (login by `phone` + password) | — |
| `/api/auth/token/refresh/` | JWT refresh | — |
| `/admin/` | Django admin (English locale) | — |

Cross-cutting behavior in `views.py`:
- **Soft delete**: `SoftDeleteModelViewSet.destroy()` sets `is_active=False` instead of deleting rows.
- **Branch scoping**: `filter_by_branch()` lets any list endpoint be filtered via `?branch=<id|name>`, always including branch-less rows.
- **Role-gated writes**: creation of holidays/categories/students/groups/learning-places/agents/payments and all user writes require `admin`/`superuser`/`is_superuser` (`is_admin_or_superuser()` helper); user CRUD is superuser-only.
- **Pagination**: `StandardPagination` — 50/page, up to 1000 via `page_size`.
- Rich query filters per resource (search, status, category, instructor/coordinator/agent, date range, jshshr, etc.), plus `?ordering=` on students/groups/payments for group start/end date and payment date sorting — students without a group (or payments without one) sort last regardless of direction (`nulls_last`).

---

## Background Jobs (Celery)

- **Broker/result backend**: Redis (`redis` service, no host port exposed).
- **`celery_worker`**: runs `celery -A config worker`, executes tasks from `management/tasks.py`.
- **`celery_beat`**: runs `celery -A config beat`, drives the schedule defined in `config/celery.py`. Its on-disk schedule state (`backend/celerybeat-schedule`) is runtime data, not source — rewritten on every beat start/tick.
- **`finish_expired_groups`** (daily, 00:05): any `started` group whose `ends_at` has passed is marked `finished`, and its still-`enrolled` students are moved to `finished` for that group — the same two updates an admin would otherwise make by hand once a course's schedule runs out.

---

## Auth Flow

1. Frontend posts `{ phone, password }` to `/api/auth/token/` (SimpleJWT, `AUTH_FIELD_NAME="phone"`).
2. Access token (1h) + refresh token (10d, rotated on every use — effectively a 10-day *sliding* session) stored in `localStorage` (if "remember me") or `sessionStorage`.
3. `services/api.js`: a request interceptor attaches `Authorization: Bearer <token>` to every request and injects the active branch as a `?branch=` query param on GET requests. A response interceptor transparently exchanges the refresh token for a new access token on the first `401` and retries the original request once (concurrent 401s during a refresh share the single in-flight refresh call instead of each racing their own); if the refresh token itself is invalid/expired, it clears stored tokens and redirects to `/login`. Without this, the access token expiring after an hour would silently 401 every request from then on with no way to recover short of a manual page reload.
4. `stores/auth.js` (Pinia) exposes `isAuthenticated`, `isSuperuser`, `isAdminOrSuperuser`, `isStaff`, `isMechanic`, `isStudent` getters and calls `/users/me/` to hydrate the current user. Any authenticated user can self-service a password change via `/users/change-password/`.
5. Router guard (`router/index.js`) redirects unauthenticated users to `/login`, and force-redirects authenticated `student` role users to their own `student-detail` page regardless of navigation target.

---

## Multi-Branch Handling

`stores/branch.js` holds the active branch (persisted to `localStorage`, default `"autoroad school"`), fetched from `/api/branches/`. The active branch is auto-appended to outbound GET requests by the axios interceptor, and the backend's `filter_by_branch()` always includes branch-less (`branch=null`) records alongside the matched branch so shared/global data stays visible.

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `POSTGRES_DB` | db, backend, celery_worker, celery_beat | Database name |
| `POSTGRES_USER` | db, backend, celery_worker, celery_beat | Database user |
| `POSTGRES_PASSWORD` | db, backend, celery_worker, celery_beat | Database password |
| `POSTGRES_HOST` | backend, celery_worker, celery_beat | DB hostname (`db` service name) |
| `POSTGRES_PORT` | backend, celery_worker, celery_beat | DB port (default `5432`) |
| `DJANGO_SECRET_KEY` | backend, celery_worker, celery_beat | Django secret key |
| `DJANGO_DEBUG` | backend, celery_worker, celery_beat | Debug mode (`True`/`False`) |
| `DJANGO_ALLOWED_HOSTS` | backend, celery_worker, celery_beat | Comma-separated allowed hosts |
| `CELERY_BROKER_URL` | backend, celery_worker, celery_beat | Redis broker URL (default `redis://redis:6379/0`) |
| `CELERY_RESULT_BACKEND` | backend | Redis result backend (defaults to `CELERY_BROKER_URL`) |
| `VITE_API_URL` | frontend | Backend API base URL |

CORS is restricted to `http://localhost:3000` / `http://127.0.0.1:3000` with credentials allowed. Localization: Uzbek (`uz`) for the app, English for `/admin/`, via `AppLanguageMiddleware`.

---

## Port Mapping

| Service | Container Port | Host Port |
|---|---|---|
| frontend | 3000 | 3000 |
| backend | 8000 | 8000 |
| db | 5432 | 5432 |
| redis | 6379 | *(not exposed to host)* |
| celery_worker | — | *(no exposed port)* |
| celery_beat | — | *(no exposed port)* |

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
  ├──▶ PostgreSQL (db service)
  │
  └──▶ Redis (broker) ──▶ celery_worker (executes tasks) ◀── celery_beat (schedules tasks)
```

---

## Notable Implementation Details

- **No hard deletes**: every resource is soft-deleted via `is_active`; list endpoints filter `is_active=True`.
- **Uploaded media**: served from `/media/` in debug mode; car photos (`media/cars/`), user photos (`media/users/`), passport scans (`media/passports/`), exam-pass certificate photos (`media/certificates/`).
- **Two distinct "certificate" concepts**: `User.certificate_series`/`certificate_number` is the course-completion certificate (series+number, no image, editable via a dedicated small modal on `HomeView`, `StudentDetailView`, `GroupDetailView`, `UserDetailView`, and the standalone `/certificates` (`CertificatesView`) admin listing); `StudentCertificate` is a separate exam-pass certificate **photo** upload, tied to the uploading instructor and optionally to a bonus `Payment`.
- **Reusable group→student cascade**: the "pick a group, then search a student within it" pattern (used by payment, certificate, and lesson-add modals) is centralized in the `useGroupSelect` composable; keyboard navigation for these searchable dropdowns is centralized in `useSearchSelectKeyboard`.
- **Dev-mode entrypoint**: `backend/entrypoint.sh` runs `makemigrations` + `migrate` on every container start before launching the dev server — fine for development, but should be replaced with a controlled migration step for production.
- **Password defaulting**: if a `User` is created without a password, it defaults to their `jshshr` (national ID number) — a convenience for bulk-importing students that should be revisited before production use.
- **Background scheduling**: group lifecycle transitions (auto-finishing expired groups) run out-of-band via Celery Beat rather than being computed on read, so the "finished" status is guaranteed fresh no later than the next daily tick even without any user visiting the page.
