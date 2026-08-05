#!/usr/bin/env bash
# Verifies scripts/queue-check.py against injected violations. Run from the docs repo root.
set -uo pipefail
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
out="$(run "$d")"; if ! grep -q "WQ-C1" <<<"$out"; then echo "FAIL case 2: error is not attributed to WQ-C1"; fail=1; fi
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

# case 5 (WQ-C3): a task with no Acceptance Criteria fails
NOAC='{"id":"q-2","title":"loose task","issue_type":"task","status":"open","description":"no sections here"}'
d="$(mkfixture "$NOAC" "")"
if [ "$(code "$d")" = "0" ]; then echo "FAIL case 5: missing Acceptance Criteria did not fail"; fail=1; fi
out="$(run "$d")"; if ! grep -q "WQ-C3" <<<"$out"; then echo "FAIL case 5: error is not attributed to WQ-C3"; fail=1; fi
rm -rf "$d"

# case 6 (WQ-C3): a closed issue is not judged on sections
CLOSED='{"id":"q-3","title":"done","issue_type":"task","status":"closed","description":"no sections here"}'
d="$(mkfixture "$CLOSED" "")"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 6: a closed issue was judged:"; run "$d"; fail=1; fi
rm -rf "$d"

# case 7 (WQ-C3): mentioning the phrase in prose is not a section
PROSE='{"id":"q-5","title":"loose task","issue_type":"task","status":"open","description":"no acceptance criteria defined yet, TBD"}'
d="$(mkfixture "$PROSE" "")"
if [ "$(code "$d")" = "0" ]; then echo "FAIL case 7: a prose mention counted as a section"; fail=1; fi
rm -rf "$d"

# case 8 (WQ-C3): a real section opening a line passes
REAL='{"id":"q-6","title":"loose task","issue_type":"task","status":"open","description":"context here\n\nAcceptance Criteria: the thing is observable"}'
d="$(mkfixture "$REAL" "")"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 8: a real section was rejected:"; run "$d"; fail=1; fi
rm -rf "$d"

# case 9 (WQ-C4): an open issue named in a commit subject warns but does not fail
OPEN_ISSUE='{"id":"q-4","title":"open work","issue_type":"chore","status":"open","description":"x"}'
d="$(mkfixture "$OPEN_ISSUE" "")"
echo "do the thing (q-4)" > "$d/subjects.txt"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 9: WQ-C4 must warn, not fail"; fail=1; fi
out="$(run "$d")"
if ! grep -q "WQ-C4" <<<"$out"; then echo "FAIL case 9: no WQ-C4 warning was emitted"; fail=1; fi
rm -rf "$d"

# case 10 (WQ-C4): the same subject against a closed issue says nothing
CLOSED_ISSUE='{"id":"q-4","title":"open work","issue_type":"chore","status":"closed","description":"x"}'
d="$(mkfixture "$CLOSED_ISSUE" "")"
echo "do the thing (q-4)" > "$d/subjects.txt"
out="$(run "$d")"
if grep -q "WQ-C4" <<<"$out"; then echo "FAIL case 10: a closed issue was reported as an orphan"; fail=1; fi
rm -rf "$d"

# case 11 (WQ-C2): a roadmap phase with no epic fails
d="$(mkfixture "$EPIC" "## Phase 0 - Platform skeleton

## Phase 1 - Flagship storefront to production")"
if [ "$(code "$d")" = "0" ]; then echo "FAIL case 11: a phase with no epic did not fail"; fail=1; fi
out="$(run "$d")"; if ! grep -q "WQ-C2" <<<"$out"; then echo "FAIL case 11: error is not attributed to WQ-C2"; fail=1; fi
rm -rf "$d"

# case 12 (WQ-C2): the '(current)' marker is not part of the name
d="$(mkfixture "$EPIC" "## Phase 0 - Platform skeleton (current)")"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 12: '(current)' was treated as part of the phase name:"; run "$d"; fail=1; fi
rm -rf "$d"

[ "$fail" = "0" ] && echo "queue-check tests: ok"
exit "$fail"
