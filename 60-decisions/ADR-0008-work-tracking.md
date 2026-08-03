---
doc: adr-0008
purpose: Where open work is tracked, and what stops being a tracker.
read_when: recording work, planning a session, wondering where a task belongs
status: frozen
updated: 2026-08-03
---

# ADR-0008: Work tracking - beads, replacing GitHub Issues and Projects

- Status: accepted
- Date: 2026-08-03
- Deciders: human
- Related: ADR-0004, CONVENTIONS.md, 40-devops/README.md, 00-product/roadmap.md

## Context
Work was tracked in an ordered markdown list in the roadmap, with GitHub Issues and Projects named in `40-devops/README.md` as the intended tracker once code work began. Neither had been exercised.

Two problems forced the decision now rather than at Phase 0.

A markdown list cannot express dependencies. The Phase -1 queue read as nine sequential items; once the same work was expressed as a graph it turned out five items were startable in parallel and six were genuinely blocked. The list had been hiding available work behind an invented ordering.

The operator has no memory across sessions and neither does the agent. Reconstructing "what is next" from a hand-maintained ordered list requires a human to have curated it correctly at the end of the previous session - the exact step most likely to be skipped.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Ordered list in `00-product/roadmap.md` | Zero tooling; already in place | No dependencies, so priority is invented rather than derived; must be hand-curated at every session close; hides parallelisable work |
| GitHub Issues + Projects | Familiar; integrates with PRs | Web UI is the primary surface, so an agent reads it over the network rather than from the working tree; offline work is awkward; a solo operator carries board maintenance for collaboration features nobody uses |
| beads (`bd`) | Dependency graph, so ready work is derived not asserted; the queue lives in the repo and works offline; output designed for agent consumption; `bd ready` is a single command a session-start hook can run | A second data store in the repo; a tool the operator must learn; young project, so churn is likely; the issue database is **not** carried by `git push` - see the sync consequence below |

## Decision
beads is the work tracker. GitHub Issues and Projects are not used for tracking.

- The database lives in the `docs` repo under `.beads/`. It is the only repository that exists, and it is already the single source of truth.
- Issue prefix is `docs`; ids look like `docs-a3f2dd`.
- `bd init` ran with `--skip-agents`, and the pointer snippet from `bd onboard` went into `CLAUDE.md` instead. Not because the AGENTS.md file beads generates would duplicate anything - it is an eight-line pointer by design, and `bd prime` supplies the live workflow context - but because this repo already has exactly one agent-instructions file and a second one would fragment where an agent looks.

## Consequences
- `00-product/roadmap.md` carries phases and exit gates only. It is no longer a queue. Putting a task there is now a defect.
- `scripts/session-brief.sh` prints `bd ready` into every new session instead of a hand-picked roadmap item. What the next session sees is derived from the graph, not from whether someone remembered to reorder a list.
- Session close step 2 in `CONVENTIONS.md` becomes a beads update: close what is done, create what was discovered, record dependencies.
- Reconstruction order becomes `INDEX.md` -> `bd ready` -> `60-decisions/` -> `git log`.
- Positive: a task discovered mid-session has somewhere to go that is not the chat log. This was the failure mode the session-close procedure was written to prevent, and it now has a mechanism rather than a rule.
- **Sync is not git.** `.beads/.gitignore` excludes the Dolt database, so `git push` carries the beads config and hooks but not a single issue. Issues sync only via `bd dolt push` to the Dolt remote. A session that commits and pushes git without `bd dolt push` leaves the queue on one machine. This is why session close carries it as an explicit step.
- Negative: a second data store in the repo. `.beads/` is machine-written; it is not documentation and is excluded from the hygiene check.
- Negative: beads is young. If it is abandoned, the graph exports to JSONL and the loss is the tooling, not the data. This is why the JSONL export matters more than the CLI.
- Negative: the operator must learn one more tool. Mitigated by the surface actually used being small - `bd ready`, `bd create`, `bd dep add`, `bd close`, `bd show`.
- Follow-up: when code repos appear, decide whether each carries its own beads database or whether `docs` stays the single tracker. Not decided here.

## Revisit triggers
- beads stops being maintained, or a release breaks the JSONL export.
- Work spans several repos and a single database in `docs` stops matching where the work happens.
- The graph stops being read - if `bd ready` is not what starts a session, the tracker has failed regardless of its features.
