#!/usr/bin/env bash
set -Eeuo pipefail

# One-shot production deploy for Django on Ubuntu VPS.
# - Backs up old nginx config + web roots
# - Replaces old website with new Django project
# - Configures gunicorn + nginx + certbot
# - Runs migrate + collectstatic
#
# Usage (as root):
#   chmod +x deploy/deploy_vps.sh
#   ./deploy/deploy_vps.sh \
#     --domain codecraften.com \
#     --repo https://github.com/USER/REPO.git
#
# Optional:
#   --project-dir /root/myproject
#   --branch main
#   --email admin@codecraften.com
#   --no-www

DOMAIN=""
REPO_URL=""
PROJECT_DIR="/root/myproject"
BRANCH="main"
EMAIL=""
USE_WWW="true"
NON_INTERACTIVE="false"

print_usage() {
  cat <<'EOF'
Usage:
  deploy_vps.sh --domain <domain> --repo <git_url> [options]

Required:
  --domain        Primary domain (example: codecraften.com)
  --repo          GitHub repository URL

Optional:
  --project-dir   Project path (default: /root/myproject)
  --branch        Git branch to deploy (default: main)
  --email         Email for certbot registration
  --no-www        Do not configure www subdomain
  --yes           Non-interactive mode (dangerous if misconfigured)
  --help          Show this help
EOF
}

log() {
  printf "\n[+] %s\n" "$1"
}

warn() {
  printf "\n[!] %s\n" "$1"
}

die() {
  printf "\n[ERROR] %s\n" "$1" >&2
  exit 1
}

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    die "Run this script as root."
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing command: $1"
}

confirm_or_exit() {
  local prompt="$1"
  if [[ "$NON_INTERACTIVE" == "true" ]]; then
    return 0
  fi
  read -r -p "$prompt [y/N]: " ans
  [[ "${ans,,}" == "y" || "${ans,,}" == "yes" ]] || die "Cancelled."
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --domain) DOMAIN="$2"; shift 2 ;;
      --repo) REPO_URL="$2"; shift 2 ;;
      --project-dir) PROJECT_DIR="$2"; shift 2 ;;
      --branch) BRANCH="$2"; shift 2 ;;
      --email) EMAIL="$2"; shift 2 ;;
      --no-www) USE_WWW="false"; shift 1 ;;
      --yes) NON_INTERACTIVE="true"; shift 1 ;;
      --help|-h) print_usage; exit 0 ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  [[ -n "$DOMAIN" ]] || die "--domain is required."
  [[ -n "$REPO_URL" ]] || die "--repo is required."
}

build_hosts() {
  if [[ "$USE_WWW" == "true" ]]; then
    SERVER_NAMES="$DOMAIN www.$DOMAIN"
    ALLOWED_HOSTS="$DOMAIN,www.$DOMAIN"
    CSRF_ORIGINS="https://$DOMAIN,https://www.$DOMAIN"
    CERTBOT_DOMAINS=(-d "$DOMAIN" -d "www.$DOMAIN")
  else
    SERVER_NAMES="$DOMAIN"
    ALLOWED_HOSTS="$DOMAIN"
    CSRF_ORIGINS="https://$DOMAIN"
    CERTBOT_DOMAINS=(-d "$DOMAIN")
  fi
}

check_dns_hint() {
  warn "Make sure DNS A records point to this VPS before certbot."
}

install_packages() {
  log "Installing system packages"
  apt update
  DEBIAN_FRONTEND=noninteractive apt install -y \
    git python3 python3-venv python3-pip nginx certbot python3-certbot-nginx
}

backup_existing() {
  BACKUP_DIR="/root/backup_$(date +%F_%H-%M-%S)"
  log "Creating backups in $BACKUP_DIR"
  mkdir -p "$BACKUP_DIR"

  cp -a /etc/nginx "$BACKUP_DIR/nginx_full_backup"
  [[ -d /var/www ]] && cp -a /var/www "$BACKUP_DIR/var_www_backup" || true
  [[ -d /usr/share/nginx/html ]] && cp -a /usr/share/nginx/html "$BACKUP_DIR/nginx_html_backup" || true
  [[ -d "$PROJECT_DIR" ]] && cp -a "$PROJECT_DIR" "$BACKUP_DIR/old_project_backup" || true

  log "Backup completed: $BACKUP_DIR"
}

