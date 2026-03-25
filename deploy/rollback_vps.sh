#!/usr/bin/env bash
set -Eeuo pipefail

# Rollback helper for VPS deploy backups created by deploy scripts.
#
# Usage:
#   chmod +x deploy/rollback_vps.sh
#   ./deploy/rollback_vps.sh --backup /root/backup_YYYY-MM-DD_HH-MM-SS
#
# Optional:
#   --restore-project   Also restore project folder backup if available
#   --yes               Non-interactive mode

BACKUP_DIR=""
RESTORE_PROJECT="false"
NON_INTERACTIVE="false"

usage() {
  cat <<'EOF'
Usage:
  rollback_vps.sh --backup <backup_dir> [options]

Required:
  --backup <dir>      Backup folder path (e.g. /root/backup_2026-03-25_22-10-00)

Optional:
  --restore-project   Restore old project folder if backup exists
  --yes               Skip confirmation prompt
  --help              Show this help
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
      --backup) BACKUP_DIR="$2"; shift 2 ;;
      --restore-project) RESTORE_PROJECT="true"; shift 1 ;;
      --yes) NON_INTERACTIVE="true"; shift 1 ;;
      --help|-h) usage; exit 0 ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  [[ -n "$BACKUP_DIR" ]] || die "--backup is required."
  [[ -d "$BACKUP_DIR" ]] || die "Backup directory does not exist: $BACKUP_DIR"
}

require_root() {
  [[ "$EUID" -eq 0 ]] || die "Run as root."
}

create_pre_rollback_backup() {
  PRE_ROLLBACK="/root/pre_rollback_$(date +%F_%H-%M-%S)"
  log "Creating safety snapshot before rollback: $PRE_ROLLBACK"
  mkdir -p "$PRE_ROLLBACK"
  cp -a /etc/nginx "$PRE_ROLLBACK/nginx_current_backup"
  [[ -d /var/www ]] && cp -a /var/www "$PRE_ROLLBACK/var_www_current_backup" || true
  [[ -d /root/myproject ]] && cp -a /root/myproject "$PRE_ROLLBACK/root_myproject_current_backup" || true
  [[ -d /var/www/myproject ]] && cp -a /var/www/myproject "$PRE_ROLLBACK/var_www_myproject_current_backup" || true
}

restore_nginx() {
  local src_nginx="$BACKUP_DIR/nginx_full_backup"
  [[ -d "$src_nginx" ]] || die "nginx backup not found at $src_nginx"

  log "Restoring /etc/nginx from backup"
  rm -rf /etc/nginx
  cp -a "$src_nginx" /etc/nginx
}

restore_web_roots() {
  if [[ -d "$BACKUP_DIR/var_www_backup" ]]; then
    log "Restoring /var/www from backup"
    rm -rf /var/www
    cp -a "$BACKUP_DIR/var_www_backup" /var/www
  else
    warn "No /var/www backup found, skipping."
  fi

  if [[ -d "$BACKUP_DIR/nginx_html_backup" ]]; then
    log "Restoring /usr/share/nginx/html from backup"
    rm -rf /usr/share/nginx/html
    cp -a "$BACKUP_DIR/nginx_html_backup" /usr/share/nginx/html
  else
    warn "No nginx html backup found, skipping."
  fi
}

restore_project_if_requested() {
  [[ "$RESTORE_PROJECT" == "true" ]] || return 0

  if [[ -d "$BACKUP_DIR/old_project_backup" ]]; then
    log "Restoring old project to /root/myproject"
    rm -rf /root/myproject
    cp -a "$BACKUP_DIR/old_project_backup" /root/myproject
  elif [[ -d "$BACKUP_DIR/root_myproject_backup" ]]; then
    log "Restoring old project to /root/myproject"
    rm -rf /root/myproject
    cp -a "$BACKUP_DIR/root_myproject_backup" /root/myproject
  else
    warn "No project backup found in this backup set."
  fi
}

restart_services() {
  log "Validating and restarting nginx"
  nginx -t
  systemctl restart nginx

  if systemctl list-unit-files | grep -q '^gunicorn\.service'; then
    log "Restarting gunicorn.service"
    systemctl restart gunicorn || warn "gunicorn restart failed."
  fi

  if systemctl list-unit-files | grep -q '^myproject-gunicorn\.service'; then
    log "Restarting myproject-gunicorn.service"
    systemctl restart myproject-gunicorn || warn "myproject-gunicorn restart failed."
  fi
}

verify() {
  log "Service status"
  systemctl --no-pager --full status nginx | sed -n '1,20p'
  systemctl status gunicorn --no-pager 2>/dev/null | sed -n '1,20p' || true
  systemctl status myproject-gunicorn --no-pager 2>/dev/null | sed -n '1,20p' || true
}

main() {
  parse_args "$@"
  require_root

  warn "Rollback source: $BACKUP_DIR"
  confirm_or_exit "Proceed with rollback?"

  create_pre_rollback_backup
  restore_nginx
  restore_web_roots
  restore_project_if_requested
  restart_services
  verify

  cat <<EOF

Rollback finished.
Restored from: $BACKUP_DIR
Pre-rollback safety snapshot: $PRE_ROLLBACK

Tips:
  - If DNS changed, verify domain still points to expected server.
  - If app errors persist, inspect:
      journalctl -u nginx -n 100 --no-pager
      tail -n 100 /var/log/nginx/error.log
EOF
}

main "$@"
