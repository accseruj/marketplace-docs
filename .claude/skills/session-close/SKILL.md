---
name: session-close
description: Use when a work session on the marketplace docs repo is ending - the user says "заканчиваем", "закрываем сессию", "хендофф", "handoff", "на этом всё", or steps away while decisions made in conversation are still only in the chat
---

# Session close

## Overview

Closing a session produces exactly two things: a docs repo where every decision from this session sits in the file that owns it, and a commit whose message explains what was decided and why.

There is no hand-off document. When the request is "приготовь хендофф", the deliverable is still these four steps. The next session reconstructs state from `INDEX.md` → `00-product/roadmap.md` → `60-decisions/` → `git log`; a separate summary file duplicates that and then contradicts it on the next edit.

Run every command from the docs repo root.

## Checklist

Create a todo for each item and complete them in order.

1. Record every decision
2. Reorder the work queue
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

## 2. Reorder the work queue

`00-product/roadmap.md` carries open work only.

- Remove items finished this session. They are already in `60-decisions/` and `git log` — the queue is not a history.
- Reorder the rest so the next session's first action is item 1 of the phase marked `(current)`.
- `scripts/session-brief.sh` prints that item into the next session's context, so it has to be actionable read alone.

## 3. Run the hygiene check

```bash
python3 scripts/docs-check.py
```

Must print `ok`. Fix whatever it reports before committing.

## 4. Commit

The message states what was decided and why it beat the alternative — not which files changed, which the diff already says. Push only if asked.

## Quick reference

| Need | Path |
|---|---|
| ADR template | `60-decisions/TEMPLATE.md` |
| Routing table, invariants, decision index | `INDEX.md` |
| Work queue | `00-product/roadmap.md` |
| Hygiene check | `scripts/docs-check.py` |
| The convention this skill automates | `CONVENTIONS.md`, section "Session close" |

## Common mistakes

- Writing a summary file — `HANDOFF.md`, `SESSION-LOG.md`, a notes directory — instead of updating the docs. It duplicates state that already has an owner and goes stale immediately.
- Leaving a decision in chat because it seemed small. Small decisions are the ones nobody reconstructs later.
- Writing history into a living doc ("previously we used X"). Living docs describe the present; the ADR chain is the history.
- A diff-summary commit message. The message is the only place the reasoning survives in searchable form.
- Marking work done without reordering the queue, leaving the next session to re-derive priority.
