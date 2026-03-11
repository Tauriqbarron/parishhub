#!/usr/bin/env bash
set -euo pipefail

# --- Configuration ---
DEPLOY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"
HEALTH_URL="http://localhost:8000/api/health"
MAX_HEALTH_RETRIES=30
HEALTH_INTERVAL=5
LOG_DIR="/var/log/parish-deploy"
BACKUP_DIR="/var/backups/parish-db"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="${LOG_DIR}/deploy-${TIMESTAMP}.log"
FORCE_DEPLOY=false

# Parse flags
for arg in "$@"; do
    case "$arg" in
        --force) FORCE_DEPLOY=true ;;
    esac
done

# --- Helpers ---
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

cleanup_old_logs() {
    find "$LOG_DIR" -name "deploy-*.log" -mtime +30 -delete 2>/dev/null || true
}

cleanup_old_backups() {
    find "$BACKUP_DIR" -name "pre-deploy-*.sql.gz" -mtime +30 -delete 2>/dev/null || true
}

rollback() {
    local previous_commit="$1"
    log "ROLLING BACK to ${previous_commit}..."
    git -C "$DEPLOY_DIR" checkout "$previous_commit"
    docker compose -f "$DEPLOY_DIR/$COMPOSE_FILE" build backend frontend
    docker compose -f "$DEPLOY_DIR/$COMPOSE_FILE" up -d --no-deps backend frontend nginx
    log "Rollback complete. Services restarted at ${previous_commit}."
}

# --- Main ---
log "=== Deploy started ==="
cd "$DEPLOY_DIR"

# Source environment variables for pg_dump
if [ -f "$DEPLOY_DIR/.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "$DEPLOY_DIR/.env"
    set +a
fi

# Record current commit for rollback
PREVIOUS_COMMIT="$(git rev-parse HEAD)"
log "Previous commit: ${PREVIOUS_COMMIT}"

# Pull latest code (skip in CI/force mode since checkout already has latest)
if [ "$FORCE_DEPLOY" = true ]; then
    log "Force deploy mode — skipping git pull."
    CURRENT_COMMIT="$(git rev-parse HEAD)"
else
    log "Pulling latest code..."
    git pull origin main
    CURRENT_COMMIT="$(git rev-parse HEAD)"
fi
log "Deploying commit: ${CURRENT_COMMIT}"

if [ "$FORCE_DEPLOY" = false ] && [ "$PREVIOUS_COMMIT" = "$CURRENT_COMMIT" ]; then
    log "No new commits."
    # Still verify the service is running
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        log "Service is healthy. Nothing to do."
        exit 0
    fi
    log "Service is not healthy. Rebuilding and restarting containers..."
    docker compose -f "$COMPOSE_FILE" build backend
    docker compose -f "$COMPOSE_FILE" up -d
    log "Waiting for health check..."
    for i in $(seq 1 "$MAX_HEALTH_RETRIES"); do
        if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
            log "Health check passed (attempt ${i}/${MAX_HEALTH_RETRIES})"
            log "=== Service restored ==="
            exit 0
        fi
        if [ "$i" -eq "$MAX_HEALTH_RETRIES" ]; then
            log "ERROR: Health check failed after ${MAX_HEALTH_RETRIES} attempts"
            exit 1
        fi
        sleep "$HEALTH_INTERVAL"
    done
fi

# Pre-deploy database backup
log "Backing up database..."
docker compose -f "$COMPOSE_FILE" exec -T db \
    pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > \
    "${BACKUP_DIR}/pre-deploy-${CURRENT_COMMIT:0:8}-${TIMESTAMP}.sql.gz"
log "Backup saved to ${BACKUP_DIR}/pre-deploy-${CURRENT_COMMIT:0:8}-${TIMESTAMP}.sql.gz"

# Build new images
log "Building images..."
docker compose -f "$COMPOSE_FILE" build backend frontend

# Run database migrations using new image
log "Running database migrations..."
if ! docker compose -f "$COMPOSE_FILE" run --rm backend alembic upgrade head; then
    log "ERROR: Migration failed. Rolling back..."
    rollback "$PREVIOUS_COMMIT"
    exit 1
fi

# Bring up services with new images
log "Restarting services..."
docker compose -f "$COMPOSE_FILE" up -d --no-deps backend frontend nginx

# Health check loop
log "Waiting for health check..."
for i in $(seq 1 "$MAX_HEALTH_RETRIES"); do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        log "Health check passed (attempt ${i}/${MAX_HEALTH_RETRIES})"
        break
    fi
    if [ "$i" -eq "$MAX_HEALTH_RETRIES" ]; then
        log "ERROR: Health check failed after ${MAX_HEALTH_RETRIES} attempts"
        rollback "$PREVIOUS_COMMIT"
        exit 1
    fi
    sleep "$HEALTH_INTERVAL"
done

# Cleanup
docker image prune -f > /dev/null 2>&1
cleanup_old_logs
cleanup_old_backups

log "=== Deploy complete: ${CURRENT_COMMIT} ==="
