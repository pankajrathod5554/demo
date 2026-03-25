#!/usr/bin/env bash
set -Eeuo pipefail

# Hardened one-shot deployment for Django on Ubuntu VPS.
# - Uses non-root deploy user
# - Deploys to /var/www/myproject
# - Configures gunicorn + nginx + certbot
#
# Usage (run as root):
#   chmod +x deploy/deploy_vps_nonroot.sh
#   ./deploy/deploy_vps_nonroot.sh \
#     --domain codecraften.com \
#     --repo https://github.com/USER/REPO.git \
#     --email admin@codecraften.com

DOMAIN=""
REPO_URL=""
BRANCH="main"
EMAIL=""
USE_WWW="true"
NON_INTERACTIVE="false"

APP_NAME="myproject"
APP_USER="myproject"
APP_GROUP="www-data"
PROJECT_DIR="/var/www/myproject"
SOCK_FILE="/run/myproject-gunicorn.sock"
SERVICE_NAME="myproject-gunicorn"

usage() {
  cat <<'EOF'
Usage:
  deploy_vps_nonroot.sh --domain <domain> --repo <git_url> [options]

Required:
  --domain        Primary domain, e.g. codecraften.com
  --repo          Git repository URL

Optional:
  --branch        Git branch (default: main)
  --email         Email for certbot
  --no-www        Disable www domain
  --yes           Non-interactive mode
  --help          Show this help
EOF
}

log() { printf "\n[+] %s\n" "$1"; }
warn() { printf "\n[!] %s\n" "$1"; }
die() { printf "\n[ERROR] %s\n" "$1" >&2; exit 1; }

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
      --branch) BRANCH="$2"; shift 2 ;;
      --email) EMAIL="$2"; shift 2 ;;
      --no-www) USE_WWW="false"; shift 1 ;;
      --yes) NON_INTERACTIVE="true"; shift 1 ;;
      --help|-h) usage; exit 0 ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  [[ -n "$DOMAIN" ]] || die "--domain is required"
  [[ -n "$REPO_URL" ]] || die "--repo is required"
}

build_domain_vars() {
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

require_root() {
  [[ "$EUID" -eq 0 ]] || die "Run as root."
}

install_packages() {
  log "Installing system packages"
  apt update
  DEBIAN_FRONTEND=noninteractive apt install -y \
    git python3 python3-venv python3-pip nginx certbot python3-certbot-nginx
}

backup_existing() {
  BACKUP_DIR="/root/backup_$(date +%F_%H-%M-%S)"
  log "Creating backup at $BACKUP_DIR"
  mkdir -p "$BACKUP_DIR"
  cp -a /etc/nginx "$BACKUP_DIR/nginx_full_backup"
  [[ -d /var/www ]] && cp -a /var/www "$BACKUP_DIR/var_www_backup" || true
  [[ -d "/root/myproject" ]] && cp -a /root/myproject "$BACKUP_DIR/root_myproject_backup" || true
}

prepare_user_dirs() {
  log "Preparing user and project directories"
  id -u "$APP_USER" >/dev/null 2>&1 || useradd --system --create-home --shell /bin/bash "$APP_USER"

  mkdir -p /var/www
  rm -rf "$PROJECT_DIR"
  mkdir -p "$PROJECT_DIR"
  chown -R "$APP_USER:$APP_USER" "$PROJECT_DIR"
}

deploy_code() {
  log "Cloning project code"
  sudo -u "$APP_USER" git clone --branch "$BRANCH" "$REPO_URL" "$PROJECT_DIR"
}

setup_venv_and_requirements() {
  log "Creating venv and installing Python dependencies"
  sudo -u "$APP_USER" bash -lc "
    cd '$PROJECT_DIR'
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip wheel setuptools
    pip install -r requirements.txt
    pip install gunicorn whitenoise python-decouple
  "
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
  chown "$APP_USER:$APP_USER" "$PROJECT_DIR/.env"
  chmod 640 "$PROJECT_DIR/.env"
}

run_django_commands() {
  log "Running migrate and collectstatic"
  sudo -u "$APP_USER" bash -lc "
    cd '$PROJECT_DIR'
    source .venv/bin/activate
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
  "
}

write_gunicorn_service() {
  log "Creating systemd gunicorn service"
  cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Gunicorn daemon for $APP_NAME
After=network.target

[Service]
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin"
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn \\
    --workers 3 \\
    --bind unix:$SOCK_FILE \\
    myproject.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
}

configure_gunicorn() {
  log "Starting gunicorn service"
  systemctl daemon-reload
  systemctl enable "$SERVICE_NAME"
  systemctl restart "$SERVICE_NAME"
}

write_nginx_config() {
  log "Writing nginx site config"
  rm -f /etc/nginx/sites-enabled/*

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
        proxy_pass http://unix:$SOCK_FILE;
    }
}
EOF

  ln -sf /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled/myproject
  nginx -t
  systemctl restart nginx
}

setup_ssl() {
  log "Configuring HTTPS with certbot"
  if [[ -n "$EMAIL" ]]; then
    certbot --nginx --agree-tos -m "$EMAIL" --redirect "${CERTBOT_DOMAINS[@]}"
  else
    certbot --nginx --register-unsafely-without-email --redirect "${CERTBOT_DOMAINS[@]}"
  fi
  certbot renew --dry-run || warn "Certbot renew dry-run failed"
}

set_permissions() {
  log "Setting static/media permissions"
  mkdir -p "$PROJECT_DIR/media" "$PROJECT_DIR/staticfiles"
  chown -R "$APP_USER:$APP_GROUP" "$PROJECT_DIR/media" "$PROJECT_DIR/staticfiles"
  chmod -R 775 "$PROJECT_DIR/media" "$PROJECT_DIR/staticfiles"
}

verify() {
  log "Verifying services"
  systemctl restart "$SERVICE_NAME"
  systemctl restart nginx
  systemctl --no-pager --full status "$SERVICE_NAME" | sed -n '1,20p'
  systemctl --no-pager --full status nginx | sed -n '1,20p'
}

print_done() {
  cat <<EOF

Deployment finished.

Project:         $PROJECT_DIR
App user:        $APP_USER
Gunicorn:        $SERVICE_NAME
Socket:          $SOCK_FILE
Nginx site:      /etc/nginx/sites-available/myproject
Env file:        $PROJECT_DIR/.env
Backup folder:   $BACKUP_DIR

Useful commands:
  journalctl -u $SERVICE_NAME -n 100 --no-pager
  tail -n 100 /var/log/nginx/error.log
  sudo -u $APP_USER bash -lc "cd $PROJECT_DIR && source .venv/bin/activate && python manage.py collectstatic --noinput"
EOF
}

main() {
  parse_args "$@"
  require_root
  build_domain_vars

  warn "This will replace the currently served website on $DOMAIN."
  confirm_or_exit "Continue with hardened non-root deployment?"

  install_packages
  backup_existing
  prepare_user_dirs
  deploy_code
  setup_venv_and_requirements
  write_env_file
  run_django_commands
  write_gunicorn_service
  configure_gunicorn
  write_nginx_config
  set_permissions
  setup_ssl
  verify
  print_done
}

main "$@"
