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

# the fixture must declare the noise it manufactures, or a reader of a run
# cannot tell a fixture artefact from an agent regression
for cls in tooling-not-copied answer-key-not-copied repaired-routing; do
  grep -q "^NOISE $cls " <<<"$out" || { echo "FAIL: no NOISE manifest line for $cls"; fail=1; }
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

# the copy must be clean under its own hygiene check. Broken references left by
# the exclusions are indistinguishable, to a reader of a fixture run, from a
# regression the agent was supposed to catch.
( cd "$TMP/corpus" && python3 scripts/docs-check.py > "$TMP/dc.out" 2>&1 )
dc=$?
grep -q "broken reference" "$TMP/dc.out" \
  && { echo "FAIL: the fixture leaves broken references in the copy:"; grep "broken reference" "$TMP/dc.out"; fail=1; }
[ "$dc" -eq 0 ] || { echo "FAIL: docs-check.py exits $dc inside the copy; see errors above"; sed -n '/^ERRORS/,/^$/p' "$TMP/dc.out"; fail=1; }

# the guard must refuse a destructive target: descendants, the corpus itself,
# ancestors, $HOME and the filesystem root - `..` is the shape that reached
# rmtree before, and it is the shape typed elsewhere in this repo. Checked as a
# pure function, never by invoking the script against these paths: the script
# deletes its target, so running it against '.', '..', "$HOME" or '/' to prove
# it refuses them would - the moment the guard being tested ever regressed -
# destroy the developer's real working directory, its parent, home, or the
# whole filesystem. importlib loads check_target() without running main(), so
# no rmtree is reachable no matter what the function decides.
if ! guard_out="$(python3 - <<'PYEOF'
import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location("drift_fixture", "scripts/drift-fixture.py")
drift_fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drift_fixture)

dangerous = [".", "..", str(pathlib.Path.home()), "/"]
not_refused = []
for p in dangerous:
    try:
        drift_fixture.check_target(pathlib.Path(p))
        not_refused.append(p)
    except SystemExit:
        pass

if not_refused:
    print("did not raise SystemExit for: " + ", ".join(not_refused))
    sys.exit(1)
PYEOF
)"; then
  echo "FAIL: check_target() did not refuse a dangerous path: $guard_out"; fail=1
fi

# an existing directory this script did not build must not be deleted - the one
# end-to-end invocation that exercises a refusal, and it is safe because
# "$TMP/not-a-fixture" is a throwaway directory, not a real ancestor.
mkdir -p "$TMP/not-a-fixture" && : > "$TMP/not-a-fixture/keepme"
if python3 scripts/drift-fixture.py "$TMP/not-a-fixture" >/dev/null 2>&1; then
  echo "FAIL: fixture overwrote a directory carrying no sentinel"; fail=1
fi
[ -f "$TMP/not-a-fixture/keepme" ] || { echo "FAIL: fixture deleted a directory it did not build"; fail=1; }

# an existing EMPTY directory carries no sentinel but has nothing to protect,
# and is exactly the shape /tmp/drift-fixture is in the first time the
# documented invocation runs - it must be accepted, not refused.
mkdir -p "$TMP/empty-target"
if ! python3 scripts/drift-fixture.py "$TMP/empty-target" >/dev/null 2>&1; then
  echo "FAIL: fixture refused an existing empty directory"; fail=1
fi
[ -f "$TMP/empty-target/.drift-fixture" ] || { echo "FAIL: fixture did not build into the accepted empty directory"; fail=1; }

# a directory it did build carries the sentinel and may be rebuilt over
[ -f "$TMP/corpus/.drift-fixture" ] || { echo "FAIL: no sentinel written into the fixture"; fail=1; }
python3 scripts/drift-fixture.py "$TMP/corpus" >/dev/null 2>&1 \
  || { echo "FAIL: fixture cannot rebuild over its own previous run"; fail=1; }

# the original corpus must be untouched
git diff --quiet || { echo "FAIL: fixture modified the real corpus"; fail=1; }

[ "$fail" -eq 0 ] && echo "ok"
exit "$fail"
