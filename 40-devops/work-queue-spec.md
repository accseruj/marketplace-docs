---
doc: work-queue-spec
purpose: How the beads queue is structured once the project spans several layers and hundreds of issues - which axis carries what, how the phase graph keeps `bd ready` small, and the checks that hold it.
read_when: creating an issue, adding a label, changing the phase structure, or deciding whether a new work-tracking rule needs a check
status: draft
updated: 2026-08-04
related: [CONVENTIONS.md, 00-product/roadmap.md, 60-decisions/ADR-0008-work-tracking.md, 40-devops/drift-audit-spec.md]
---

# Work queue - design

Design approved 2026-08-04. Nothing below is built yet. ADR-0008 chose beads; this document says how it is used at scale.

## Why this exists

Measured on 2026-08-04, `bd` 1.0.5, 31 open issues:

- `bd ready` returns **21 of 31**. The queue does not narrow. Two thirds of the database is nominally startable.
- Priority no longer discriminates: **P0=7, P1=16, P2=7, P3=1**. Half the database sits in one bucket.
- **31 of 31** issues are type `task`, including issues whose whole content is a decision.
- **Zero** labels exist.
- All 31 id suffixes are 3 characters; beads lengthens suffixes as the database grows, so ids will not stay uniform.

The corpus will span infra, frontend, backend, catalog, feeds and sourcing (`10-architecture/c4-container.md` already names the repos) and is expected to reach hundreds of issues. At that size the failure above is not cosmetic: a `bd ready` that returns 200 items is the ordered list beads replaced, wearing a different shape.

**The constraint this design follows: readiness is computed from `blocks` and `parent_id` only. Labels, priority, type and every non-blocking link leave the ready frontier untouched.** Therefore the queue is narrowed by the phase graph, and labels exist only to slice a view.

## Decisions

### WQ-01 One database for the whole project
- One beads database serves all layers. Code repos reach it through `BEADS_DIR` rather than owning a database each.
- Rationale: cross-layer dependencies (feed adapter -> backend contract -> storefront) stay ordinary `bd dep` edges. Splitting per repo makes the one relationship the tool was chosen for the one relationship it cannot express directly.
- Rejected: `bd federation`, which multiplies a sync path that is not yet proven to round-trip (`bd` issue docs-3nj).

### WQ-02 The prefix names the project, not a layer
- The current prefix is `docs`, which is already wrong for an issue about returns policy and will be wrong for every infra issue.
- Rename to a neutral prefix once, as early as possible. A prefix is permanent per issue and cannot be changed per issue afterwards.
- **Blocked by `bd` issue docs-3nj.** The rename rewrites every id in one operation; doing that on a sync path not yet shown to reach a second clone risks a split database.
- Cost accepted at rename time: 38 references across 6 files are rewritable; 7 commit subjects in git history are not and will dangle permanently. That cost grows with every commit, which is why the rename is not deferred past docs-3nj.

### WQ-03 Kind of work is `issue_type`, never a label
- `bug`, `feature`, `epic`, `chore`, `decision`, `spike`, `milestone` are built in, filterable with `--type` / `--exclude-type`, and drive `bd lint` section requirements.
- Backfill: the 31 existing `task` issues are retyped. Issues whose content is a choice between options become `decision`.

### WQ-04 Layer is one flat label, carried by the epic
- Closed vocabulary, derived from `10-architecture/c4-container.md`, not invented here: `infrastructure`, `frontend`, `backend`, `catalog`, `feeds`, `sourcing`, `product`.
- `product` covers commercial, legal and market work - the majority of the current queue - which owns no container.
- The label is set on the epic. Children inherit labels at creation, so the layer is stated once per epic rather than once per issue.
- Consequence of inheritance: an epic carries **only** its layer label. Any other label on an epic propagates to every child, including ones it does not describe.
- **`dimension:value` syntax is forbidden for this axis.** That form belongs to `bd set-state` / `bd state`, which write an event bead on every change and model operational state. A layer does not change over time and must not carry that machinery.
- This is the only label axis. Upstream guidance is 5-10 technical labels; seven values spend that budget. A second axis requires retiring this one.

