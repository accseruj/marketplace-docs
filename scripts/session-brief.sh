#!/usr/bin/env bash
# Prints the next action and recent decision history for a new Claude Code session.
# Wired as a SessionStart hook; stdout is injected into the model's context.
# Resolves the docs repo from its own location, so moving the project only
# requires updating the path in .claude/settings.json.
set -uo pipefail

DOCS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROADMAP="$DOCS/00-product/roadmap.md"

[ -f "$ROADMAP" ] || exit 0

echo "== Next action =="
awk '
  /^## .*\(current\)/ { inphase = 1; print "Phase: " substr($0, 4); next }
  inphase && /^## /   { exit }
  inphase && /^1\. /  { print; exit }
' "$ROADMAP"
echo "Full queue: 00-product/roadmap.md"

echo
echo "== Recent decisions =="
git -C "$DOCS" log --oneline -3 2>/dev/null

echo
echo "Read order: INDEX.md -> CONVENTIONS.md -> 00-product/automation-charter.md -> 00-product/roadmap.md"
echo "Session close procedure: CONVENTIONS.md"
