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
# Only the dated form can be aged. `ls | sort | tail -1` took the lexicographic
# maximum over every audit-*.md, so an `audit-draft.md` outranked a real dated
# report, both `date` branches failed, and the block printed nothing at all -
# a years-overdue audit made invisible inside the one mechanism whose purpose
# is to fire. Anything unparseable is now named on stdout instead of dropped.
# The glob expands in lexicographic order and ISO dates sort chronologically,
# so the last match is the newest.
latest_audit=""
unparseable=""
for f in audit-*.md; do
  [ -e "$f" ] || continue
  case "$f" in
    audit-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md) latest_audit="$f" ;;
    *) unparseable="$unparseable $f" ;;
  esac
done
if [ -n "$unparseable" ]; then
  echo "== Drift audit: unparseable report filename(s):$unparseable - expected audit-YYYY-MM-DD.md; not aged =="
fi
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
  if [ -z "${audit_epoch:-}" ]; then
    echo "== Drift audit: cannot compute the age of $latest_audit - neither date branch parsed '$audit_date' =="
  else
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