### WQ-05 Phases are epics; roadmap.md and the graph do not overlap
- One epic per roadmap phase. `bd dep add <phase N+1> <phase N> --type blocks` orders them.
- An issue that belongs to a phase is created with `--parent <phase epic>`, which also delivers WQ-04 inheritance.
- **Division of ownership, so there are two documents and one fact, not two copies:**
  - `00-product/roadmap.md` owns what a phase means, its deliverables, its exit gate in prose, and its course-change thresholds. It names no issues.
  - The phase epic owns which issues are in the phase and what blocks what. It carries no prose.
  - The only shared fact is the name and order of the phases. That is what WQ-C2 checks.
- This replaces the current unverifiable pointer in roadmap.md, Phase -1: *"All three are open beads issues"* names no ids, so a fourth issue would join silently.
- Issues outside every phase (repo hygiene, tooling) take no parent and stay permanently ready. That is correct, and it means the ready set floors above zero rather than reaching it.
- Such issues also carry no layer label, since WQ-04 attaches the label to an epic. That is the intended reading, not an omission: work that belongs to no container has no layer to name. WQ-C1 therefore scopes itself to issues that have a parent.

```mermaid
graph LR
  P-1[Phase -1 epic] --> G0{{gate: human}} --> P0[Phase 0 epic]
  P0 --> G1{{gate: human}} --> P1[Phase 1 epic]
  P1 --> G2{{gate: human}} --> P2[Phase 2 epic]
  P2 --> G3{{gate: human}} --> P3[Phase 3 epic]
  P0 -.children.-> C1[issue] & C2[issue]
```

### WQ-06 Exit gates are gate issues
- `bd gate create --type=human --blocks <next phase epic> --reason "<phase> exit gate"`, one per transition.
- A gate blocks like any blocker and is hidden from `bd list` by default, so an exit gate stops being prose and starts holding the frontier without adding queue noise.
- `--type=gh:pr` and timer gates exist and are evaluated by `bd gate check`. Not used yet: no CI condition currently gates a phase.

### WQ-07 Repeated work becomes a formula, after it has been done once
- Phase 2 and Phase 3 instantiate the same work graph per tenant and per supplier.
- Path: build it by hand in Phase 1, then `bd mol distill <epic-id> <formula-name>`, then `bd mol pour <formula> --var slug=<tenant>` per instance.
- Writing a formula before the first instance exists templates a guess. `.beads/formulas/` stays empty until then.

### WQ-08 Discovery keeps its provenance
- Issues found while doing other work are created with `--deps discovered-from:<id>`.
- This is a non-blocking link: it records where the finding came from without adding a blocker.

### WQ-09 Out of scope
- Multi-agent orchestration - swarms, personas, merge slots, agent routing. The beads charter places "agent routing, task assignment strategy, model choice, retry plans, scheduling" outside the tool; this project has one operator and gains nothing.
- Tracker integrations (jira, linear, notion, ado) - ADR-0008 removed the tracker they would bridge to.
- `metadata` JSON - an extension point for integrations, and this design needs no field that a label or a type does not already carry.
- `bd repo` multi-repo hydration - the one mechanism that could revisit WQ-01. Evaluate after docs-3nj, not before.

## Checks

A rule stated here without an instrument is an obligation verified at review, and this repo has measured what that produces (`40-devops/drift-audit-spec.md`). Each check below ships in the same commit as the rule it enforces, with the violation that makes it fail.

| id | Check | Injected violation that must make it exit non-zero |
|---|---|---|
| WQ-C1 | Every open non-gate issue that has a parent carries exactly one WQ-04 label | Add a second layer label to one issue; remove the label from one epic |
| WQ-C2 | Phase headings in `00-product/roadmap.md` and phase epics agree on count and name | Add a phase heading to roadmap.md with no matching epic; rename one epic |
| WQ-C3 | Every open issue carries the sections its type requires, each opening a line | Create an issue of type `task` with no Acceptance Criteria; and one whose description only mentions the phrase in prose |
| WQ-C4 | No issue id appears in a commit subject while still open — **warning, not error** | Reference an open issue id in a commit subject and leave it open; the run must warn and still exit 0 |

