# Deploy CodeCraften (Django) on Hostinger VPS — Ubuntu 24.04

Use this after **DNS** points `codecraften.com` and `www.codecraften.com` to your VPS IP (A records).

Replace `/var/www/codecraften` if you use another folder. Run commands on the **VPS as root** (or prefix with `sudo`).

---

## 1. System packages

```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-dev python3-pip build-essential nginx postgresql postgresql-contrib git certbot python3-certbot-nginx
```

---

## 2. PostgreSQL — database and user

Pick your own password and keep it secret.

```bash
sudo -u postgres psql -c "CREATE USER codecraften_user WITH PASSWORD 'YOUR_STRONG_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE codecraften_db OWNER codecraften_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE codecraften_db TO codecraften_user;"
sudo -u postgres psql -c "ALTER DATABASE codecraften_db OWNER TO codecraften_user;"
```

For Django migrations with PostgreSQL 15+ you may need:

```bash
sudo -u postgres psql -d codecraften_db -c "GRANT ALL ON SCHEMA public TO codecraften_user;"
```

---

## 3. App directory and code

```bash
mkdir -p /var/www/codecraften
chown -R $SUDO_USER:$SUDO_USER /var/www/codecraften   # if not root, adjust
```

Copy your project here (example with Git):

```bash
cd /var/www
git clone YOUR_REPO_URL codecraften
cd codecraften
```

---

## 4. Virtualenv and Python deps

```bash
cd /var/www/codecraften
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Production `.env`

In `/var/www/codecraften/.env` (same folder as `manage.py`):

```env
SECRET_KEY=generate-a-new-50-char-random-string
DEBUG=False
ALLOWED_HOSTS=codecraften.com,www.codecraften.com
CSRF_TRUSTED_ORIGINS=https://codecraften.com,https://www.codecraften.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=codecraften_db
DB_USER=codecraften_user
DB_PASSWORD=YOUR_STRONG_PASSWORD
DB_HOST=localhost
DB_PORT=5432
```

Generate `SECRET_KEY`:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

(Install Django once in venv first, or use any long random string.)

**HTTP-only test (before SSL):** temporarily add:

`CSRF_TRUSTED_ORIGINS=http://codecraften.com,http://www.codecraften.com,http://YOUR_VPS_IP`

Remove duplicate `http` entries after HTTPS works.

---

## 6. Django commands

```bash
cd /var/www/codecraften
source .venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

## 7. Permissions

```bash
chown -R www-data:www-data /var/www/codecraften/media /var/www/codecraften/staticfiles
chmod -R 755 /var/www/codecraften/media
```

---

## 8. Gunicorn (systemd)

Copy the example unit and edit paths if needed:

```bash
sudo cp deploy/gunicorn.service.example /etc/systemd/system/gunicorn-codecraften.service
sudo nano /etc/systemd/system/gunicorn-codecraften.service   # check paths
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-codecraften
sudo systemctl status gunicorn-codecraften
```

---

## 9. Nginx

```bash
sudo cp deploy/nginx-codecraften.conf.example /etc/nginx/sites-available/codecraften
sudo ln -sf /etc/nginx/sites-available/codecraften /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

## 10. HTTPS (Let’s Encrypt)

```bash
sudo certbot --nginx -d codecraften.com -d www.codecraften.com
```

After SSL works, ensure `.env` has only `https://` in `CSRF_TRUSTED_ORIGINS`, then:

```bash
sudo systemctl restart gunicorn-codecraften
```

---

## 11. Firewall

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
ufw status
```

---

## Troubleshooting

- **502 Bad Gateway:** `journalctl -u gunicorn-codecraften -n 50` — check `.env`, DB credentials, `WorkingDirectory`.
- **Static CSS missing:** run `collectstatic` again; Whitenoise serves static through Gunicorn.
- **Uploads 403:** `chown www-data:www-data media` and Nginx `location /media/` path must match `MEDIA_ROOT`.

---

## Files in `deploy/`

| File | Purpose |
|------|---------|
| `env.production.example` | Copy to `.env` on server |
| `gunicorn.service.example` | systemd unit |
| `nginx-codecraften.conf.example` | Nginx site |
