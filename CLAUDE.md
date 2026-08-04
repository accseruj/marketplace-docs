---
doc: claude-docs-repo
purpose: Operating rules for Claude inside the docs repo.
read_when: session start in this repo
status: living
updated: 2026-08-04
---

# Operating rules — docs repo

## Start of every session
1. Read `INDEX.md`, then `CONVENTIONS.md`, then `00-product/automation-charter.md`.
2. Read only the routing-table files the current task needs. Do not read the whole repo.

## Elicitation first
Before any substantial piece of work - an ADR, a PRD, a tech spec, a phase kickoff, a research task - run a structured Q&A round instead of assuming. Ask a small number of high-leverage questions (one to three per round), present concrete options rather than open prompts, and only then produce the artefact. The human prefers this and it is the cheapest way to avoid building on a wrong premise. Record the answers in the relevant doc in the same session.

## Issue tracking
This project uses **bd (beads)** for all work tracking (ADR-0008). Not markdown lists, not GitHub Issues.
Run `bd prime` for workflow context, or install hooks (`bd hooks install`) for auto-injection.
- `bd ready` - find unblocked work
- `bd create "Title" --type task --priority 2` - create an issue
- `bd dep add <id> --blocked-by <id>` - record a dependency
- `bd close <id>` - complete work
- `bd dolt push` - **required**; `git push` does not carry issues

Use `bd update` with flags, never `bd edit` - it needs an interactive editor.
Where `bd prime` and this repo's `CONVENTIONS.md` disagree on session close, `CONVENTIONS.md` wins: it adds the docs-specific steps.

## Behaviour
- This repo is the single source of truth. If code and docs disagree, that is a bug — report it, do not silently pick one.
- Never invent a decision. If a decision is missing, say so and propose an ADR.
- Architectural choices are proposed by Claude, decided by the human, recorded as an ADR before implementation.
- Prefer editing an existing file over creating a new one. New files require a routing-table entry in `INDEX.md`.
- Preparatory phase is deliberately long. Do not push toward writing code; push toward closing OPEN items.

## Subagent policy
Delegate to a subagent only when the task reads a lot and returns little.
- Roster (authored vs. planned, kept in one place): `40-devops/README.md`.
- Do not use: role-shaped "developer" agents. Features are built in the main thread.

## Tool policy
Keep the installed toolset minimal — each MCP server costs context before the first call.
- Baseline: bash (WSL + Docker + n98-magerun2), GitHub.
- Situational: Playwright (visual checks), Cloudflare (deploy phase).
