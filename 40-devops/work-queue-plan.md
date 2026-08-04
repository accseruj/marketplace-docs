---
doc: work-queue-plan
purpose: Task-by-task implementation plan for the queue structure specified in 40-devops/work-queue-spec.md.
read_when: implementing the work-queue structure or its checks
status: draft
updated: 2026-08-04
related: [40-devops/work-queue-spec.md, CONVENTIONS.md, 00-product/roadmap.md]
---

# Work queue implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the queue structure specified in `40-devops/work-queue-spec.md` — one label axis, phases as epics, human gates — and the four checks that keep it from rotting.

**Architecture:** A single new instrument, `scripts/queue-check.py`, reads the git-tracked beads export and `git log`; it never invokes `bd`, because CI installs Python only. Checks are built **before** the data they police, each proven against an injected violation on a synthetic fixture rather than against the live queue. The data migration (retype, epics, labels, gates) follows, and CI wiring comes last so the pipeline is never knowingly red.

**Tech Stack:** Python 3.12 (matching `scripts/docs-check.py` and the CI workflow), POSIX/bash shell, `bd` 1.0.5 for the migration tasks only.

## Global Constraints

- All docs are English. Conversation with the operator is Russian. (`CONVENTIONS.md`)
- Paths inside docs are relative to the docs repo root — `00-product/roadmap.md`, never prefixed with the repo directory name.
- Machine-first writing: single-line facts, conclusions first, explicit numbers, stable IDs.
- Every new file under the repo root needs a routing-table row in `INDEX.md`, except under `.claude/`, `.beads/`, `.github/`, `scripts/`.
- `python3 scripts/docs-check.py` must exit 0 before every commit. Never pipe it — `... > out 2>&1; echo $?`, because a pipe reports the exit code of the last stage.
- Commit messages state what was decided and why, not which files changed. Append the `bd` issue id in parentheses when the work belongs to one.
- `bd dolt push` after any task that writes to the queue. `git push` does not carry issues (ADR-0008).
- The layer vocabulary is closed and exactly these seven: `infrastructure`, `frontend`, `backend`, `catalog`, `feeds`, `sourcing`, `product`.
- Never use `bd edit` — it needs an interactive editor. Use `bd update` with flags.
- Shell must work on macOS (this machine) and WSL Ubuntu (`40-devops/README.md`).

---

### Task 1: `queue-check.py` skeleton and WQ-C1 (layer label)

**Files:**
- Create: `scripts/queue-check.py`
- Create: `scripts/tests/test-queue-check.sh`

**Interfaces:**
- Produces: `queue-check.py --root <dir>` reads `<dir>/.beads/issues.jsonl`, prints `ERRORS (n):` lines, exits 1 on any error and 0 when clean. Tasks 2-4 add checks to the same `errors` list and the same test file.
- Produces: `parent_of(issue) -> str | None`, reading `dependencies[].type == "parent-child"`. Used by `check_layers` only; later tasks do not call it.
- Produces: `LAYERS` — the seven-value frozenset.

- [ ] **Step 1: Write the failing test**

Create `scripts/tests/test-queue-check.sh`:

```bash
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash scripts/tests/test-queue-check.sh`
Expected: FAIL — `can't open file '.../scripts/queue-check.py'`, exit non-zero.

- [ ] **Step 3: Write the minimal implementation**

Create `scripts/queue-check.py`:

```python
#!/usr/bin/env python3
"""Work-queue checks. Run from the docs repo root: python3 scripts/queue-check.py

Enforces 40-devops/work-queue-spec.md:
  WQ-C1  every issue with a parent carries exactly one layer label
Reads .beads/issues.jsonl, which is tracked in git. Never invokes bd: CI
installs Python only, and a check that shells out to a missing binary is a
green tick with nothing behind it.
Exit code 1 on any error.
"""
import argparse, json, pathlib, sys

LAYERS = frozenset({"infrastructure", "frontend", "backend",
                    "catalog", "feeds", "sourcing", "product"})

def load_issues(root):
    path = root / ".beads" / "issues.jsonl"
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out

def parent_of(issue):
    # The export carries no parent field; the link is a dependency row.
    # Reading the dot in the id would work today and break the day an id
    # legitimately contains one.
    for dep in issue.get("dependencies") or []:
        if dep.get("type") == "parent-child" and dep.get("issue_id") == issue.get("id"):
            return dep.get("depends_on_id")
    return None

def check_layers(issues):
    errors = []
    for i in issues:
        if i.get("status") == "closed" or parent_of(i) is None:
            continue
        found = sorted(set(i.get("labels") or []) & LAYERS)
        if len(found) != 1:
            errors.append(f"WQ-C1 {i['id']}: has a parent but carries {len(found)} layer labels {found}")
    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument("--subjects-file", default=None)
    args = ap.parse_args()
    root = pathlib.Path(args.root)

    issues = load_issues(root)
    errors = check_layers(issues)

    print(f"checked {len(issues)} issues\n")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print("  " + e)
        print()
    print("ok" if not errors else "FAILED")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash scripts/tests/test-queue-check.sh`
Expected: `queue-check tests: ok`, exit 0.

- [ ] **Step 5: Confirm it is vacuum-safe on the live queue**

Run: `python3 scripts/queue-check.py > /tmp/qc.out 2>&1; echo $?`
Expected: exit 0. No issue has a parent yet, so WQ-C1 has nothing to judge. This is expected and temporary — Task 6 creates the parents.

- [ ] **Step 6: Commit**

```bash
git add scripts/queue-check.py scripts/tests/test-queue-check.sh
git commit -m "check the layer label on the export rather than through bd"
```

---

### Task 2: WQ-C3 (required sections per type)

**Files:**
- Modify: `scripts/queue-check.py` (add `REQUIRED_SECTIONS`, `check_sections`, call it in `main`)
- Modify: `scripts/tests/test-queue-check.sh` (append cases 5-6 before the final `[ "$fail" = "0" ]` line)

**Interfaces:**
- Consumes: `load_issues`, from Task 1.
- Produces: `check_sections(issues) -> list[str]`.

- [ ] **Step 1: Write the failing test**

Append to `scripts/tests/test-queue-check.sh`, immediately before the `[ "$fail" = "0" ]` line:

```bash
# case 5 (WQ-C3): a task with no Acceptance Criteria fails
NOAC='{"id":"q-2","title":"loose task","issue_type":"task","status":"open","description":"no sections here"}'
d="$(mkfixture "$NOAC" "")"
if [ "$(code "$d")" = "0" ]; then echo "FAIL case 5: missing Acceptance Criteria did not fail"; fail=1; fi
if ! run "$d" | grep -q "WQ-C3"; then echo "FAIL case 5: error is not attributed to WQ-C3"; fail=1; fi
rm -rf "$d"

# case 6 (WQ-C3): a closed issue is not judged on sections
CLOSED='{"id":"q-3","title":"done","issue_type":"task","status":"closed","description":"no sections here"}'
d="$(mkfixture "$CLOSED" "")"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 6: a closed issue was judged:"; run "$d"; fail=1; fi
rm -rf "$d"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash scripts/tests/test-queue-check.sh`
Expected: `FAIL case 5: missing Acceptance Criteria did not fail`, exit 1.

- [ ] **Step 3: Write the minimal implementation**

Add to `scripts/queue-check.py`, after `check_layers`:

```python
# Mirrors `bd lint`'s requirements rather than calling it. Four lines of
# duplication buys a check that runs where bd is not installed.
REQUIRED_SECTIONS = {
    "task": ["Acceptance Criteria"],
    "feature": ["Acceptance Criteria"],
    "bug": ["Steps to Reproduce", "Acceptance Criteria"],
    "epic": ["Success Criteria"],
}

def check_sections(issues):
    errors = []
    for i in issues:
        if i.get("status") == "closed":
            continue
        body = i.get("description") or ""
        for section in REQUIRED_SECTIONS.get(i.get("issue_type", ""), []):
            if section.lower() not in body.lower():
                errors.append(f"WQ-C3 {i['id']}: {i.get('issue_type')} is missing section '{section}'")
    return errors
```