disable_old_nginx_sites() {
  log "Removing old enabled nginx site configs"
  mkdir -p "$BACKUP_DIR/old_sites_available"
  cp -a /etc/nginx/sites-available/* "$BACKUP_DIR/old_sites_available/" 2>/dev/null || true
  rm -f /etc/nginx/sites-enabled/*
}

deploy_code() {
  log "Deploying project from GitHub"
  rm -rf "$PROJECT_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$PROJECT_DIR"
}

setup_python() {
  log "Setting up virtual environment and dependencies"
  cd "$PROJECT_DIR"
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip wheel setuptools
  pip install -r requirements.txt
  pip install gunicorn whitenoise python-decouple
}

write_env_file() {
  log "Writing production .env"
  cat > "$PROJECT_DIR/.env" <<EOF
SECRET_KEY=change-this-to-a-long-random-secret
DEBUG=False
ALLOWED_HOSTS=$ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS=$CSRF_ORIGINS

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=$PROJECT_DIR/db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
EOF
  chmod 600 "$PROJECT_DIR/.env"
}

run_django_tasks() {
  log "Running migrate and collectstatic"
  cd "$PROJECT_DIR"
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
}

write_gunicorn_service() {
  log "Creating /etc/systemd/system/gunicorn.service"
  cat > /etc/systemd/system/gunicorn.service <<EOF
[Unit]
Description=Gunicorn daemon for myproject
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin"
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn \\
    --workers 3 \\
    --bind unix:/run/gunicorn.sock \\
    myproject.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
}

enable_gunicorn() {
  log "Enabling and starting gunicorn"
  systemctl daemon-reload
  systemctl enable gunicorn
  systemctl restart gunicorn
}

write_nginx_config() {
  log "Creating nginx config for $DOMAIN"
  cat > /etc/nginx/sites-available/myproject <<EOF
server {
    listen 80;
    server_name $SERVER_NAMES;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
    }

    location / {
        include proxy_params;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
EOF

  ln -sf /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled/myproject
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl restart nginx
}

setup_ssl() {
  log "Requesting SSL certificate via certbot"
  if [[ -n "$EMAIL" ]]; then
    certbot --nginx --agree-tos -m "$EMAIL" --redirect "${CERTBOT_DOMAINS[@]}"
  else
    certbot --nginx --register-unsafely-without-email --redirect "${CERTBOT_DOMAINS[@]}"
  fi
  certbot renew --dry-run || warn "Certbot dry-run failed. Check certbot logs."
}

fix_common_permissions() {
  log "Applying common static/media permission fixes"
  mkdir -p "$PROJECT_DIR/media" "$PROJECT_DIR/staticfiles"
  chown -R www-data:www-data "$PROJECT_DIR/media" "$PROJECT_DIR/staticfiles" || true
  chmod -R 755 "$PROJECT_DIR/media" "$PROJECT_DIR/staticfiles" || true
}

verify_services() {
  log "Service health checks"
  systemctl restart gunicorn
  systemctl restart nginx
  systemctl --no-pager --full status gunicorn | sed -n '1,20p'
  systemctl --no-pager --full status nginx | sed -n '1,20p'
  ss -tulpn | grep -E ':80|:443' || true
}

print_post_deploy_notes() {
  cat <<EOF

Deployment complete.

Key paths:
  Project:      $PROJECT_DIR
  Env file:     $PROJECT_DIR/.env
  Gunicorn svc: /etc/systemd/system/gunicorn.service
  Nginx site:   /etc/nginx/sites-available/myproject
  Backup:       $BACKUP_DIR

Useful commands:
  journalctl -u gunicorn -n 100 --no-pager
  tail -n 100 /var/log/nginx/error.log
  nginx -t
  systemctl restart gunicorn nginx

If static files fail:
  cd $PROJECT_DIR && source .venv/bin/activate && python manage.py collectstatic --noinput

If 502 error:
  systemctl status gunicorn --no-pager
  journalctl -u gunicorn -n 200 --no-pager
EOF
}

main() {
  parse_args "$@"
  require_root
  require_cmd systemctl
  require_cmd apt

  build_hosts
  check_dns_hint

  cat <<EOF
This will REPLACE old website on:
  Domain:      $DOMAIN
  Project dir: $PROJECT_DIR
  Repo:        $REPO_URL
  Branch:      $BRANCH
EOF

  confirm_or_exit "Proceed with full deployment?"

  install_packages
  backup_existing
  disable_old_nginx_sites
  deploy_code
  setup_python
  write_env_file
  run_django_tasks
  write_gunicorn_service
  enable_gunicorn
  write_nginx_config
  setup_ssl
  fix_common_permissions
  verify_services
  print_post_deploy_notes
}

main "$@"
