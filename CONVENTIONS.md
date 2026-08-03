---
doc: conventions
purpose: Format rules for this repo. These rules exist to make ingestion by Claude cheap and unambiguous.
read_when: before creating or editing any doc
status: living
updated: 2026-08-04
---

# Conventions

## Language
All docs are in English. Rationale: fewer tokens, exact match with framework/vendor terminology, no translation drift in identifiers. Conversation with the human stays in Russian.

## Every file starts with frontmatter
```
---
doc: <slug>
purpose: <one line — what a reader gets from this file>
read_when: <the trigger that should make Claude open it>
status: draft | living | frozen | superseded
updated: YYYY-MM-DD
related: [paths]
---
```

## Writing style (machine-first)
- Facts as single-line bullets. One fact per line. No narrative paragraphs.
- Front-load conclusions. No build-up, no restating the question.
- Stable IDs for anything referenced elsewhere: `INV-02`, `ASM-01`, `ADR-0003`, `RB-new-tenant`, `EV-order-placed`.
- Numbers and versions explicit. "Node 22", not "recent Node".
- Cross-reference by path, never duplicate a fact. One fact lives in exactly one file.
- Mark unknowns explicitly: `TODO(owner): question` or `OPEN: <question>` — never silently omit.
- No screenshots. Diagrams as Mermaid in-file.

## Doc lifecycle
- `draft` — being written, not yet authoritative.
- `living` — authoritative, updated in place.
- `frozen` — historical record, never edited (all ADRs are frozen once Accepted).
- `superseded` — replaced; header must link the replacement.

## Preventing rot
Documentation decays by accumulation, not by error. Three mechanisms keep it from becoming a maze.

**1. Separate state from history.**
- *Living docs* (`00`-`50`, `70`) describe the world as it is now. They carry no history. They are edited in place and never grow an "old approach" section.
- *Decision docs* (`60-decisions/`) are the history. Frozen on acceptance, never edited. When a decision changes, write a new ADR and set the old one to `superseded by ADR-nnnn`. The chain of ADRs is how anyone reconstructs the reasoning.
- *Git* is the third layer: `git log -p <file>` answers "what did this say in March" without any doc keeping a changelog.
- Consequence: never write "previously we did X" in a living doc. Point to the ADR.

**2. Every file is reachable and dated.**
- A file not in the `INDEX.md` routing table does not exist. Orphans are either routed or archived.
- `updated:` is bumped on every substantive edit.
- If a `living` doc has not been touched in one full phase, it is reviewed at the phase gate: still true, needs edit, or archive.

**3. Retirement, not deletion.**
- A document whose subject no longer exists moves to `90-archive/` with a reason header. See `90-archive/README.md`.
- Nothing is deleted. Nothing keeps `-v2` copies.

## Every asserted claim names its falsifier
Added 2026-08-04, after the foundational audit found the same failure three times: the project asserted invariants with nothing that could test them, the Phase -1 exit gate specified a 19x3 matrix that existed nowhere, and `scripts/docs-check.py` claimed to enforce a routing rule it could not detect a violation of. The same session asserted a durability property of a tool it had installed twenty minutes earlier, and recorded software versions read from documentation rather than from the software.

One rule covers all of it:

- Stating a constraint, a capacity, a version or a property obliges you to name what would show it false, in the same edit.
- A constraint with no falsifier is not an invariant. It goes in `00-product/assumptions.md`.
- A check that enforces a rule must be shown to fail on a violation of that rule. An untested check is a false negative wearing a green tick.
- A fact copied from documentation is a claim about documentation. Cite the primary source or mark it unverified.

## Rejecting a finding is a decision, sometimes
Not every rejected review finding needs a record - that generates its own sprawl. The test is consequence, not severity: **record the rejection when the rejection itself constrains future design.** Rejecting "put personal data at order level" is a decision and belongs in the doc that owns the topic, or in an ADR. Rejecting "split the router into sub-routers" is a preference and needs nothing.

## Docs hygiene pass
Run at every phase gate, and whenever the routing table stops feeling obvious. Automate what can be automated in CI:
- frontmatter present and well-formed on every file
- every file appears in the `INDEX.md` routing table
- no broken cross-references
- no `living` doc older than one phase without review
- count and age of `TODO(human)`, `TODO(Claude)`, `OPEN:` markers - a marker older than two phases is a decision being avoided
- duplicated facts: the same statement in two files is a defect; keep one, link the other

## Definition of Done for any code change
1. Tests pass; visual regression pass on affected tenants.
2. Core Web Vitals thresholds hold on the affected route archetype.
3. Automation-readiness test in `00-product/automation-charter.md` answered for anything touching the value chain.
4. Affected docs updated in the same commit. A PR that changes behaviour and no docs is incomplete.
5. If an architectural choice was made, an ADR exists.

## Session close (matters because Claude has no memory between sessions)
There is no hand-off document. A hand-off that lives outside the docs goes stale the moment the docs change, and it duplicates state the routing table already owns. Everything a hand-off would say belongs in one of four places: an ADR, the living doc that owns the fact, the work queue, or the commit message.

Run these four steps before ending any session:
1. Every decision made in the session is recorded - as an ADR if it is architectural, otherwise as an edit to the living doc that owns the fact. Nothing stays only in the chat.
2. Update beads: close what was finished (`bd close`), create what the session discovered, set the dependency if a new item is blocked. `bd ready` afterwards must show work that is genuinely startable. Then `bd dolt push` - `git push` does not carry issues (ADR-0008).
3. Run `python3 scripts/docs-check.py`.
4. Commit. The message states what was decided and why, not which files changed. When the work belongs to a beads issue, put its id in parentheses at the end of the subject line - `bd doctor` uses that to find issues that were worked on but never closed.

Reconstruction, in order: `INDEX.md` for where things live, `bd ready` for what is next, `60-decisions/` for why, `git log` for when. `00-product/roadmap.md` carries phases and exit gates, never the queue.

## Commit/PR hygiene
- Commit messages state intent, not diff summary.
- In code repos, every PR links the PRD or ADR it implements, and the session notes go in the PR body rather than a separate file.