Change the `errors` line in `main` to:

```python
    errors = check_layers(issues) + check_sections(issues)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash scripts/tests/test-queue-check.sh`
Expected: `queue-check tests: ok`, exit 0.

- [ ] **Step 5: Record the live failure count without fixing it**

Run: `python3 scripts/queue-check.py > /tmp/qc.out 2>&1; echo $?; head -5 /tmp/qc.out`
Expected: exit 1, roughly 31 WQ-C3 errors — no existing issue has an Acceptance Criteria section. **Do not backfill descriptions here.** Task 5 handles it, and the number belongs in that task's commit message.

- [ ] **Step 6: Commit**

```bash
git add scripts/queue-check.py scripts/tests/test-queue-check.sh
git commit -m "restate bd lint's section rule where bd is not installed"
```

---

### Task 3: WQ-C4 (an open issue named in a commit subject)

**Files:**
- Modify: `scripts/queue-check.py` (add `check_orphans`, `commit_subjects`; call in `main`)
- Modify: `scripts/tests/test-queue-check.sh` (append cases 7-8)

**Interfaces:**
- Consumes: `load_issues`, from Task 1.
- Produces: `check_orphans(issues, subjects) -> list[str]`; `commit_subjects(root, subjects_file) -> list[str]`, which reads `subjects_file` when given and otherwise runs `git log --format=%s` in `root`.

- [ ] **Step 1: Write the failing test**

Append to `scripts/tests/test-queue-check.sh`, before the `[ "$fail" = "0" ]` line:

```bash
# case 7 (WQ-C4): an open issue named in a commit subject fails
OPEN_ISSUE='{"id":"q-4","title":"open work","issue_type":"chore","status":"open","description":"x"}'
d="$(mkfixture "$OPEN_ISSUE" "")"
echo "do the thing (q-4)" > "$d/subjects.txt"
if [ "$(code "$d")" = "0" ]; then echo "FAIL case 7: open issue in a commit subject did not fail"; fail=1; fi
if ! run "$d" | grep -q "WQ-C4"; then echo "FAIL case 7: error is not attributed to WQ-C4"; fail=1; fi
rm -rf "$d"

# case 8 (WQ-C4): the same subject against a closed issue passes
CLOSED_ISSUE='{"id":"q-4","title":"open work","issue_type":"chore","status":"closed","description":"x"}'
d="$(mkfixture "$CLOSED_ISSUE" "")"
echo "do the thing (q-4)" > "$d/subjects.txt"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 8: a closed issue was reported as an orphan:"; run "$d"; fail=1; fi
rm -rf "$d"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash scripts/tests/test-queue-check.sh`
Expected: `FAIL case 7: open issue in a commit subject did not fail`, exit 1.

- [ ] **Step 3: Write the minimal implementation**

Add to `scripts/queue-check.py` (and add `re, subprocess` to the imports):

```python
def commit_subjects(root, subjects_file):
    if subjects_file:
        return pathlib.Path(subjects_file).read_text(encoding="utf-8").splitlines()
    try:
        out = subprocess.run(["git", "-C", str(root), "log", "--format=%s"],
                             capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []          # no git history reachable: nothing to check, not an error
    return out.stdout.splitlines()

def check_orphans(issues, subjects):
    open_ids = {i["id"] for i in issues if i.get("status") != "closed"}
    errors = []
    for subject in subjects:
        for ref in re.findall(r"\(([a-z0-9]+-[a-z0-9.]+)\)", subject):
            if ref in open_ids:
                errors.append(f"WQ-C4 {ref}: named in a commit subject but still open - {subject[:60]!r}")
    return errors
```

Change the `errors` line in `main` to:

