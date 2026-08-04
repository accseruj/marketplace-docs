#!/usr/bin/env bash
# Verifies scripts/queue-check.py against injected violations. Run from the docs repo root.
set -u
DOCS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail=0

# Builds a throwaway repo root containing only what queue-check reads.
# $1 = jsonl body, $2 = roadmap body (may be empty)
mkfixture() {
  local dir; dir="$(mktemp -d)"
  mkdir -p "$dir/.beads" "$dir/00-product"
  printf '%s\n' "$1" > "$dir/.beads/issues.jsonl"
  printf '%s\n' "${2:-}" > "$dir/00-product/roadmap.md"
  : > "$dir/subjects.txt"
  echo "$dir"
}

run() { python3 "$DOCS/scripts/queue-check.py" --root "$1" --subjects-file "$1/subjects.txt" 2>&1; }
code() { python3 "$DOCS/scripts/queue-check.py" --root "$1" --subjects-file "$1/subjects.txt" >/dev/null 2>&1; echo $?; }

EPIC='{"id":"q-1","title":"Phase 0 - Platform skeleton","issue_type":"epic","status":"open","labels":["backend"],"description":"Success Criteria: x"}'
CHILD='{"id":"q-1.1","title":"child","issue_type":"task","status":"open","labels":["backend"],"description":"Acceptance Criteria: x","dependencies":[{"issue_id":"q-1.1","depends_on_id":"q-1","type":"parent-child"}]}'

# case 1: a well-formed pair passes
d="$(mkfixture "$EPIC
$CHILD" "## Phase 0 - Platform skeleton")"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 1: expected exit 0, got:"; run "$d"; fail=1; fi
rm -rf "$d"

# case 2 (WQ-C1): a child carrying two layer labels fails
TWO='{"id":"q-1.1","title":"child","issue_type":"task","status":"open","labels":["backend","frontend"],"description":"Acceptance Criteria: x","dependencies":[{"issue_id":"q-1.1","depends_on_id":"q-1","type":"parent-child"}]}'
d="$(mkfixture "$EPIC
$TWO" "## Phase 0 - Platform skeleton")"
if [ "$(code "$d")" = "0" ]; then echo "FAIL case 2: two layer labels did not fail"; fail=1; fi
if ! run "$d" | grep -q "WQ-C1"; then echo "FAIL case 2: error is not attributed to WQ-C1"; fail=1; fi
rm -rf "$d"

# case 3 (WQ-C1): a child carrying no layer label fails
NONE='{"id":"q-1.1","title":"child","issue_type":"task","status":"open","labels":[],"description":"Acceptance Criteria: x","dependencies":[{"issue_id":"q-1.1","depends_on_id":"q-1","type":"parent-child"}]}'
d="$(mkfixture "$EPIC
$NONE" "## Phase 0 - Platform skeleton")"
if [ "$(code "$d")" = "0" ]; then echo "FAIL case 3: missing layer label did not fail"; fail=1; fi
rm -rf "$d"

# case 4 (WQ-C1): an issue with no parent needs no layer label - WQ-05
LOOSE='{"id":"q-9","title":"tidy a script","issue_type":"chore","status":"open","description":"x"}'
d="$(mkfixture "$LOOSE" "")"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 4: parentless issue was required to carry a layer:"; run "$d"; fail=1; fi
rm -rf "$d"

[ "$fail" = "0" ] && echo "queue-check tests: ok"
exit "$fail"
