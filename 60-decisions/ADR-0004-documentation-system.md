---
doc: adr-0004
purpose: How project knowledge is stored so it survives across sessions.
read_when: questioning the docs structure or where something should live
status: frozen
updated: 2026-08-02
---

# ADR-0004: Machine-first docs repo as single source of truth

- Status: accepted
- Date: 2026-08-02
- Deciders: human
- Related: CONVENTIONS.md, INDEX.md

## Context
The project spans years and multiple repos, built by one human working with an AI assistant that has no memory between sessions. The documentation's primary consumer is the assistant, not the human. An alternative proposal was several parallel projects (docs, FE, BE, DevOps) coordinated by a master project.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Separate projects per discipline + master | Mirrors the mental model of specialised teams | Fragmented context; constant manual sync; no single place to answer "why" |
| Docs inside each code repo | Close to the code | Cross-cutting decisions have no home; duplication and drift |
| One docs repo as source of truth, referenced by every code repo | Single place for "why"; cheap to load; no duplication | Requires discipline to keep code and docs in the same PR |

## Decision
One `docs` repo, machine-first format (frontmatter, fact-lines, stable IDs, routing table in `INDEX.md`), referenced from each code repo's `CLAUDE.md`. Decisions recorded as MADR ADRs, frozen once accepted. Written in English for token efficiency and terminology consistency; conversation with the human stays in Russian.

## Consequences
- Positive: one load path for context; "why" is always answerable; cross-repo contracts have a home.
- Negative / accepted: docs must be updated in the same PR as behaviour changes; English adds a small reading cost for the human.
- Follow-up: Claude Code `adr` skill; Definition of Done enforcement in PR template.

## Revisit triggers
- The docs repo grows past what can be routed efficiently by `INDEX.md`.