```python
    subjects = commit_subjects(root, args.subjects_file)
    errors = check_layers(issues) + check_sections(issues) + check_orphans(issues, subjects)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash scripts/tests/test-queue-check.sh`
Expected: `queue-check tests: ok`, exit 0.

- [ ] **Step 5: Commit**

```bash
git add scripts/queue-check.py scripts/tests/test-queue-check.sh
git commit -m "catch issues worked on in a commit but never closed"
```

---

### Task 4: WQ-C2 (roadmap phases against phase epics)

**Files:**
- Modify: `scripts/queue-check.py` (add `phase_headings`, `check_phases`; call in `main`)
- Modify: `scripts/tests/test-queue-check.sh` (append cases 9-10)

**Interfaces:**
- Consumes: `load_issues`, from Task 1.
- Produces: `check_phases(issues, roadmap_text) -> list[str]`. Matching is on the exact phase name: the roadmap heading `## Phase 0 - Platform skeleton` requires an epic titled `Phase 0 - Platform skeleton`. The trailing ` (current)` marker in the roadmap is stripped before comparing.

- [ ] **Step 1: Write the failing test**

Append to `scripts/tests/test-queue-check.sh`, before the `[ "$fail" = "0" ]` line:

```bash
# case 9 (WQ-C2): a roadmap phase with no epic fails
d="$(mkfixture "$EPIC" "## Phase 0 - Platform skeleton

## Phase 1 - Flagship storefront to production")"
if [ "$(code "$d")" = "0" ]; then echo "FAIL case 9: a phase with no epic did not fail"; fail=1; fi
if ! run "$d" | grep -q "WQ-C2"; then echo "FAIL case 9: error is not attributed to WQ-C2"; fail=1; fi
rm -rf "$d"

# case 10 (WQ-C2): the '(current)' marker is not part of the name
d="$(mkfixture "$EPIC" "## Phase 0 - Platform skeleton (current)")"
if [ "$(code "$d")" != "0" ]; then echo "FAIL case 10: '(current)' was treated as part of the phase name:"; run "$d"; fail=1; fi
rm -rf "$d"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash scripts/tests/test-queue-check.sh`
Expected: `FAIL case 9: a phase with no epic did not fail`, exit 1.

- [ ] **Step 3: Write the minimal implementation**

Add to `scripts/queue-check.py`:

```python
def phase_headings(roadmap_text):
    names = []
    for line in roadmap_text.splitlines():
        m = re.match(r"^##\s+(Phase\s.+?)\s*$", line)
        if m:
            names.append(re.sub(r"\s*\(current\)\s*$", "", m.group(1)))
    return names

def check_phases(issues, roadmap_text):
    wanted = phase_headings(roadmap_text)
    have = {i["title"].strip() for i in issues
            if i.get("issue_type") == "epic" and i.get("title", "").startswith("Phase ")}
    errors = []
    for name in wanted:
        if name not in have:
            errors.append(f"WQ-C2 roadmap phase {name!r} has no epic with that exact title")
    for title in sorted(have - set(wanted)):
        errors.append(f"WQ-C2 phase epic {title!r} matches no roadmap heading")
    return errors
```

In `main`, read the roadmap and extend the error list:

```python
    roadmap = root / "00-product" / "roadmap.md"
    roadmap_text = roadmap.read_text(encoding="utf-8") if roadmap.exists() else ""
    errors = (check_layers(issues) + check_sections(issues)
              + check_orphans(issues, subjects) + check_phases(issues, roadmap_text))
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash scripts/tests/test-queue-check.sh`
Expected: `queue-check tests: ok`, exit 0.

- [ ] **Step 5: Commit**

```bash
git add scripts/queue-check.py scripts/tests/test-queue-check.sh
git commit -m "hold roadmap phases and phase epics to the same names"
```

---

### Task 5: Retype the existing 31 issues (WQ-03)

**Files:**
- Modify: the beads database (no repo files except the regenerated `.beads/issues.jsonl`)

