# IT Solutions - Django Project

A production-ready Django project with custom admin panel and user-facing website.

## Folder Structure

```
frontend/myproject/
├── api/                    # Main app (models, views, forms, urls)
├── myproject/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   ├── user/               # User site assets (css, js, img, fonts)
│   └── admin/              # Admin panel assets
├── templates/
│   ├── user_site/          # User-facing pages
│   └── admin_panel/        # Custom admin panel templates
├── media/                  # User uploads (created on first upload)
├── staticfiles/            # Collected static (created by collectstatic)
├── requirements.txt
├── .env                    # Environment variables (create from .env.example)
└── .env.example
```

## Quick Start

### 1. Virtual Environment

```bash
cd frontend/myproject
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/Mac
```

Edit `.env` and set a secure `SECRET_KEY` for production.

### 4. Database Migrations

```bash
python manage.py migrate
```

### 5. Create Admin User (Staff)

```bash
python manage.py createsuperuser
```

**Important:** When prompted, set `is_staff=True` (it's the default for superuser). Staff users can access the custom admin panel at `/admin-panel/`.

### 6. Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server

```bash
python manage.py runserver
```

- **User site:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin-panel/
- **Admin login:** http://127.0.0.1:8000/admin-panel/login/
- **Django admin:** http://127.0.0.1:8000/django-admin/

## Environment Variables (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | (required) |
| DEBUG | Enable debug mode | True |
| ALLOWED_HOSTS | Comma-separated hosts | localhost,127.0.0.1 |
| DB_ENGINE | Database engine | django.db.backends.sqlite3 |
| DB_NAME | Database name/path | db.sqlite3 |

## Features

### User Site
- Home pages (index-1, index-2, index-3)
- About, Services, Case Study, Blog, FAQ, Team, Contact
- Contact form with validation (submits to backend)
- All static assets served via Django

### Admin Panel (Custom)
- Login / Logout
- Dashboard with stats
- **Services:** Create, Edit, Delete
- **Portfolio:** Create, Edit, Delete
- **Blog Posts:** Create, Edit, Delete
- **Testimonials:** Create, Edit, Delete
- **Messages:** View contact form submissions, Mark read, Delete

### Security
- CSRF protection on all forms
- Staff-only access for admin panel
- python-decouple for secrets
- Production security settings when DEBUG=False

## Deployment Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Set a strong `SECRET_KEY` (50+ chars)
- [ ] Set `ALLOWED_HOSTS` to your domain(s)
- [ ] Configure database (PostgreSQL recommended)
- [ ] Run `collectstatic` before deploy
- [ ] Use HTTPS (CSRF_COOKIE_SECURE, SESSION_COOKIE_SECURE)
- [ ] Set up media file serving (e.g. S3, nginx)
- [ ] Configure WSGI/ASGI server (gunicorn, uvicorn)

## Commands Summary

```bash
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# Database
python manage.py migrate
python manage.py createsuperuser

# Static (production)
python manage.py collectstatic --noinput

# Run
python manage.py runserver
```
