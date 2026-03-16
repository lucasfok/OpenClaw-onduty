#!/usr/bin/env bash
set -euo pipefail

: "${SKILLS_SRC:=/opt/onduty/skills}"
: "${CODEX_HOME:=/home/openclaw/.codex}"
SKILLS_DST="$CODEX_HOME/skills"

mkdir -p "$SKILLS_DST"

if [[ -d "$SKILLS_SRC" ]]; then
  cp -rn "$SKILLS_SRC"/* "$SKILLS_DST"/ 2>/dev/null || true
fi

exec "$@"