**Interfaces:**
- Consumes: nothing.
- Produces: every open issue typed `decision`, `task`, `chore` or `feature`, and every open issue carrying the section its type requires.

- [ ] **Step 1: Retype the decisions**

These 12 exist to choose between options, which is what `decision` means:

```bash
bd update docs-47o docs-9fl docs-dqt docs-dvg docs-1kr docs-q6x \
          docs-97h docs-cn2 docs-muc docs-npe docs-u26 docs-0u3 --type decision
```

- [ ] **Step 2: Retype the chores**

Repo and tooling upkeep, no product outcome:

```bash
bd update docs-nqk docs-8gf docs-i1w docs-b83 docs-3nj --type chore
```

- [ ] **Step 3: Leave the rest as `task` and verify the split**

Run: `bd list --status open --json | python3 -c "import json,sys,collections; d=json.load(sys.stdin); print(collections.Counter(i['issue_type'] for i in (d if isinstance(d,list) else d['issues'])))"`
Expected: `Counter({'decision': 12, 'task': 14, 'chore': 5})`. If the counts differ, a `bd update` silently matched nothing — re-run the failing id alone and read its output.

- [ ] **Step 4: Add the missing Acceptance Criteria sections**

WQ-C3 fails on all 14 open `task` issues; `decision` and `chore` require no section.

**Do not use `bd note`** — it writes the `notes` field, and WQ-C3 reads `description`. Appending without losing the existing text needs a read-modify-write:

```bash
append_ac() {   # $1 = issue id, $2 = the criterion
  local tmp; tmp="$(mktemp)"
  bd show "$1" --json | python3 -c "
import json,sys
d = json.load(sys.stdin)
o = d[0] if isinstance(d, list) else d
sys.stdout.write(o.get('description') or '')
" > "$tmp"
  printf '\n\nAcceptance Criteria: %s\n' "$2" >> "$tmp"
  bd update "$1" --body-file "$tmp"
  rm -f "$tmp"
}
```

Worked example, so the shape of a real criterion is not left to taste:

```bash
append_ac docs-rt4 "every version claim in 10-architecture/c4-container.md cites a primary source, or is marked unverified"
append_ac docs-jvy "a real feed file from a named NL-warehoused distributor is saved in the repo, with its field list recorded"
```

Write one per issue. "Done when done" passes the check and defeats it.

- [ ] **Step 5: Verify and push**

Run: `python3 scripts/queue-check.py > /tmp/qc.out 2>&1; echo $?; cat /tmp/qc.out`
Expected: exit 0 — WQ-C3 clean. WQ-C1 and WQ-C2 are still vacuum-passing; Task 6 and Task 7 give them something to judge.

```bash
bd dolt push
git add .beads/issues.jsonl
git commit -m "type the queue by what each issue is, and say what ends each task"
```

---

### Task 6: Phase epics, layer labels, parents (WQ-04, WQ-05)

**Files:**
- Modify: the beads database and the regenerated `.beads/issues.jsonl`

**Interfaces:**
- Consumes: the retyped issues from Task 5.
- Produces: five epics titled exactly as the `00-product/roadmap.md` headings, each carrying one layer label; every phase-owned issue reparented under one of them.

- [ ] **Step 1: Create the five phase epics**

Titles must match `00-product/roadmap.md` headings exactly, minus ` (current)` — WQ-C2 compares strings:

```bash
bd create "Phase -1 - Foundations on paper" -t epic -p 0 --description "Success Criteria: every VC stage has a named owner component, a defined contract, and an answered automation-readiness test; ADR-0005 decided; returns policy set; reservation strategy set."
bd create "Phase 0 - Platform skeleton" -t epic -p 1 --description "Success Criteria: measured LCP/INP/CLS on a real category and product page; measured cost per 1M requests."
bd create "Phase 1 - Flagship storefront to production" -t epic -p 2 --description "Success Criteria: field CWV pass; a real order sourced, purchased, shipped and tracked without manual intervention."
bd create "Phase 2 - Templatisation and second supplier" -t epic -p 3 --description "Success Criteria: second storefront launched purely by configuration; second supplier live without core changes."
bd create "Phase 3 - Rollout" -t epic -p 3 --description "Success Criteria: SC-01, SC-04, SC-07."
```

