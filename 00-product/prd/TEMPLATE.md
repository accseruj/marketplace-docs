---
doc: prd-template
purpose: Template for a feature/epic PRD. Copy to `PRD-<nnn>-<slug>.md`.
read_when: starting a new epic
status: living
updated: 2026-08-02
---

# PRD-<nnn>: <title>

- Status: draft | approved | shipped | dropped
- Owner: human
- Related: <ADRs, tech specs, VC stages>

## Problem
<What is broken or missing. Observable, not speculative.>

## Users and jobs
<Who, and what they are trying to do. One line each.>

## Scope
- In: <bullets>
- Out: <bullets — explicit, this section prevents scope creep>

## Acceptance criteria
- AC-01 <testable statement>
- AC-02 ...

## Automation impact
- Value-chain stages touched: <VC-xx>
- Target automation level after this epic: <L0-L3>
- Automation-readiness test answers (all six): <answers, or link to the tech spec>

## Non-functional requirements
- Performance: <CWV budgets for affected routes>
- Cost: <expected infra delta>
- Security: <auth, rate limiting, data exposure>

## Risks
| Risk | Impact | Mitigation |
|---|---|---|

## Open questions
- OPEN: ...
