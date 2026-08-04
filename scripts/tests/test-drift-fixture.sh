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

# the answer key must not travel with the copy
[ -e "$TMP/corpus/.superpowers" ] && { echo "FAIL: .superpowers copied into the fixture"; fail=1; }
[ -e "$TMP/corpus/40-devops/drift-audit-plan.md" ] && { echo "FAIL: the plan quotes every injection and must not be copied"; fail=1; }
[ -e "$TMP/corpus/40-devops/drift-audit-spec.md" ] && { echo "FAIL: the spec must not be copied"; fail=1; }
grep -rq "EXPECT PR-" "$TMP/corpus" && { echo "FAIL: EXPECT lines are readable inside the fixture"; fail=1; }

# the evidence each pair needs must survive the copy
for needed in scripts/session-brief.sh scripts/docs-check.py; do
  [ -f "$TMP/corpus/$needed" ] || { echo "FAIL: $needed missing from the copy; a pair becomes undetectable"; fail=1; }
done
ls "$TMP/corpus"/audit-*.md >/dev/null 2>&1 && { echo "FAIL: an audit report was copied; AUD-14 quotes an injection verbatim"; fail=1; }

# the guard must refuse a destructive target
if python3 scripts/drift-fixture.py . >/dev/null 2>&1; then
  echo "FAIL: fixture did not refuse to build inside the corpus"; fail=1
fi

# the original corpus must be untouched
git diff --quiet || { echo "FAIL: fixture modified the real corpus"; fail=1; }

[ "$fail" -eq 0 ] && echo "ok"
exit "$fail"
