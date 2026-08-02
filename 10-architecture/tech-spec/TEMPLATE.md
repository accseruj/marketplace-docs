---
doc: tech-spec-template
purpose: Template for an implementation spec. Copy to `TS-<nnn>-<slug>.md`.
read_when: before writing code for an epic
status: living
updated: 2026-08-02
---

# TS-<nnn>: <title>

- Status: draft | approved | implemented | superseded
- Implements: PRD-<nnn>
- Decisions relied on: ADR-<nnnn>

## Summary
<3 lines max. What is being built.>

## Design
<Diagrams (Mermaid), data flow, schema changes, new endpoints/events.>

## Contracts touched
<Links into `10-architecture/api-contracts/`. If a contract changes, say how consumers migrate.>

## State machines touched
<Transitions added/changed, events emitted.>

## Automation-readiness answers
1. Trigger vs decision:
2. Explicit state:
3. API parity:
4. Idempotent/replayable:
5. Observable:
6. Exception path:

## Performance and cost
- Route archetypes affected and their CWV budgets.
- Expected infra cost delta.
- Cache strategy: what is cached, at which layer, how it is invalidated.

## Security
- Auth, rate limiting, data exposure, abuse scenarios.

## Rollout
- Migration steps, canary plan, rollback plan, tenants affected.

## Test plan
- Unit / integration / E2E / visual regression scope.

## Open questions
- OPEN: ...
