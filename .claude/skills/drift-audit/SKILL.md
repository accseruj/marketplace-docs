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
