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
echo "Read order: INDEX.md -> CONVENTIONS.md -> 00-product/automation-charter.md"
echo "Work queue is beads, not roadmap.md. roadmap.md carries phases and exit gates only."
echo "Session close procedure: CONVENTIONS.md"
