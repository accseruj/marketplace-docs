#!/usr/bin/env bash
# Verifies the drift-audit staleness line. Run from the docs repo root.
set -uo pipefail
DOCS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cp -R "$DOCS" "$TMP/docs"
cd "$TMP/docs" || exit 1
rm -f audit-*.md

fail=0

# case 1: no audit file at all
out="$(bash scripts/session-brief.sh 2>/dev/null)"
if ! grep -q "Drift audit: never run" <<<"$out"; then
  echo "FAIL case 1: expected 'never run', got:"; echo "$out"; fail=1
fi

# case 2: an audit 45 days old is overdue
old="$(python3 -c "import datetime;print((datetime.date.today()-datetime.timedelta(days=45)).isoformat())")"
printf -- '---\ndoc: x\n---\n' > "audit-$old.md"
out="$(bash scripts/session-brief.sh 2>/dev/null)"
if ! grep -q "Drift audit: last run $old (45 days ago) - overdue" <<<"$out"; then
  echo "FAIL case 2: expected overdue line for $old, got:"; echo "$out"; fail=1
fi

# case 3: an audit 31 days old is overdue - the boundary is strictly greater than 30
rm -f audit-*.md
d31="$(python3 -c "import datetime;print((datetime.date.today()-datetime.timedelta(days=31)).isoformat())")"
printf -- '---\ndoc: x\n---\n' > "audit-$d31.md"
out="$(bash scripts/session-brief.sh 2>/dev/null)"
if ! grep -q "Drift audit: last run $d31 (31 days ago) - overdue" <<<"$out"; then
  echo "FAIL case 3: expected overdue at 31 days, got:"; echo "$out"; fail=1
fi

# case 4: exactly 30 days is not overdue, and the brief still ran to completion
rm -f audit-*.md
d30="$(python3 -c "import datetime;print((datetime.date.today()-datetime.timedelta(days=30)).isoformat())")"
printf -- '---\ndoc: x\n---\n' > "audit-$d30.md"
out="$(bash scripts/session-brief.sh 2>/dev/null)"
if grep -q "Drift audit" <<<"$out"; then
  echo "FAIL case 4: expected no overdue line at exactly 30 days, got:"; echo "$out"; fail=1
fi
if ! grep -q "Read order:" <<<"$out"; then
  echo "FAIL case 4: the brief did not run to completion"; fail=1
fi

[ "$fail" -eq 0 ] && echo "ok"
exit "$fail"
