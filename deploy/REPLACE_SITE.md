# Replace old Django site on VPS (Nginx + Gunicorn) with a new project

Use this when **HTTPS and DNS already work** and you want to **fully replace** the deployed app with your new local project (the one you run with `runserver` at `127.0.0.1:8000`).

**Variables** — substitute everywhere:

| Variable | Example (this repo) | Your value |
|----------|---------------------|------------|
| `APP_DIR` | `/var/www/codecraften` | Directory on VPS for the project |
| `DOMAIN` | `codecraften.com` | Your domain |
| `WSGI_MODULE` | `myproject.wsgi:application` | `package.wsgi:application` |
| `GUNICORN_SERVICE` | `gunicorn-codecraften` | Any name, e.g. `gunicorn-myapp` |
| `NGINX_SITE` | `codecraften` | Filename under `sites-available` |

Run long commands on the VPS over **SSH** as `root` or with `sudo`.

---

## 1. Safely remove or back up the old project

### Option A — Full backup (recommended)

```bash
sudo tar -czvf ~/old-site-backup-$(date +%F).tar.gz /var/www/OLD_PROJECT_DIR
```

Replace `OLD_PROJECT_DIR` with the real folder name (e.g. `codecraften`, `django_app`).

### Option B — Database backup (PostgreSQL)

```bash
sudo -u postgres pg_dump OLD_DB_NAME > ~/old-db-$(date +%F).sql
```

### Stop the old app (avoid 502 during file swap)

```bash
sudo systemctl stop gunicorn-codecraften   # use your actual old unit name
# List units if unsure:
# systemctl list-units --type=service | grep -i gunicorn
```

### Remove old code (after backup)

**If the new app will use the *same* directory** (e.g. still `APP_DIR`):

```bash
sudo rm -rf /var/www/codecraften/*
sudo rm -rf /var/www/codecraften/.[!.]* 2>/dev/null || true   # dotfiles like .git, .env — careful
```

**Safer:** rename old folder, then create fresh:

```bash
sudo mv /var/www/codecraften /var/www/codecraften.old-$(date +%F)
sudo mkdir -p /var/www/codecraften
sudo chown $USER:$USER /var/www/codecraften   # or www-data if you deploy as that user
```

Update **Nginx** `alias` and **Gunicorn** `WorkingDirectory` to `APP_DIR` if you changed the path.

---

## 2. Upload the new project (Git or SCP)

### Git (recommended)

```bash
cd /var/www
sudo rm -rf codecraften   # only if empty / you chose fresh dir
sudo git clone https://github.com/YOU/YOUR_REPO.git codecraften
sudo chown -R www-data:www-data /var/www/codecraften
# If you deploy as a deploy user:
# sudo chown -R deploy:deploy /var/www/codecraften
```

Use **SSH deploy key** or **private repo** token as needed.

### SCP from your Windows PC (PowerShell)

From the folder **containing** your project (parent of `manage.py`):

```powershell
scp -r .\* root@YOUR_VPS_IP:/var/www/codecraften/
```

Better: push to Git and clone on the server (cleaner, no missing hidden files).

**Ensure on the server:** `manage.py`, `myproject/`, `api/`, `requirements.txt`, `templates/`, `static/`, etc.

---

## 3. Python virtual environment

```bash
cd /var/www/codecraften
sudo -u www-data python3 -m venv .venv
# If files owned by you:
# python3 -m venv .venv
sudo chown -R www-data:www-data /var/www/codecraften/.venv
```

---

## 4. Install dependencies

```bash
cd /var/www/codecraften
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

If `psycopg2-binary` fails, install: `sudo apt install -y libpq-dev python3-dev`.

---

## 5. Django production settings (`.env`)

Create `/var/www/codecraften/.env` (same folder as `manage.py`):

```env
SECRET_KEY=your-new-long-random-secret-never-commit
DEBUG=False
ALLOWED_HOSTS=codecraften.com,www.codecraften.com
CSRF_TRUSTED_ORIGINS=https://codecraften.com,https://www.codecraften.com

# PostgreSQL example:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

Generate `SECRET_KEY`:

```bash
cd /var/www/codecraften && source .venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
deactivate
```

**Static / media** (your `settings.py` should already have):

- `STATIC_ROOT`, `STATIC_URL`, `STATICFILES_DIRS` (or WhiteNoise)
- `MEDIA_ROOT`, `MEDIA_URL`

Lock down `.env`:

```bash
sudo chmod 640 /var/www/codecraften/.env
sudo chown root:www-data /var/www/codecraften/.env
# Adjust if Gunicorn runs as www-data and decouple reads .env from cwd — ensure www-data can read:
# sudo chown www-data:www-data /var/www/codecraften/.env && sudo chmod 640 /var/www/codecraften/.env
```

---

## 6. Migrations and collectstatic