- All four read `.beads/issues.jsonl` and `git log`. Neither invokes `bd`.
- WQ-C4 warns rather than fails, decided 2026-08-05 on a case in this repo's own history. `d4704f2` names `docs-b83` in its subject because it *recorded* that issue, not because it did its work, and the work is still legitimately open. The check cannot separate the two intents, so as an error it would be permanently red — the failure mode `scripts/docs-check.py` already names, where a check that is always failing teaches the reader to skip it. Every other rule here is an error.
- Reason, corrected 2026-08-04 during planning: `.github/workflows/docs-hygiene.yml` installs Python only. A check that shells out to `bd` either breaks CI or is skipped when the binary is absent, and a skipped check is a green tick with nothing behind it. The export file is tracked in git (`export.auto`, `export.git-add` in `.beads/config.yaml`), so the queue's state is readable as a file wherever the repo is checked out.
- WQ-C3 restates what `bd lint` enforces rather than calling it. The duplication is deliberate and bounded: the section requirements per type are four lines.
- They live in `scripts/queue-check.py`, not in `scripts/docs-check.py`, which owns document hygiene and takes no argument about issues.
- The export lags the database. `bd update` writes Dolt; the checks read `.beads/issues.jsonl`, refreshed on a 60s `export.interval`. Measured 2026-08-05: a check run immediately after a batch of updates reported 13 errors that no longer existed. Any local run therefore does `bd export -o .beads/issues.jsonl` first; CI is unaffected, since it reads the committed file.
- WQ-C4 already works today with no new convention: `CONVENTIONS.md` session close requires the issue id in the commit subject.
- Registering these does not create an eighth drift-audit pair. WQ-C2 compares one line per phase, not two descriptions of the same phase; the prose lives in exactly one place by WQ-05.

## Evidence status

Verified locally against `bd` 1.0.5 (Homebrew) on 2026-08-04, by running the command:

- label inheritance from parent, and its opt-out - `bd create --help` (`--no-inherit-labels`)
- `dimension:value` is owned by state machinery - `bd set-state --help`, `bd state --help`
- `bd lint` section requirements per type - `bd lint --help`
- `bd orphans` reads commit subjects - `bd orphans --help`
- `--deps discovered-from:<id>` - `bd create --help`
- multi-repo hydration exists as `bd repo` - `bd repo --help`
- the five measurements under "Why this exists" - `bd list --json`
- no hardcoded issue-id length exists in `scripts/` or `.github/`, so growing id suffixes break nothing here

Verified by probe on 2026-08-04 - two throwaway issues created, inspected and deleted, database confirmed back at 33 records:

- a child created with `--parent` inherits the parent's labels, unasked. Confirmed on the export, not on the help text.
- a child's id is hierarchical: parent `docs-2ob` produced child `docs-2ob.1`.
- the parent link is exported explicitly as a dependency of `"type": "parent-child"`. WQ-C1 reads that, not the dot in the id.
- `labels` appears in the export only when an issue has labels; absent means none, not an omission.
- there is no `parent`/`parent_id` field in the export at all.

Claims about upstream documentation, cited rather than tested. All read 2026-08-04, all under `https://github.com/gastownhall/beads/blob/main/`:

- readiness is computed from `blocks` and `parent_id` only - docs/core-concepts/graph-links.md
- label budget of 5-10 technical labels, and the inheritance caveat - docs/core-concepts/labels.md
- id suffix length grows with database size - docs/core-concepts/adaptive-ids.md
- a prefix is permanent and prefix-based isolation is "too fragile" - engdocs/CONTRIBUTOR_NAMESPACE_ISOLATION.md
- orchestration is out of scope for beads - engdocs/PROJECT_CHARTER.md
- gate semantics and `--type=human` - docs/workflows/gates.md
- distill / pour / `--var` - docs/workflows/molecules.md
- phases as epics plus blocking dependencies - examples/multi-phase-development/README.md

## Open

- OPEN: the neutral prefix string for WQ-02. Blocked by docs-3nj.
- OPEN: whether `bd repo` hydration changes WQ-01. Evaluate after docs-3nj.
- OPEN: which phase owns an issue that spans two phases. Current rule is the earliest phase that cannot finish without it; untested against a real case.