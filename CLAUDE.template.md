---
doc: claude-code-repo-template
purpose: Drop this into each code repo as CLAUDE.md and fill the placeholders.
read_when: setting up a new repo
status: living
updated: 2026-08-02
---

# <REPO NAME>

## Source of truth
Architecture, contracts and decisions live in the `docs` repo at `<PATH_OR_SUBMODULE>`.
Read `docs/INDEX.md` before non-trivial work. Do not restate its content here.

## What this repo is
- Purpose: <one line>
- Runtime: <e.g. Node 22 / PHP 8.4>
- Owns: <the part of the domain model this repo owns>
- Does not own: <explicit non-responsibilities>

## Local environment
- Host: Windows + WSL (Ubuntu). All services run in Docker.
- Path: `~/work/<repo>`
- Start: `<command>`
- Tests: `<command>`
- Lint/format: `<command>`

## Rules
- Follow `docs/CONVENTIONS.md` Definition of Done.
- Any change to a cross-repo contract requires updating `docs/10-architecture/api-contracts/` in the same PR.
- Any architectural choice requires an ADR in `docs/60-decisions/` before implementation.
- Never introduce a manual-only state transition — see `docs/00-product/automation-charter.md`.

## Known traps
- <repo-specific gotchas; keep this list short and current>
