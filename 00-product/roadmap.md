---
doc: roadmap
purpose: Phases, exit gates, and the thresholds that would change course.
read_when: planning what to work on next
status: living
updated: 2026-08-03
related: [00-product/vision.md, 00-product/market-selection.md, 60-decisions/]
---

# Roadmap

Method: Shape Up style cycles (4-6 weeks), Kanban with WIP = 1. No sprints, no estimation theatre.

## Phase -1 - Foundations on paper (current)
Deliberately long. No production code.

The list below is the work queue in priority order - each item unblocks the ones after it. It carries only open work; what was already decided is in `60-decisions/` and in git. Read it after the routing table when planning a session.

1. **Verify the first market and vertical.** `00-product/market-selection.md` recommends the Netherlands and a segment of hand tools / workshop consumables. It names two things it could not settle from public sources: keyword-level organic competition in Dutch, and a real sample feed pulled from a named NL-warehoused distributor. Everything downstream is sized off these two.
2. **Decide ADR-0005 - catalog data layer.** Blocked on the SKU count, cadence and delta-vs-snapshot shape that item 1 produces.
3. **Reservation strategy** - cart, checkout, or PO acknowledgement. The main oversell lever. Carried as OPEN in `10-architecture/domain-model.md`.
4. **Returns policy.** A commercial decision that blocks the returns design in a model with no warehouse (VC-17).
5. **Domain model transition tables** - allowed actors, guard conditions, event per transition. Gated on ADR-0005.
6. **Fill `10-architecture/api-contracts/`** - the two supplier contracts first. The adapter contract must carry ADR-0007 labelling evidence as feed fields, not as paperwork.
7. **Backend sizing inputs** - SKU count per supplier, expected traffic per tenant (`20-backend/README.md`).
8. **PRD for the flagship storefront.**
9. **Author the Claude Code skills** listed in `40-devops/README.md`, plus a session-close skill that automates the procedure in `CONVENTIONS.md`.

- Exit gate: every VC stage has a named owner component, a defined contract, and an answered automation-readiness test.

## Phase 0 - Platform skeleton
- Monorepo, shared `packages/ui`, GraphQL client + codegen, tenant resolution, CI.
- One throwaway tenant rendering real catalog data.
- One supplier feed ingested end-to-end into a canonical product.
- Exit gate: measured LCP/INP/CLS on a real category and product page; measured cost per 1M requests.
- Threshold: if the OpenNext bundle exceeds the Worker size limit, or CPU cost per storefront exceeds budget, revisit ADR-0003 and consider the hybrid per-archetype model from ADR-0002.

## Phase 1 - Flagship storefront to production
- Full commerce flow: catalog, search, cart, checkout, account.
- Full order flow: sourcing decision, PO placement, tracking ingest, customer comms.
- SEO: sitemaps, robots, hreflang, canonical, JSON-LD rendered server-side.
- Exit gate: field CWV pass; a real order sourced, purchased, shipped and tracked without manual intervention.

## Phase 2 - Templatisation and second supplier
- Layout archetypes, tenant config schema, visual regression, canary pipeline.
- Second supplier onboarded through the adapter contract, not custom code.
- Exit gate: second storefront launched purely by configuration; second supplier live without core changes.

## Phase 3 - Rollout
- Remaining storefronts and suppliers in waves.
- Reconciliation and freshness monitoring at target levels.
- Exit gate: SC-01, SC-04, SC-07.
