---
doc: drift-audit-plan
purpose: Task-by-task implementation plan for the drift audit specified in 40-devops/drift-audit-spec.md.
read_when: implementing the drift audit
status: draft
updated: 2026-08-04
related: [40-devops/drift-audit-spec.md, CONVENTIONS.md]
---

# Drift audit implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the recurring drift auditor specified in `40-devops/drift-audit-spec.md` — a cold subagent that compares seven named pairs, writes a report, and is itself proven to detect injected defects.

**Architecture:** A fixture harness injects known defects into a throwaway copy of the corpus; a subagent definition carries the pair list and the report contract; a skill invokes the agent and writes the report; the session brief prints a staleness line. The fixture is built **first** because it is the test for everything after it.

**Tech Stack:** Python 3.12 (matching `scripts/docs-check.py` and the CI workflow), POSIX shell, Claude Code agent and skill markdown.

## Global Constraints

- All docs are English. Conversation with the operator is Russian. (`CONVENTIONS.md`)
- Paths inside docs are relative to the docs repo root — `00-product/vision.md`, never the same path prefixed with the repo directory name.
- Machine-first writing: single-line facts, conclusions first, explicit numbers, stable IDs.
- Every new file under `docs/` needs a routing-table row in `INDEX.md`, except under `.claude/`, `.beads/`, `.github/`, `scripts/`.
- `python3 scripts/docs-check.py` must exit 0 before every commit.
- Commit messages state what was decided and why, not which files changed. Append the `bd` issue id in parentheses when the work belongs to one.
- Shell must work on both macOS (this machine) and WSL Ubuntu (the operator's documented environment, `40-devops/README.md`). `date` differs between them; every date arithmetic needs both branches.
- The agent must not be able to edit files. This is enforced by omitting `Write` and `Edit` from its tool list, not by instructing it not to.

---

### Task 1: Staleness line in the session brief (DA-05)

**Files:**
- Modify: `scripts/session-brief.sh` (append after the "Recent decisions" block)
- Test: `scripts/tests/test-session-brief.sh` (create)

**Interfaces:**
- Consumes: nothing.
- Produces: a stdout line matching `Drift audit: never run` or `Drift audit: last run YYYY-MM-DD (N days ago) - overdue`. Task 4 relies on the filename pattern `audit-<date>.md` in the repo root, where `<date>` is ISO.

- [ ] **Step 1: Write the failing test**

Create `scripts/tests/test-session-brief.sh`:

```bash
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
```

Make it executable: `chmod +x scripts/tests/test-session-brief.sh`

- [ ] **Step 2: Run the test to verify it fails**

Run: `bash scripts/tests/test-session-brief.sh; echo "exit=$?"`
Expected: `FAIL case 1`, `FAIL case 2` and `FAIL case 3` printed, `exit=1`.
Do not pipe this into `head` or `tail` — the exit code you need is the script's, and a pipe reports the last command's. This trap is recorded in `CONVENTIONS.md`.

- [ ] **Step 3: Write the minimal implementation**

Append to `scripts/session-brief.sh`, after the `git log --oneline -3` block and before the closing `echo` lines:

```bash
echo
latest_audit="$(ls -1 audit-*.md 2>/dev/null | sort | tail -1)"
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
  if [ -n "${audit_epoch:-}" ]; then
    age=$(( ( $(date +%s) - audit_epoch ) / 86400 ))
    if [ "$age" -gt 30 ]; then
      echo "== Drift audit: last run $audit_date ($age days ago) - overdue. Run the drift-audit skill =="
    fi
  fi
fi
```

The `date -j -f` branch is macOS; the `date -d` branch is GNU/WSL. Pinning `00:00:00` keeps the age calculation from drifting by a day with the current time.

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash scripts/tests/test-session-brief.sh; echo "exit=$?"`
Expected: `ok`, `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add scripts/session-brief.sh scripts/tests/test-session-brief.sh
git commit -m "make the drift audit's own staleness visible at session start

A monthly cadence enforced by a scheduler produces a report nobody opens,
because it fires while the operator is not working. A line in the session
brief appears when he is about to work, which is when he can act on it. The
day count grows on its own; no escalation mechanism is needed."
```

---

### Task 2: Fixture harness that injects known defects (DA-07)

**Files:**
- Create: `scripts/drift-fixture.py`
- Test: `scripts/tests/test-drift-fixture.sh` (create)

**Interfaces:**
- Consumes: nothing.
- Produces: `python3 scripts/drift-fixture.py <target_dir>` copies the corpus to `<target_dir>`, injects four defects, and prints one `EXPECT <PAIR-ID> <file> <one-line description>` per injection to stdout. Task 3 and Task 5 consume this output.

- [ ] **Step 1: Write the failing test**

Create `scripts/tests/test-drift-fixture.sh`:

```bash
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
```

Make it executable: `chmod +x scripts/tests/test-drift-fixture.sh`

- [ ] **Step 2: Run the test to verify it fails**

Run: `bash scripts/tests/test-drift-fixture.sh; echo "exit=$?"`
Expected: a Python error that `scripts/drift-fixture.py` does not exist, `exit=1`.

- [ ] **Step 3: Write the minimal implementation**

Create `scripts/drift-fixture.py`:

```python
#!/usr/bin/env python3
"""Build a throwaway copy of the corpus with known drift injected.

Usage: python3 scripts/drift-fixture.py <target_dir>

Prints one EXPECT line per injected defect. The drift auditor is run against
the copy and must report every EXPECT line. A pair with no injection here is
uncovered, and the agent's instructions say so rather than implying coverage.
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


# Never copied into a fixture, and why. The reason is data: an entry without
# one cannot be added.
#   dot-prefixed names - tooling, not corpus. `.superpowers/` holds the SDD
#                        briefs, which name every injection in plain text.
#   __pycache__        - build artefact.
#   ANSWER_KEY         - the two drift-audit documents quote this file's source
#                        verbatim, so copying them hands the agent under test
#                        its own answers. Excluding them costs nothing: a
#                        fixture run grades the agent, it does not audit the
#                        corpus.
ANSWER_KEY = {
    "40-devops/drift-audit-plan.md",
    "40-devops/drift-audit-spec.md",
    "scripts/drift-fixture.py",
    "scripts/tests/test-drift-fixture.sh",
}


def _ignore(directory, names):
    root = ROOT.resolve()
    here = pathlib.Path(directory).resolve()
    ignored = set()
    for name in names:
        if name.startswith(".") or name == "__pycache__":
            ignored.add(name)
            continue
        rel_path = (here / name).relative_to(root).as_posix()
        if rel_path in ANSWER_KEY:
            ignored.add(name)
        if re.fullmatch(r"audit-\d{4}-\d{2}-\d{2}\.md", name) and here == root:
            ignored.add(name)
    return ignored


def inject(path, old, new, pair, description):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        sys.exit(f"fixture is stale: anchor not found in {path.name}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"EXPECT {pair} {path.name} {description}")


# Strings that only exist in the corpus because this fixture put them there.
# If one is readable anywhere except the file it was injected into, the copy
# hands the agent under test an answer it did not have to find.
# PR-4 has no entry: its injected value is `status: draft`, which legitimately
# occurs throughout the corpus. That pair is not covered by this check, and
# saying so is the point - an uncovered case named is not the same as a
# covered one.
LEAK_NEEDLES = {
    "prints the current phase's item 1": "40-devops/README.md",
    "INV-99": "60-decisions/ADR-0001-storefront-stack.md",
    "Every table must be alphabetised": "CONVENTIONS.md",
}


def assert_no_leak(target):
    problems = []
    for needle, injected_into in LEAK_NEEDLES.items():
        for path in sorted(target.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(target).as_posix()
            if rel == injected_into:
                continue
            try:
                if needle in path.read_text(encoding="utf-8"):
                    problems.append(f"{needle!r} is readable in {rel}")
            except (UnicodeDecodeError, OSError):
                continue
    if problems:
        sys.exit("fixture leaks its own answers:\n  " + "\n  ".join(problems))


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: drift-fixture.py <target_dir>")
    target = pathlib.Path(sys.argv[1])
    root = ROOT.resolve()
    resolved = target.resolve()
    if resolved == root or root in resolved.parents:
        sys.exit(f"refusing to build a fixture inside the corpus: {resolved}")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROOT, target, ignore=_ignore)

    # PR-1 doc vs mechanism: describe session-brief.sh doing what it no longer does
    inject(
        target / "40-devops" / "README.md",
        "which prints `bd ready` and the last three commits",
        "which prints the current phase's item 1 from `00-product/roadmap.md`",
        "PR-1",
        "describes session-brief.sh printing a roadmap item; it prints bd ready",
    )

    # PR-3 ID reference vs definition: cite an invariant that does not exist
    inject(
        target / "60-decisions" / "ADR-0001-storefront-stack.md",
        "- Related: INV-02,",
        "- Related: INV-99, INV-02,",
        "PR-3",
        "cites INV-99, which is defined nowhere",
    )

    # PR-4 status across surfaces: frontmatter contradicts body and INDEX
    inject(
        target / "60-decisions" / "ADR-0001-storefront-stack.md",
        "status: frozen",
        "status: draft",
        "PR-4",
        "frontmatter says draft; body says accepted and INDEX says Accepted",
    )

    # PR-6 rule without instrument: a new rule no check enforces
    inject(
        target / "CONVENTIONS.md",
        "## Docs hygiene pass",
        "## Table ordering\nEvery table must be alphabetised by its first column.\n\n"
        "## Docs hygiene pass",
        "PR-6",
        "adds a rule with no check in docs-check.py and no not-mechanisable note",
    )

    assert_no_leak(target)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash scripts/tests/test-drift-fixture.sh; echo "exit=$?"`
Expected: four `EXPECT` lines, then `ok`, `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add scripts/drift-fixture.py scripts/tests/test-drift-fixture.sh
git commit -m "build the drift auditor's test before the drift auditor

An untested check is a false negative wearing a green tick, and that applies
to a reviewing agent exactly as it applies to a script. The fixture injects
one defect per mechanically-checkable pair, so a run that reports nothing is
distinguishable from a run that cannot see anything.

Three pairs get no injection - doc-to-doc duplication, doc-to-queue, and
falsifier scope. They are judgement-shaped and are declared uncovered in the
agent's instructions rather than implied to be covered."
```

---

### Task 3: Agent definition and report contract (DA-03, DA-06)

**Files:**
- Create: `.claude/agents/drift-auditor.md`
- Create: workspace-root symlink for the agent

**Interfaces:**
- Consumes: `scripts/drift-fixture.py` output format from Task 2.
- Produces: an agent named `drift-auditor`. Task 4 dispatches it and expects findings as markdown with one `## PR-n` section per pair, each containing either findings or the literal line `No finding.`

- [ ] **Step 1: Write the agent definition**

Create `.claude/agents/drift-auditor.md`:

```markdown
---
name: drift-auditor
description: Compares the seven pairs in 40-devops/drift-audit-spec.md and reports where the two sides disagree. Read-only. Invoked by the drift-audit skill, not directly.
tools: Read, Grep, Glob, Bash
model: opus
---

You audit one repository for drift. Drift is two places that must agree and no longer do.

You are given a fixed list of pairs. You are not asked to find problems in general. Check exactly these pairs and report per pair, including when you find nothing.

Read the corpus. Do not rely on anything you think you already know about it — you were started cold on purpose, because a session that has been discussing this repository recalls it instead of reading it, and recalls it wrong exactly where it has changed.

## The pairs

- PR-1 Doc vs mechanism. Any sentence describing what a script, config or workflow does, against what it actually does. Read `scripts/`, `.github/workflows/`, `.beads/config.yaml`, and the workspace-root `.claude/settings.json` if reachable.
- PR-2 Doc vs doc. One fact stated in two files, now divergent. `CONVENTIONS.md` forbids duplication, so any fact in two places is a finding even when the copies still agree.
- PR-3 ID reference vs definition. Every `INV`, `ADR`, `ASM`, `VC`, `SC`, `HF`, `REG`, `MC`, `SM`, `RB` citation must resolve to a definition, and must mean what it is cited for. A citation that resolves but supports a different claim is the more dangerous case.
- PR-4 Decision status across surfaces. ADR frontmatter `status:` vs the body `- Status:` vs the decision index in `INDEX.md`.
- PR-5 Doc vs queue. Run `bd list --all` and `bd show <id>`. Look for issues citing docs that no longer say what is cited, closed issues whose stated close reason is recorded in no file, and findings marked dispositioned while the contradiction is still live.
- PR-6 Rule vs instrument. Every rule-bearing section of `CONVENTIONS.md` either has a check in `scripts/docs-check.py` or is registered as deliberately not mechanisable. A rule with neither is a finding.
- PR-7 Assumption vs falsifier scope. For each `ASM-nn` in `00-product/assumptions.md`, does the named falsifier separate the hypothesis from the nearest live alternative that would lead to a *different decision*? Not from every rival — an auxiliary hypothesis always remains untested, and demanding that would forbid measuring anything. A falsifier with no threshold is not a falsifier.

## Fixture coverage

PR-1, PR-3, PR-4 and PR-6 are covered by `scripts/drift-fixture.py`. PR-2, PR-5 and PR-7 are **not** covered by any fixture: nobody has demonstrated that you can detect them. Treat your own silence on those three as uninformative and say so in the report.

## Prohibitions

You have no write tools. Do not attempt to create or modify any file, and do not create, close or modify any `bd` issue. Disposition is a human decision made after reading your report.

## Report

Return markdown. One `## PR-n` section per pair, in order, all seven present.

Each section contains either findings or the single line `No finding.`

Each finding carries:

- **Claim** — one sentence stating the disagreement.
- **Evidence** — `file:line` for both sides.
- **Verdict** — `VERIFIED` if you read both sides, `JUDGEMENT` if it is an argument.
- **Reproduce** — a shell command that re-derives it. If a claim has no such command, say so; that marks it as the class this project treats as unreliable.
- **Introduced** — `same-commit` if `git log -S` shows both sides landing in one commit, `cross-commit` otherwise. Run the command; do not guess.
- **Rejection** — `records-a-decision` if rejecting this finding would constrain future design, `preference` otherwise. Per `CONVENTIONS.md`, only the first kind needs a written rejection.

State counts only with the command that produced them. An unverified count is the failure mode this repository has measured eight times.
```

- [ ] **Step 2: Link the definition into the workspace root**

The agent is only dispatchable from where Claude Code is launched, which is the directory above this repo. That root is not a git repository (`bd` issue docs-nqk), so the definition lives here and is linked out - the mechanism already used for `session-close`.

```bash
mkdir -p ../.claude/agents
ln -sfn ../../docs/.claude/agents/drift-auditor.md ../.claude/agents/drift-auditor.md
ls -l ../.claude/agents/
```

Expected: the link resolves. Task 4 dispatches this agent and cannot do so until this step has run.

- [ ] **Step 3: Verify the agent is registered**

Run: `ls -l .claude/agents/drift-auditor.md && ls -l ../.claude/agents/drift-auditor.md`
Expected: both exist and the link resolves. Agent definitions are picked up from `.claude/agents/`; confirm it appears in the available agent types on the next session start, and note if it does not.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/drift-auditor.md
git commit -m "define the drift auditor as a cold reader with a fixed pair list

It receives seven pairs that must agree, not a request to find problems. A
fixed list makes the output falsifiable, a miss attributable to a named pair,
and a new failure type an added row rather than a new rule.

Its read-only prohibition is enforced by the tool list, not by an instruction
telling it not to write. A rule is checked at review; a mechanism fires while
acting, and that distinction is the whole reason this agent exists."
```

---

### Task 4: Skill that runs the audit and writes the report (DA-04)

**Files:**
- Create: `.claude/skills/drift-audit/SKILL.md`

**Interfaces:**
- Consumes: the `drift-auditor` agent from Task 3; the filename pattern from Task 1.
- Produces: a skill named `drift-audit` that writes `audit-<date>.md` in the repo root.

- [ ] **Step 1: Write the skill**

Create `.claude/skills/drift-audit/SKILL.md`:

```markdown
---
name: drift-audit
description: Use when the session brief reports the drift audit is overdue, when the operator asks for a drift audit or "аудит дрейфа", or at a phase gate before the exit-gate review
---

# Drift audit

Detects drift — two places that must agree and no longer do. Specified in `40-devops/drift-audit-spec.md`.

Not a review of premises. Premises do not change monthly; that review belongs at a phase gate.

## Procedure

1. Confirm the working tree is clean and in sync. A report written over uncommitted work describes a state nobody else has.

   ```bash
   git status --short && git rev-list --left-right --count origin/main...HEAD
   ```

2. Dispatch the `drift-auditor` subagent. Give it only this: the repo path and the instruction to audit all seven pairs. Do **not** summarise the corpus for it, do not tell it what you expect it to find, and do not pass your own reading of recent changes. It starts cold on purpose; a framing from you is the thing that makes a reviewer agree with its author.

3. Write its output to `audit-<today>.md` in the repo root, with frontmatter:

   ```
   ---
   doc: audit-<today>
   purpose: Drift audit. Pairs compared, findings, and what was checked and found clean.
   read_when: dispositioning the findings of this run
   status: draft
   updated: <today>
   ---
   ```

   All seven `## PR-n` sections must be present, including those reporting `No finding.` A pair silent for three runs is either a clean corpus or a broken check, and without the coverage line those two states are indistinguishable.

4. Run `python3 scripts/docs-check.py > /tmp/dc.out 2>&1; echo $?`. Must be 0. Do not pipe it — the exit code you need is the checker's.

5. Commit the report. Do not create `bd` issues. Disposition is the operator's decision in a later session, and the two-step order is what keeps `bd ready` startable.

## When findings arrive

- A `same-commit` finding is evidence that a diff-time reviewer would have caught it, which is the falsifier for deferring that tier (`40-devops/drift-audit-spec.md`, DA-08). Report it as such.
- A pair reporting `No finding.` for three consecutive runs, where the fixture does not cover that pair, is a candidate for removal or for a fixture.

## Verifying the auditor still works

Before trusting a clean report, run the fixture and confirm the agent still detects every injected defect:

```bash
python3 scripts/drift-fixture.py /tmp/drift-fixture
```

Then dispatch the agent against `/tmp/drift-fixture` and compare its findings to the `EXPECT` lines. Required after any edit to the agent's instructions.
```

- [ ] **Step 2: Verify end to end against the fixture** — *executed by the controller, not by an implementer subagent.* A subagent cannot dispatch another subagent; and the agent must be run by someone who did not write its instructions, or the acceptance test is self-review.

Run:

```bash
python3 scripts/drift-fixture.py /tmp/drift-fixture
```

Dispatch `drift-auditor` against `/tmp/drift-fixture`. Compare its findings against the four `EXPECT` lines.
Expected: PR-1, PR-3, PR-4 and PR-6 each report the injected defect. Every one of the seven sections is present.
If a defect is missed, the agent's instructions for that pair are wrong — fix them and re-run. Do not proceed on a partial pass.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/drift-audit/SKILL.md
git commit -m "add the drift-audit skill; verify the auditor against injected defects

The skill passes the agent no framing - not a summary of the corpus, not what
it expects to be found. Seven of eight measured rule violations were caught by
a reader who had not written the thing; a reviewer briefed by its author is
closer to self-review than it looks."
```

---

### Task 5: Wire it in and remove the drift this task creates

**Files:**
- Create: workspace-root symlink for the skill
- Modify: `40-devops/README.md` (the Claude Code setup section)
- Modify: `40-devops/drift-audit-spec.md` (path style)

**Interfaces:**
- Consumes: everything from Tasks 1–4.
- Produces: nothing later depends on this.

- [ ] **Step 1: Link the skill into the workspace root**

The agent link was created in Task 3. The skill needs the same treatment.

```bash
mkdir -p ../.claude/skills
ln -sfn ../../docs/.claude/skills/drift-audit ../.claude/skills/drift-audit
ls -l ../.claude/skills/
```

Expected: the link resolves.

- [ ] **Step 2: Fix the path style in the spec**

`40-devops/drift-audit-spec.md` writes both `.claude` paths with a leading `docs/` prefix. Every other path in the corpus is relative to the docs repo root. Strip that prefix from both, leaving `.claude/agents/drift-auditor.md` and `.claude/skills/drift-audit/SKILL.md`.

This is a PR-3-class defect in a document written three commits ago, which is the argument for the audit in one line.

- [ ] **Step 3: Correct the subagent list**

`40-devops/README.md` and `CLAUDE.md` both state six subagents as current policy — `researcher`, `code-reviewer`, `security-auditor`, `test-runner`, `visual-regression`, `magento-log-triage` — and none exists (AUD-25). This task creates the first real one, so the claim becomes checkable and therefore false.

In `40-devops/README.md`, replace the subagent line with:

```markdown
Subagents (context isolation, not roles). Authored: `drift-auditor` - the recurring drift audit, see `40-devops/drift-audit-spec.md`. Planned, none yet written: `researcher`, `code-reviewer`, `security-auditor`, `test-runner`, `visual-regression`, `magento-log-triage`.
```

In `CLAUDE.md`, change the subagent bullet from a "Use:" list to the same authored/planned split. Do not restate the descriptions — `CONVENTIONS.md` forbids the duplication and the two files already carry seven of them.

- [ ] **Step 4: Run every test and the hygiene check**

```bash
bash scripts/tests/test-session-brief.sh; echo "brief=$?"
bash scripts/tests/test-drift-fixture.sh; echo "fixture=$?"
python3 scripts/docs-check.py > /tmp/dc.out 2>&1; echo "docs=$?"
```

Expected: `brief=0`, `fixture=0`, `docs=0`.

- [ ] **Step 5: Commit**

```bash
git add ../.claude 2>/dev/null; git add 40-devops/README.md 40-devops/drift-audit-spec.md CLAUDE.md
git commit -m "wire the drift auditor in, and correct what wiring it falsified

Naming six subagents as current policy was harmless while none existed and
none could be checked. Authoring the first one makes the claim checkable, and
it is false: they are planned, not present. Split the list accordingly.

The spec written three commits ago used docs-relative paths where the corpus
uses repo-root-relative ones - a PR-3 defect in the document specifying the
check for PR-3 defects."
```

---

## Self-review

**Spec coverage.** DA-01 and DA-02 delivered before this plan (`49a624d`). DA-03 → Task 3. DA-04 → Task 4. DA-05 → Task 1. DA-06 → Task 3, report contract, verified in Task 4 Step 2. DA-07 → Task 2. DA-08 is a deferral, nothing to build; its instrument is the `Introduced` field in Task 3's report contract. AC-01 → Task 4 Step 2. AC-02 → Task 3 report contract. AC-03 → Task 3 tool list. AC-04 → Task 1. AC-05 → Task 5 Step 5.

**Not covered by this plan, deliberately.** The spec's three `OPEN` items: whether PR-6 is mechanisable now, the unmeasured cost per run, and the not-mechanisable rule registry. PR-6 is checked by the agent here as judgement; mechanising it needs the registry, and building that registry is separate work worth its own decision.

**Type consistency.** `EXPECT <PAIR-ID> <file> <description>` is produced in Task 2 and consumed in Task 4 Step 2. Pair ids are `PR-1`..`PR-7` throughout, matching the spec. The report section heading is `## PR-n` in both Task 3 and Task 4. The filename pattern `audit-<date>.md` is written in Task 4 and parsed in Task 1.

**Known weakness.** Task 4 Step 2 is the only step whose pass condition depends on a model's output rather than an exit code. It is the acceptance test for the whole build, and it is the least deterministic step in it. Re-run it after any edit to the agent's instructions; treat a single pass as weaker evidence than the exit codes elsewhere.
