#!/usr/bin/env bash
set -euo pipefail

: "${DAILY_CHECK_UTC_HOUR:=07}"
: "${DAILY_CHECK_UTC_MINUTE:=00}"
: "${RUNBOOK_PATH:=/etc/onduty/runbook.json}"
: "${REPORTS_DIR:=/workspace/reports}"
: "${ROTATION_TEAM_PATH:=/etc/onduty/rotation-team.json}"
: "${ROTATION_STATE_PATH:=/workspace/rotation/state.json}"

mkdir -p "$REPORTS_DIR"

pick_responsible() {
  ROTATION_TEAM_PATH="$ROTATION_TEAM_PATH" ROTATION_STATE_PATH="$ROTATION_STATE_PATH" \
    python3 /opt/onduty/select_responsible.py
}

run_checks() {
  local timestamp
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  local report_file="$REPORTS_DIR/report-${timestamp}.json"

  local assignment_json
  assignment_json="$(pick_responsible)"
  local responsible
  responsible="$(ASSIGNMENT_JSON="$assignment_json" python3 - <<'PY'
import json, os
print(json.loads(os.environ["ASSIGNMENT_JSON"])["person"])
PY
)"

  echo "[onduty-agent] responsible this week: $responsible"
  echo "[onduty-agent] starting runbook checks at $(date -u --iso-8601=seconds)"

  if REPORT_PATH="$report_file" RUNBOOK_PATH="$RUNBOOK_PATH" RESPONSIBLE_PERSON="$responsible" python3 /opt/onduty/runbook_runner.py; then
    ln -sf "$report_file" "$REPORTS_DIR/latest-report.json"
    echo "[onduty-agent] checks passed -> $report_file"
  else
    ln -sf "$report_file" "$REPORTS_DIR/latest-report.json"
    echo "[onduty-agent] checks failed -> $report_file"
  fi
}

seconds_until_target() {
  python3 - <<'PY'
from datetime import datetime, timedelta, timezone
import os

hour = int(os.environ.get("DAILY_CHECK_UTC_HOUR", "7"))
minute = int(os.environ.get("DAILY_CHECK_UTC_MINUTE", "0"))
now = datetime.now(timezone.utc)
target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
if target <= now:
    target = target + timedelta(days=1)
print(int((target - now).total_seconds()))
PY
}

if [[ "${RUN_IMMEDIATELY:-false}" == "true" ]]; then
  run_checks
fi

while true; do
  sleep_for="$(seconds_until_target)"
  echo "[onduty-agent] sleeping ${sleep_for}s until next schedule ${DAILY_CHECK_UTC_HOUR}:${DAILY_CHECK_UTC_MINUTE} UTC"
  sleep "$sleep_for"
  run_checks
  sleep 1
done
