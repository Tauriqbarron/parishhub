#!/bin/bash
# Parish Hub — One-shot backup setup for ProDesk server
# Run: gh api repos/Tauriqbarron/parishhub/contents/scripts/setup-parish-backups.sh --jq .content | base64 -d | bash
set -euo pipefail

echo "=== Parish Hub Backup Setup ==="
BACKUP_ROOT="$HOME/backups/parish-hub"
SCRIPTS_DIR="$HOME/scripts"
mkdir -p "$BACKUP_ROOT"/{daily,weekly,monthly} "$SCRIPTS_DIR"

# Daily backup
cat > "$SCRIPTS_DIR/backup-parish-hub.sh" << 'S1'
#!/bin/bash
set -euo pipefail
DIR="$HOME/backups/parish-hub/daily"
TS=$(date +%F)
LOG="$HOME/backups/parish-hub/parish-hub-backup.log"
mkdir -p "$DIR"
docker exec parishhub-db-1 pg_dump -U postgres parish_db | gzip > "$DIR/parish_db_${TS}.sql.gz.tmp" && mv "$DIR/parish_db_${TS}.sql.gz.tmp" "$DIR/parish_db_${TS}.sql.gz"
SIZE=$(stat -c%s "$DIR/parish_db_${TS}.sql.gz" 2>/dev/null || echo 0)
[ "$SIZE" -lt 100 ] && echo "$(date) ERROR: too small ($SIZE bytes)" >> "$LOG" && exit 1
echo "$(date) OK: Daily ($SIZE bytes)" >> "$LOG"
find "$DIR" -name "*.sql.gz" -mtime +30 -delete
S1

# Weekly backup
cat > "$SCRIPTS_DIR/backup-parish-hub-weekly.sh" << 'S2'
#!/bin/bash
set -euo pipefail
DAILY="$HOME/backups/parish-hub/daily"
WEEKLY="$HOME/backups/parish-hub/weekly"
LOG="$HOME/backups/parish-hub/parish-hub-backup.log"
mkdir -p "$WEEKLY"
LATEST=$(ls -t "$DAILY"/parish_db_*.sql.gz 2>/dev/null | head -1)
[ -z "$LATEST" ] && echo "$(date) ERROR: No daily backup" >> "$LOG" && exit 1
cp "$LATEST" "$WEEKLY/"
if command -v rclone &>/dev/null && rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
  rclone copy "$LATEST" "gdrive:parish-hub-backups/weekly"
  echo "$(date) OK: Weekly offsite" >> "$LOG"
else
  echo "$(date) WARN: rclone not ready" >> "$LOG"
fi
find "$WEEKLY" -name "*.sql.gz" -mtime +56 -delete
S2

# Monthly backup
cat > "$SCRIPTS_DIR/backup-parish-hub-monthly.sh" << 'S3'
#!/bin/bash
set -euo pipefail
DAILY="$HOME/backups/parish-hub/daily"
MONTHLY="$HOME/backups/parish-hub/monthly"
LOG="$HOME/backups/parish-hub/parish-hub-backup.log"
mkdir -p "$MONTHLY"
LATEST=$(ls -t "$DAILY"/parish_db_*.sql.gz 2>/dev/null | head -1)
[ -z "$LATEST" ] && echo "$(date) ERROR: No daily backup" >> "$LOG" && exit 1
cp "$LATEST" "$MONTHLY/"
if command -v rclone &>/dev/null && rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
  rclone copy "$LATEST" "gdrive:parish-hub-backups/monthly"
  echo "$(date) OK: Monthly offsite" >> "$LOG"
else
  echo "$(date) WARN: rclone not ready" >> "$LOG"
fi
find "$MONTHLY" -name "*.sql.gz" -mtime +365 -delete
S3

chmod +x "$SCRIPTS_DIR"/backup-parish-hub*.sh
echo "Scripts created."

# Cron
(crontab -l 2>/dev/null | grep -v 'backup-parish-hub'; cat <<CRON
# Parish Hub Backups
0 2 * * * $SCRIPTS_DIR/backup-parish-hub.sh
0 3 * * 0 $SCRIPTS_DIR/backup-parish-hub-weekly.sh
0 4 1 * * $SCRIPTS_DIR/backup-parish-hub-monthly.sh
CRON
) | crontab -
echo "Cron installed:"
crontab -l | grep parish

# Test
echo "Running test backup..."
bash "$SCRIPTS_DIR/backup-parish-hub.sh"
echo ""
ls -lh "$BACKUP_ROOT/daily/"
echo ""
echo "=== Setup complete ==="
echo ""
echo "Next: Set up rclone + Google Drive for offsite backups:"
echo "  curl -fsSL https://rclone.org/install.sh | sudo bash"
echo "  rclone config  (choose 'drive', name it 'gdrive')"
