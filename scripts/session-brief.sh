#!/usr/bin/env bash
# Prints ready work and recent decision history for a new Claude Code session.
# Wired as a SessionStart hook; stdout is injected into the model's context.
# Resolves the docs repo from its own location, so moving the project only
# requires updating the path in .claude/settings.json.
set -uo pipefail

DOCS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DOCS" || exit 0

echo "== Ready work (bd ready) =="
if command -v bd >/dev/null 2>&1; then
  bd ready 2>/dev/null || echo "bd failed; run 'bd ready' manually"
else
  echo "bd not on PATH - install it (brew install beads), see ADR-0008"
fi

echo
echo "== Recent decisions =="
git log --oneline -3 2>/dev/null

echo
latest_audit="$(ls -1 audit-*.md 2>/dev/null | sort | tail -1)"
if [ -z "$latest_audit" ]; then
  echo "== Drift audit: never run =="
else
  audit_date="${latest_audit#audit-}"
  audit_date="${audit_date%.md}"
  if audit_epoch="$(date -j -f "%Y-%m-%d %H:%M:%S" "$audit_date 00:00:00" +%s 2>/dev/null)"; then
    :
  else
    audit_epoch="$(date -d "$audit_date" +%s 2>/dev/null)"
  fi
  if [ -n "${audit_epoch:-}" ]; then
    age=$(( ( $(date +%s) - audit_epoch ) / 86400 ))
    if [ "$age" -gt 30 ]; then
      echo "== Drift audit: last run $audit_date ($age days ago) - overdue. Run the drift-audit skill =="
    fi
  fi
fi

echo
echo "Read order: INDEX.md -> CONVENTIONS.md -> 00-product/automation-charter.md"
echo "Work queue is beads, not roadmap.md. roadmap.md carries phases and exit gates only."
echo "Session close procedure: CONVENTIONS.md"