Record the five returned ids; the steps below call them `$P_1 $P0 $P1 $P2 $P3`.

- [ ] **Step 2: Order the phases**

```bash
bd dep add "$P0" "$P_1" --type blocks
bd dep add "$P1" "$P0"  --type blocks
bd dep add "$P2" "$P1"  --type blocks
bd dep add "$P3" "$P2"  --type blocks
```

Verify: `bd dep cycles` prints none, and `bd ready` no longer lists Phase 1-3 epics.

- [ ] **Step 3: Label each epic with its layer**

Phase epics span layers, so each takes the layer of the work it mostly carries; children that differ get their own label in Step 5.

```bash
bd label add "$P_1" product
bd label add "$P0" infrastructure
bd label add "$P1" frontend
bd label add "$P2" frontend
bd label add "$P3" product
```

- [ ] **Step 4: Reparent the existing issues**

`bd update --parent` moves an issue under an epic. Phase -1 takes everything currently open except the four that are explicitly Phase 0+ work:

```bash
bd update docs-4qa docs-2w2 docs-rt3 docs-wwe --parent "$P0"
bd update docs-47o docs-9fl docs-dqt docs-dvg docs-jvy docs-n1f docs-pjl \
          docs-1kr docs-q6x docs-97h docs-cn2 docs-ecw docs-npe docs-u26 \
          docs-xa6 docs-72g docs-e2h docs-muc docs-rt4 docs-ruf --parent "$P_1"
```

Left deliberately parentless, per WQ-05 — repo and tooling upkeep belongs to no phase: `docs-0u3`, `docs-3nj`, `docs-8gf`, `docs-b83`, `docs-i1w`, `docs-nqk`, `docs-uoo`.

- [ ] **Step 5: Correct the inherited labels that are wrong**

Reparenting does not re-run inheritance — inheritance applies at creation. Set the layer explicitly on every reparented issue:

```bash
bd label add docs-47o docs-dqt docs-jvy catalog
bd label add docs-2w2 docs-rt3 backend
bd label add docs-wwe docs-4qa frontend
bd label add docs-9fl docs-dvg docs-n1f docs-pjl docs-1kr docs-q6x docs-97h \
             docs-cn2 docs-ecw docs-npe docs-u26 docs-xa6 docs-72g docs-e2h \
             docs-muc docs-rt4 docs-ruf product
```

- [ ] **Step 6: Verify WQ-C1 and WQ-C2 now have something to judge, and pass**

Run: `python3 scripts/queue-check.py > /tmp/qc.out 2>&1; echo $?; cat /tmp/qc.out`
Expected: exit 0, and `checked 38 issues` — 33 existing plus 5 epics.

Then prove the check is not vacuum-passing: add a second layer label to one issue, re-run, confirm exit 1 and a WQ-C1 line, then remove it.

```bash
bd label add docs-2w2 frontend
python3 scripts/queue-check.py > /tmp/qc.out 2>&1; echo $?   # expect 1
bd label remove docs-2w2 frontend
python3 scripts/queue-check.py > /tmp/qc.out 2>&1; echo $?   # expect 0
```

- [ ] **Step 7: Confirm the queue actually narrowed**

Run: `bd ready | tail -3`
Expected: fewer ready issues than the 21 recorded on 2026-08-04. Record the new number — it goes in the commit message and is the only evidence this whole design worked.

- [ ] **Step 8: Commit**

```bash
bd dolt push
git add .beads/issues.jsonl
git commit -m "give the queue a phase graph, so bd ready stops answering with everything"
```

---

### Task 7: Exit gates (WQ-06)

**Files:**
- Modify: the beads database and the regenerated `.beads/issues.jsonl`

**Interfaces:**
- Consumes: the phase epic ids from Task 6.
- Produces: four human gates, each blocking the next phase epic.

