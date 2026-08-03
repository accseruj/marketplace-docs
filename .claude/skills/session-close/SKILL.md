---
name: session-close
description: Use when a work session on the marketplace docs repo is ending - the user says "заканчиваем", "закрываем сессию", "хендофф", "handoff", "на этом всё", or steps away while decisions made in conversation are still only in the chat
---

# Session close

## Overview

Closing a session produces exactly two things: a docs repo where every decision from this session sits in the file that owns it, and a commit whose message explains what was decided and why.

There is no hand-off document. When the request is "приготовь хендофф", the deliverable is still these four steps. The next session reconstructs state from `INDEX.md` → `bd ready` → `60-decisions/` → `git log`; a separate summary file duplicates that and then contradicts it on the next edit.

Run every command from the docs repo root.

## Checklist

Create a todo for each item and complete them in order.

1. Record every decision
2. Update the work queue in beads
3. Run the hygiene check
4. Commit

## 1. Record every decision

Walk the session and place each decision:

| What was decided | Where it goes |
|---|---|
| An architectural choice, or one that constrains future design | A new ADR in `60-decisions/`, copied from `TEMPLATE.md` |
| A fact about the world as it is now | The single living doc that owns that fact — find it in the `INDEX.md` routing table |
| A new permanent rule | An `INV-nn` line in `INDEX.md`, pointing at the ADR that established it |
| Something a doc still carries as `TODO(...)` or `OPEN:` | Delete the marker and state the resolved fact in its place |

Bump `updated:` on every file touched. An accepted ADR gets `status: frozen` in frontmatter and `- Status: accepted` in the body, and is never edited afterwards.

A decision that exists only in the conversation is gone when the session ends. That is what this step prevents.

## 2. Update the work queue in beads

The queue is beads, not a markdown list (ADR-0008).

- `bd close <id>` everything finished this session.
- `bd create` everything the session discovered. A discovered task that stays in the chat is lost.
- `bd dep add <id> --blocked-by <id>` wherever new work is genuinely gated on other work. An unrecorded dependency shows up as ready work that cannot actually start.
- Run `bd ready` and read it. Every line must be startable by someone who was not in this session; if a title only makes sense with today's context, rewrite it.

- `bd dolt push`. **Required.** `.beads/` is gitignored except config, so `git push` carries no issues at all. Skipping this leaves the queue on one machine.

Use `bd update` with flags, never `bd edit` — it needs an interactive editor.

`scripts/session-brief.sh` prints `bd ready` into the next session's context, so that list is the hand-off.

## 3. Run the hygiene check

```bash
python3 scripts/docs-check.py
```

Must print `ok`. Fix whatever it reports before committing.

## 4. Commit

The message states what was decided and why it beat the alternative — not which files changed, which the diff already says. When the work belongs to a beads issue, put its id in parentheses at the end of the subject line. Push only if asked.

`bd prime` states a generic session-close protocol. Where it and `CONVENTIONS.md` disagree, `CONVENTIONS.md` wins — it adds the steps specific to a docs repo.

## Quick reference

| Need | Path |
|---|---|
| ADR template | `60-decisions/TEMPLATE.md` |
| Routing table, invariants, decision index | `INDEX.md` |
| Work queue | `bd ready`, `bd show <id>` (ADR-0008) |
| Phases and exit gates | `00-product/roadmap.md` |
| Hygiene check | `scripts/docs-check.py` |
| The convention this skill automates | `CONVENTIONS.md`, section "Session close" |

## Common mistakes

- Writing a summary file — `HANDOFF.md`, `SESSION-LOG.md`, a notes directory — instead of updating the docs. It duplicates state that already has an owner and goes stale immediately.
- Leaving a decision in chat because it seemed small. Small decisions are the ones nobody reconstructs later.
- Writing history into a living doc ("previously we used X"). Living docs describe the present; the ADR chain is the history.
- A diff-summary commit message. The message is the only place the reasoning survives in searchable form.
- Closing beads issues without creating the ones the session discovered. The queue then looks finished while the work is not.
- Recording a task in `roadmap.md` instead of beads. That file carries phases and exit gates only.