```bash
cd /var/www/codecraften
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)   # optional; decouple reads .env automatically from cwd
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py createsuperuser      # optional
deactivate
```

```bash
sudo mkdir -p /var/www/codecraften/media
sudo chown -R www-data:www-data /var/www/codecraften/media /var/www/codecraften/staticfiles
```

---

## 7. Gunicorn (systemd)

Edit or create `/etc/systemd/system/gunicorn-codecraften.service`:

```ini
[Unit]
Description=Gunicorn for Django (new site)
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/codecraften
Environment=PATH=/var/www/codecraften/.venv/bin
RuntimeDirectory=gunicorn
RuntimeDirectoryMode=0755
ExecStart=/var/www/codecraften/.venv/bin/gunicorn \
    --workers 3 \
    --timeout 120 \
    --bind unix:/run/gunicorn/gunicorn.sock \
    myproject.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Change** `WorkingDirectory`, `ExecStart` paths, and `myproject.wsgi:application` to match your project.

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-codecraften
sudo systemctl start gunicorn-codecraften
sudo systemctl status gunicorn-codecraften --no-pager
```

---

## 8. Nginx — point to new project

Your **socket** must match Gunicorn: `unix:/run/gunicorn/gunicorn.sock`.

**Media** path must match `MEDIA_ROOT` on disk, e.g.:

```nginx
upstream django_app {
    server unix:/run/gunicorn/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;
    server_name codecraften.com www.codecraften.com;

    client_max_body_size 20M;

    location /media/ {
        alias /var/www/codecraften/media/;
    }

    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Certbot usually adds **443** blocks — keep `server_name` and `proxy_pass` / `alias` consistent.

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 9. Restart services

```bash
sudo systemctl restart gunicorn-codecraften
sudo systemctl restart nginx
```

Check:

```bash
sudo systemctl status gunicorn-codecraften --no-pager
curl -sI https://codecraften.com | head -5
```

---

## 10. Verify the new site is live

- Browser: `https://YOUR_DOMAIN` (incognito).
- Logs:

```bash
sudo journalctl -u gunicorn-codecraften -n 80 --no-pager
sudo tail -n 50 /var/log/nginx/error.log
```

- Django sanity (on server):

```bash
cd /var/www/codecraften && source .venv/bin/activate
python manage.py check --deploy
deactivate
```

---

## Common mistakes to avoid

| Mistake | Why it hurts |
|--------|----------------|
| `DEBUG=True` in production | Security risk, wrong error pages |
| Wrong `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` | 400 / CSRF failures on forms |
| Gunicorn `WorkingDirectory` not where `manage.py` and `.env` live | App won’t load settings / DB |
| Socket path mismatch (Nginx vs Gunicorn `--bind`) | **502** |
| Old Gunicorn still running on same socket | Stale/old code or crash |
| Forgot `collectstatic` | Missing CSS/JS (often 404 on static) |
| `www-data` cannot read `.env` or `media/` | Crashes or 403 on uploads |
| Only replaced code, not **restarted** Gunicorn | Still serving old workers |

---

## Debug: 502 Bad Gateway

1. **Gunicorn running?**  
   `sudo systemctl status gunicorn-codecraften`

2. **Socket exists and permissions?**  
   `ls -la /run/gunicorn/`

3. **Nginx error log:**  
   `sudo tail -f /var/log/nginx/error.log`

4. **Gunicorn journal:**  
   `sudo journalctl -u gunicorn-codecraften -f`

5. **Run Gunicorn manually** (stop service first) to see traceback:

```bash
cd /var/www/codecraften
sudo -u www-data ./.venv/bin/gunicorn myproject.wsgi:application --bind unix:/tmp/test.sock
```

---

## Debug: Static files not loading

1. Run `python manage.py collectstatic --noinput` again.
2. If using **WhiteNoise**, static is served by Django/Gunicorn — no separate Nginx `location /static/` required unless you configured it.
3. If Nginx serves `/static/`, `alias` must point to `STATIC_ROOT` (e.g. `staticfiles/`).
4. `DEBUG=False` — browser hard refresh (Ctrl+F5).

---

## Quick checklist

- [ ] Backup old site + DB  
- [ ] Stop old Gunicorn  
- [ ] New code in `APP_DIR`  
- [ ] `.venv` + `pip install -r requirements.txt`  
- [ ] `.env` with `DEBUG=False`, hosts, DB  
- [ ] `migrate` + `collectstatic`  
- [ ] `media/` + `staticfiles/` ownership `www-data`  
- [ ] systemd unit paths + `WSGI_MODULE` correct  
- [ ] Nginx `proxy_pass` + `/media/` paths correct  
- [ ] `systemctl restart` gunicorn + nginx  
- [ ] `curl -I https://DOMAIN` → 200  

---

Repo copies of examples: `deploy/gunicorn.service.example`, `deploy/nginx-codecraften.conf.example`, `deploy/env.production.example`.