- [ ] **Step 1: Create the four gates**

```bash
bd gate create --type=human --blocks "$P0" --reason "Phase -1 exit gate: see 00-product/roadmap.md"
bd gate create --type=human --blocks "$P1" --reason "Phase 0 exit gate: see 00-product/roadmap.md"
bd gate create --type=human --blocks "$P2" --reason "Phase 1 exit gate: see 00-product/roadmap.md"
bd gate create --type=human --blocks "$P3" --reason "Phase 2 exit gate: see 00-product/roadmap.md"
```

The `--reason` points at the roadmap rather than restating the criteria: WQ-05 gives the prose one owner.

- [ ] **Step 2: Verify the gates block and stay out of the way**

Run: `bd list | grep -c "exit gate"`
Expected: `0` — gates are hidden from `bd list` by default.

Run: `bd list --include-gates | grep -c "exit gate"`
Expected: `4`.

- [ ] **Step 3: Verify queue-check still passes**

Run: `python3 scripts/queue-check.py > /tmp/qc.out 2>&1; echo $?`
Expected: exit 0. Gate issues have no parent, so WQ-C1 skips them; if they are exported with a parent link, WQ-C1 will say so and the gate needs a layer label or an exemption — decide then, do not pre-empt it here.

- [ ] **Step 4: Commit**

```bash
bd dolt push
git add .beads/issues.jsonl
git commit -m "make each phase exit a thing that holds the frontier, not a paragraph"
```

---

### Task 8: Wire the checks in, and route the documents

**Files:**
- Modify: `.github/workflows/docs-hygiene.yml`
- Modify: `CONVENTIONS.md` (session close, step 3)
- Modify: `INDEX.md` (routing row for this plan)

**Interfaces:**
- Consumes: `scripts/queue-check.py` and `scripts/tests/test-queue-check.sh` from Tasks 1-4.

- [ ] **Step 1: Add both to CI**

In `.github/workflows/docs-hygiene.yml`, after the `docs hygiene check` step:

```yaml
      - name: work-queue check
        run: python3 scripts/queue-check.py
      - name: queue-check test suite
        run: bash scripts/tests/test-queue-check.sh
```

Separate steps, matching the reasoning already recorded in that file: a failure should name which instrument broke.

- [ ] **Step 2: Add it to the session-close procedure**

In `CONVENTIONS.md`, session close step 3, replace the single command with both:

```markdown
3. Run `python3 scripts/docs-check.py` and `python3 scripts/queue-check.py`. Neither may be piped - a pipe reports the exit code of the last stage.
```

The routing row for this plan is already in `INDEX.md` — it was added when the file was written, because a file outside the routing table does not exist by `CONVENTIONS.md` and `docs-check.py` fails on it immediately.

- [ ] **Step 3: Verify everything passes together**

```bash
python3 scripts/docs-check.py  > /tmp/dc.out 2>&1; echo "docs-check=$?"
python3 scripts/queue-check.py > /tmp/qc.out 2>&1; echo "queue-check=$?"
bash scripts/tests/test-queue-check.sh; echo "tests=$?"
```

Expected: `0`, `0`, `0`.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/docs-hygiene.yml CONVENTIONS.md
git commit -m "run the queue checks where they cannot be forgotten"
```

---

## Deliberately not in this plan

- WQ-01, one database reached through `BEADS_DIR`. It needs no action until a second repo exists; today there is one repo and the database is in it. The setting is recorded in the spec so the first code repo does not silently `bd init` its own.
- The prefix rename (WQ-02). Blocked by `bd` issue docs-3nj; it needs its own plan once the sync round-trip is proven.
- Formulas and molecules (WQ-07). Nothing to distil until Phase 1 has been done once by hand.
- `bd repo` evaluation (WQ-09). Also gated on docs-3nj.
- Backfilling `discovered-from` on existing issues (WQ-08). It applies to issues created from now on; retrofitting provenance from memory would invent it.
