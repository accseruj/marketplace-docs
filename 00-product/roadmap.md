---
doc: roadmap
purpose: Phases, exit gates, and the thresholds that would change course.
read_when: planning what to work on next
status: living
updated: 2026-08-02
related: [00-product/vision.md, 60-decisions/]
---

# Roadmap

Method: Shape Up style cycles (4-6 weeks), Kanban with WIP = 1. No sprints, no estimation theatre.

## Phase -1 - Foundations on paper (current)
Deliberately long. No production code.
- Close OPEN items in `00-product/vision.md`, especially supplier channels and returns policy.
- Decide ADR-0005 (catalog data layer) and ADR-0006 (product identity model). Both block everything downstream.
- Fill `10-architecture/domain-model.md`: entities, state machines, transition tables, events.
- Fill `10-architecture/api-contracts/`.
- Write the PRD for the flagship storefront and for supplier ingestion.
- Author Claude Code skills (see `40-devops/README.md`).
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
