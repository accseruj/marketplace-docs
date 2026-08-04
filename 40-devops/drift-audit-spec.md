---
doc: drift-audit-spec
purpose: Design for the recurring drift audit - what it compares, how it runs, how it is itself tested.
read_when: implementing or changing the drift audit; deciding whether a new hygiene rule needs a check
status: draft
updated: 2026-08-04
related: [CONVENTIONS.md, 40-devops/README.md, 00-product/assumptions.md]
---

# Drift audit - design

Status: design approved 2026-08-04, and built. DA-01 and DA-02 delivered in `49a624d`; DA-03 through DA-07 delivered on the same branch as this line - the agent, the skill, the report format, the staleness line and the fixture all exist and are covered by `scripts/tests/`. DA-08 is deferred and is the only item not built.

## Why this exists

**This section owns the count. Every other document links here rather than restating a figure; an unverified count restated in three places is itself the failure this project measured.**

Measured, not assumed. **Seven cases**, recorded 2026-08-02..04, in which a stated rule, or a property asserted about a tool, was contradicted by the repository state at the moment of writing. Method: each case was written down with the file and line of both sides when it was found; the number is the length of that record, not an estimate or a recollection. Six were found by a session that had not written them. The seventh was found by its author, and only because the test was mechanical - an injected violation read by exit code - rather than a rereading.

Second measurement over the same period: `CONVENTIONS.md` went from 8 sections to 11, one of them carrying eight new rules, while `scripts/docs-check.py` stayed at four checks - all from the original skeleton. Rules grew, instruments did not.

Both facts point at the same conclusion and it is the design constraint here: **a rule is an obligation verified at review; an instrument is a mechanism that fires while writing.** This document specifies instruments.

## What the audit is, and is not

