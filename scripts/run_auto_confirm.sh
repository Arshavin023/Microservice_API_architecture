#!/bin/bash
# Cron wrapper for auto_confirm_delivery.py
# Runs every 15 minutes — add to crontab:
# */15 * * * * /home/uche-nnodim/pizzasale_api/scripts/run_auto_confirm.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${SCRIPT_DIR}/venv/bin/python3"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/auto_confirm.log"
MAX_LOG_LINES=2000

mkdir -p "$LOG_DIR"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "── ${TIMESTAMP} ─────────────────────" >> "$LOG_FILE"

if "$VENV_PYTHON" "${SCRIPT_DIR}/auto_confirm_delivery.py" --fix >> "$LOG_FILE" 2>&1; then
    EXIT_CODE=0
else
    EXIT_CODE=$?
fi

echo "Exit code: ${EXIT_CODE}" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Rotate
if [ -f "$LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$LOG_FILE")
    if [ "$LINE_COUNT" -gt "$MAX_LOG_LINES" ]; then
        tail -n "$MAX_LOG_LINES" "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
fi

exit "$EXIT_CODE"
