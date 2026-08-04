#!/usr/bin/env bash
# Verifies the fixture injects every defect it claims to. Run from the docs repo root.
set -uo pipefail
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail=0

out="$(python3 scripts/drift-fixture.py "$TMP/corpus")"
echo "$out"

for pair in PR-1 PR-3 PR-4 PR-6; do
  grep -q "^EXPECT $pair " <<<"$out" || { echo "FAIL: no EXPECT line for $pair"; fail=1; }
done

# the injections must actually be present in the copy
grep -q "INV-99" "$TMP/corpus/60-decisions/ADR-0001-storefront-stack.md" \
  || { echo "FAIL PR-3: dangling INV-99 not injected"; fail=1; }
grep -q "^status: draft" "$TMP/corpus/60-decisions/ADR-0001-storefront-stack.md" \
  || { echo "FAIL PR-4: frontmatter status not contradicted"; fail=1; }
grep -q "prints the current phase's item 1" "$TMP/corpus/40-devops/README.md" \
  || { echo "FAIL PR-1: stale mechanism description not injected"; fail=1; }
grep -q "Every table must be alphabetised" "$TMP/corpus/CONVENTIONS.md" \
  || { echo "FAIL PR-6: uninstrumented rule not injected"; fail=1; }

# the original corpus must be untouched
git diff --quiet || { echo "FAIL: fixture modified the real corpus"; fail=1; }

[ "$fail" -eq 0 ] && echo "ok"
exit "$fail"