- Is: detection of *drift* - two places that must agree and no longer do.
- Is not: a foundational review of premises. Premises do not change monthly; running that cadence produces noise. It belongs at a phase gate or on a market/vertical change.
- Is not: an issue creator. It writes a report; disposition into `bd` is a human decision. The two-step order is what kept the queue usable when the 2026-08-04 audit turned 33 findings into 6 issues rather than 33 tickets (ADR-0008 names a `bd ready` nobody starts from as the tracker's failure condition).

## The standard - pairs that must agree

The auditor receives this fixed list. It does not receive "find problems". A fixed list makes its output falsifiable, its misses diagnosable to a specific pair, and a new failure type an added row rather than a new rule.

| ID | Pair | What must agree | Origin case |
|---|---|---|---|
| PR-1 | Doc ↔ mechanism | A sentence describing what a script, config or workflow does, against what it does | `40-devops` hook description; JSONL export asserted but disabled |
| PR-2 | Doc ↔ doc | One fact stated in two files, now divergent | The seven duplications in AUD-12 |
| PR-3 | ID reference ↔ ID definition | Every ID citation resolves to a definition and means what it is cited for. The prefix list is owned by `.claude/agents/drift-auditor.md` and is not restated here | ADR-0001 and ADR-0003 citing INV-05 where INV-07 is meant |
| PR-4 | Decision status across surfaces | ADR frontmatter ↔ ADR body ↔ the decision index in `INDEX.md` | ADR-0003 and ADR-0005 carry two vocabularies across three places |
| PR-5 | Doc ↔ queue | Issues citing docs; closed issues whose stated close reason is in no file; findings marked dispositioned while the contradiction is live | New. The queue began citing the corpus and the corpus the queue |
| PR-6 | Rule ↔ instrument | Every rule section in `CONVENTIONS.md` either has a check or is registered as not mechanisable | The 8-rules-to-0-checks imbalance |
| PR-7 | Assumption ↔ falsifier scope | Does the named falsifier separate the hypothesis from the nearest live alternative that leads to a different decision | `docs-pjl` named as ASM-03's falsifier while unable to separate niche difficulty from content-model failure |

PR-8, contract doc ↔ implementation, is added when code repositories exist. Not before.

**The list must shrink, not grow.** PR-1..PR-6 are progressively mechanisable and move out of the agent into `scripts/docs-check.py` as they are. PR-7 is the only one that requires judgement and is the reason an agent exists at all. The healthy end state is an agent with two pairs and a checker with twelve checks, not the reverse.

## Delivered - checks in `scripts/docs-check.py`

- DA-01 Every `INV-nn` in the `INDEX.md` declaration list carries a derivation - error if absent - and a revisit trigger - warning if absent. Delivered `49a624d`. The revisit-trigger half self-exempted anything naming an ADR and therefore fired on nothing until that clause was dropped; it now warns on INV-02, INV-07, INV-10 and INV-11.
- DA-02 Every `ASM-nn` in `00-product/assumptions.md` carries a falsifier - error if absent, warning if incomplete (no threshold, or "none exists"). Delivered `49a624d`.

Both were verified by injecting a violation and reading the exit code. The first implementation of DA-01 silently caught nothing - a missing `re.M` - and only the injected violation revealed it. Record that method; reading the output would have passed.

Warning rather than error where the gap is owned: `TODO(human)` is this repo's established way to hold an open question, and a permanently red check teaches its reader to ignore it.

## Delivered - the audit mechanism

All five shipped on the branch that carries this line. Each item states what exists, not what was intended.

This section no longer relies on the `planned` link-check exemption in `scripts/docs-check.py`, and that is deliberate: the word `planned` in a heading disables the link check for everything under it, so a section named for work not yet done also stops anyone noticing when its references break. Renaming it surfaced one - a filename *pattern* read as a filename - now written as `audit-<YYYY-MM-DD>.md`, which the checker skips by the `<` rule rather than by a heading. The `###`-resets-the-exemption defect stays recorded against `bd` issue docs-8gf; sub-headings are simply no longer constrained here.

**DA-03 Agent definition.**
- Path: `.claude/agents/drift-auditor.md`, symlinked into the workspace-root `.claude/agents/`. Same mechanism as the `session-close` skill, so the definition is versioned rather than living only in an unversioned workspace root (`bd` issue docs-nqk).
- A subagent, not execution in the main thread. Justification is measured: a session that has been discussing the corpus recalls it instead of reading it, and recalls wrong exactly where it is wrong. A subagent starts cold. Cold reading produced six of the seven cases counted in "Why this exists"; the seventh came from a mechanical test, and nothing produced it by rereading.
- Input: the pair list above, the corpus, `git log`, and the `bd` graph.
- Read-only by rule, not by mechanism. Omitting `Write` and `Edit` from the tool list signals the intent; `Bash` is unscoped and can write, so nothing enforces it. The definition states this plainly rather than claiming a barrier it does not have. Building the `PreToolUse` deny-hook that would enforce it is separate work.

**DA-04 Skill and invocation.**
- Path: `.claude/skills/drift-audit/SKILL.md`, symlinked as above.
- Responsibility: spawn the agent, receive findings, write the report. The skill is the caller; the agent is the reader.

**DA-05 Staleness reminder.**
- `scripts/session-brief.sh` filters `audit-*.md` in the repo root to the dated form `audit-<YYYY-MM-DD>.md` (the glob expands in lexicographic order and ISO dates sort chronologically, so the last match is the newest), computes that file's age in days, and prints it when older than 30. Prints "never run" when no dated form exists. A filename matching `audit-*.md` but not the dated form - audit-draft.md, say - is named on stdout as unparseable rather than silently dropped or let stand in for the newest report.
- Visible, not enforcing. A scheduled run firing while the operator is not working produces a report nobody opens; a line in the session brief appears exactly when he is about to work.
- No escalation mechanism. The day count grows on its own and that is the escalation.

**DA-06 Report format.**
- Path: `audit-<YYYY-MM-DD>.md` in the repo root. Reuses the existing `NO_LINK_CHECK` exemption; does not introduce a second naming mechanism. Audit type is stated in frontmatter, not in the filename. `scripts/session-brief.sh` ages only this exact form and names anything else it finds, so a report the pattern cannot parse is visible rather than silently unaged.
- Per finding: pair id, `VERIFIED` or `JUDGEMENT`, `file:line`, a reproduction command, and the `CONVENTIONS.md` rejection-record criterion applied.
- Per finding, additionally: `same-commit` or `cross-commit` - both sides of the contradiction introduced together, or apart. This is the instrument for DA-08.
- **Coverage lines are mandatory.** The report states, per pair, that it was checked and what was found, including nothing. A pair silent for three months is either a clean corpus or a broken check, and without the coverage line those two states are indistinguishable. The 2026-08-04 audit omitted this and that is a defect in it.

**DA-07 Self-test fixture.**
- `scripts/drift-fixture.py` copies the corpus to a target directory, injects one defect per covered pair, and prints one `EXPECT` line per injection. Run on every change to the agent's instructions.
- The target is guarded before anything is deleted. `check_target()` refuses the corpus itself, any path containing or contained by it, `$HOME`, and the filesystem root - `..` from the docs root reaches the whole workspace and is the shape a typo produces. `clear_target()` then refuses to delete an existing target unless it is empty or carries the `.drift-fixture` sentinel a prior run wrote; a non-empty directory without the sentinel was not built by this script and is left alone.
- After the `EXPECT` lines, the script prints a NOISE manifest naming every class of false positive its own exclusions manufacture - files it does not copy (dot-directories, the answer key) and routing rows it repairs so the copy stays clean under `docs-check.py`. The manifest is what a reader needs to tell a fixture artefact from an agent regression; the instruction that would make them read it does not exist yet - `.claude/skills/drift-audit/SKILL.md` still says to compare against the `EXPECT` lines alone. Producing side built, reading side open: `bd` issue docs-b83.
- Covered by fixture: PR-1, PR-3, PR-4, PR-6. All four are mechanical and unambiguous.
- Not covered by fixture: PR-2, PR-5, PR-7. Stated as uncovered in the agent's instructions. Uncovered and labelled is not the same as a green tick.
- This is the most expensive item in the build, and it is the item without which the agent is the thing this document was written to prevent.

## Deferred - not built

**DA-08 Per-commit review agent.**
- Not built, and the only item in this document that is not. Decided 2026-08-04 on capacity grounds (AUD-05, `bd` issue docs-npe).
- Falsifier: a drift audit reporting a `same-commit` finding is evidence a diff-time reviewer would have caught it, and that this tier is needed. DA-06 carries the tag for exactly this purpose.
- At least three of the seven were same-commit and are named rather than counted: the ASM-03 falsifier stated two lines above the confound that voids it; ASM-01's falsifier with no threshold; the INV-05 citations in ADR-0001 and ADR-0003. The expected answer is therefore that this tier will be needed. It is deferred, not rejected.

## Acceptance criteria

- AC-01 `scripts/drift-fixture.py` runs, injects, and the agent reports every injected defect. Demonstrated, not asserted.
- AC-02 A run against the unmodified corpus produces a report with a coverage line for all seven pairs.
- AC-03 The agent creates no `bd` issue and modifies no file other than its own report.
- AC-04 `session-brief.sh` prints the staleness line, verified by backdating a report file.
- AC-05 `python3 scripts/docs-check.py` passes with the new files present.

## Open

- OPEN: whether PR-6 is mechanisable now. It requires a registry of which `CONVENTIONS.md` rules are deliberately not mechanisable; that registry does not exist and creating it is itself the useful half of the work.
- OPEN: cost per run is unmeasured. Measure on the first run before committing to a cadence; 30 days is a starting assumption, not a finding.
- Settled 2026-08-04: the six subagents named in `CLAUDE.md` and `40-devops/README.md` were current policy while none existed and none could be checked. Authoring `drift-auditor` made the claim checkable and false. The roster now has one owner and separates authored from planned. Whether the six planned agents are ever written is a separate decision and is not open here.
