# Almaviva / Italian Embassy Visa Automation System

A production-grade, containerized automated appointment reservation assistant designed for the Italian Embassy / Almaviva Visa Portal. Built with Django REST Framework, Celery, Redis, PostgreSQL, Selenium (Chromium), and React 19 SPA with Tailwind CSS served via Nginx reverse proxy.

---

## 🏗️ Architecture Overview

The system runs as an isolated, resilient 5-tier containerized stack via Docker Compose:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 Nginx Reverse Proxy                    │
                  │             (Port 80: React SPA + Proxy)               │
                  └───────────────┬────────────────────────┬───────────────┘
                                  │                        │
                    Static & SPA  │                        │ /api/*, /admin/*
                                  ▼                        ▼
                     [ React 19 Frontend ]        [ Django Backend (Gunicorn) ]
                                                           │
                                          ┌────────────────┴────────────────┐
                                          ▼                                 ▼
                                 [ PostgreSQL 16 ]                    [ Redis 7 ]
                                                                            │
                                                                            ▼
                                                                 [ Celery Automation Worker ]
                                                                 (Chromium + Selenium Engine)
```

### Stack Components:
1. **`visa_bot_frontend`**: React 19 SPA built with Vite and Tailwind CSS, served by high-performance Alpine Nginx. Handles reverse proxying for `/api/`, `/admin/`, `/media/`, and `/static/`.
2. **`visa_bot_backend`**: Django REST API running with Gunicorn WSGI workers, managing bookings, Excel processing, authentication, and task dispatching.
3. **`visa_bot_worker`**: Celery worker executing browser automation via headless Chromium and Chromedriver with human-in-the-loop challenge resolution.
4. **`visa_bot_postgres`**: PostgreSQL 16 relational database with persistent named volume `postgres_data`.
5. **`visa_bot_redis`**: Redis 7 in-memory broker for Celery task queuing and caching with persistent named volume `redis_data`.

---

## 🚀 Quick Start

### 1. Prerequisites
- Docker Engine 24+ & Docker Compose v2+
- Port `80` (or configured `HTTP_PORT`) free on host

### 2. Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```
Ensure `.env` contains your secure database and secret key credentials.

### 3. Build & Run
```bash
# Build and launch all 5 containers in background
docker compose up -d --build

# Verify container health status
docker compose ps
```

All 5 services should report `Up (healthy)`.

---

## 🔑 Default Administrator Credentials

A Django superuser has been provisioned:

- **URL**: [http://localhost/admin/](http://localhost/admin/)
- **Frontend Dashboard**: [http://localhost/](http://localhost/)
- **Username**: `admin`
- **Password**: `AdminPassword2026!`
- **Email**: `admin@almaviva-bot.local`

To create or reset a superuser at any time:
```bash
docker compose exec backend python manage.py createsuperuser
# Or programmatically:
docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; u = get_user_model().objects.get(username='admin'); u.set_password('YourNewPassword'); u.save()"
```

---

## 🌐 Web Endpoints

| Path | Purpose | Upstream Target |
| :--- | :--- | :--- |
| `http://localhost/` | React SPA Web Dashboard | `visa_bot_frontend` (Nginx) |
| `http://localhost/admin/` | Django Admin Management Panel | `visa_bot_backend:8000` |
| `http://localhost/api/auth/login/` | JWT / Session Authentication | `visa_bot_backend:8000` |
| `http://localhost/api/dashboard/stats/` | Real-time Dashboard KPI & Stats | `visa_bot_backend:8000` |
| `http://localhost/api/bookings/` | Customer & Booking CRUD | `visa_bot_backend:8000` |
| `http://localhost/api/bookings/<id>/start/` | Dispatch Booking Automation | `visa_bot_backend:8000` |
| `http://localhost/api/bookings/<id>/status/` | Real-time Step Progress & Status | `visa_bot_backend:8000` |
| `http://localhost/api/excel/preview/` | 2-Stage Excel Import Preview | `visa_bot_backend:8000` |
| `http://localhost/api/excel/confirm/` | Commit Excel Data to Database | `visa_bot_backend:8000` |
| `http://localhost/api/excel/template/` | Download Standard Excel Template | `visa_bot_backend:8000` |

---

## ⚙️ Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *(Django secret key)* | Django encryption and session secret key |
| `DEBUG` | `False` | Debug mode (`False` in production) |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,backend,frontend,*` | Permitted hostnames |
| `DATABASE_URL` | `postgres://postgres:password@postgres:5432/visa_bot` | PostgreSQL connection URL |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Redis Celery broker connection URL |
| `SELENIUM_HEADLESS` | `true` | Runs Chromium headless inside container |
| `CHROME_BIN` | `/usr/bin/chromium` | Container Linux Chromium binary path |
| `CHROMEDRIVER_PATH` | `/usr/bin/chromedriver` | Container Linux Chromedriver binary path |
| `BOT_SIMULATION_MODE` | `false` | When `true`, runs simulation workflow without real browser |
| `HTTP_PORT` | `80` | Host port exposed for web frontend |

---

## 🛡️ Human-In-The-Loop & Security Challenge Handling

In compliance with official visa portal policies:
- The automation engine **never bypasses CAPTCHAs, OTPs, or anti-bot protections**.
- When an OTP or CAPTCHA challenge is encountered, the worker transitions the booking to:
  ```json
  {
    "status": "WAITING_FOR_USER",
    "action_required": "Please enter the OTP verification code sent to your registered mobile phone or solve the security challenge",
    "last_screenshot": "/media/screenshots/challenge_<id>.png"
  }
  ```
- The user can inspect the live screenshot directly in the React Dashboard, enter the required response or solve the challenge, and click **Resume**.
- The automation worker picks up the session seamlessly without restarting from scratch.

---

## 🛠️ Management Commands & Operations

### View Container Logs
```bash
# View all logs
docker compose logs -f

# View backend API logs
docker compose logs -f backend

# View Celery automation worker logs
docker compose logs -f worker
```

### Apply Database Migrations Manually
```bash
docker compose exec backend python manage.py migrate
```

### Run Django Automated Test Suite
```bash
docker compose exec backend python manage.py test
```

### Stop & Restart Services
```bash
# Stop all services (preserves volumes)
docker compose down

# Stop and wipe volumes (caution: removes data)
docker compose down -v

# Restart a specific service
docker compose restart worker
```

### Production Deployment Profile
```bash
docker compose -f docker-compose.yml -f compose.prod.yml up -d --build
```
This enables CPU / Memory limits (2.0 CPUs / 2GB RAM for worker, 1.0 CPU / 1GB RAM for backend) and JSON file log rotation (10m max size, 3 files).
