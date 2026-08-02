---
doc: automation-charter
purpose: The north star. Target automation level per value-chain stage and the test every design must pass.
read_when: designing any process, writing any PRD or tech spec, reviewing any ADR
status: living
updated: 2026-08-02
related: [10-architecture/domain-model.md, 00-product/vision.md]
---

# Automation charter

## North star
Zero-touch flow: supplier feed -> canonical catalog -> published on the right storefronts -> customer order -> sourcing decision -> purchase order to supplier -> supplier ships -> tracking to customer -> after-sales. Human attention is an exception path, not a step.

## Automation levels
- L0 manual - a human performs the step in a UI.
- L1 assisted - a human triggers it; the system executes and validates.
- L2 automated - the system triggers and executes; a human handles exceptions only.
- L3 autonomous - the system triggers, executes, detects its own failures and self-heals or escalates with full context.

## Value chain and target levels

| ID | Stage | Now | Target | Notes |
|---|---|---|---|---|
| VC-01 | Supplier onboarding (contract, feed mapping) | L0 | L1 | Judgement step; mapping must be config, not code (SC-05) |
| VC-02 | Feed ingestion | L0 | L3 | Scheduled pull/push, schema validation, quarantine on drift |
| VC-03 | Normalisation and product matching | L0 | L2 | Map supplier items to canonical products; human only on unmatched |
| VC-04 | Enrichment and content quality gates | L0 | L2 | Completeness rules decide publishability |
| VC-05 | Assortment assignment to tenants | L0 | L2 | Rule-driven per website, not hand-picked |
| VC-06 | Pricing (cost -> retail, margin rules per tenant) | L0 | L3 | Guardrails: never below floor margin |
| VC-07 | Stock and price freshness sync | L0 | L3 | Event or short-interval batch; staleness is alertable (INV-09) |
| VC-08 | Publication and indexing | L0 | L3 | mview indexers, cache invalidation, no manual reindex |
| VC-09 | Storefront onboarding | L0 | L2 | Config-driven; see `50-runbooks/new-tenant.md` |
| VC-10 | Order capture and validation | L0 | L3 | Storefront checkout + Magento order |
| VC-11 | Sourcing decision and order splitting | L0 | L3 | Pick supplier offer per line; split into POs |
| VC-12 | Purchase order placement with supplier | L0 | L2 | Depends on supplier channel: API, EDI, CSV, or email |
| VC-13 | Supplier acknowledgement and exception handling | L0 | L2 | Rejections, partial fills, backorders |
| VC-14 | Shipment and tracking ingest | L0 | L3 | Per-PO tracking, merged into one customer view |
| VC-15 | Customer communication | L0 | L3 | Event-driven, split-shipment aware |
| VC-16 | Payment capture and supplier settlement | L0 | L2 | TODO(human): settlement model is an OPEN in vision.md |
| VC-17 | Returns and refunds | L0 | L2 | TODO(human): policy first; routing differs per supplier |
| VC-18 | Reconciliation (stock, orders, money) | L0 | L3 | Detects drift between system, supplier and payment provider |
| VC-19 | Monitoring and incident response | L0 | L2 | Alerts carry a runbook link |

All stages start at L0 because the system is greenfield (INV-06).

## Automation-readiness test
Every design touching the value chain must answer all six. A "no" is allowed only with an explicit, dated remediation note.

1. **Trigger, not decision.** Is the manual part a *trigger* (must be automatable now) or a *judgement* (may stay human longer)? Triggers must never be permanently manual.
2. **Explicit state.** Is every state transition persisted in a named state machine? No state in a spreadsheet, an inbox, or the operator's head.
3. **API parity.** Can everything a human does in a UI also be done by an API call or event? If not, the UI action is a future blocker. Enforces INV-03.
4. **Idempotent and replayable.** Can the step be safely re-run on the same input, and replayed from an event log after a failure?
5. **Observable.** Does the step emit an audit record and a metric that would make its failure visible without a human noticing?
6. **Exception path.** Is there a defined escalation for cases automation cannot handle, and does it carry enough context to act on?

## Supplier-channel rule
Suppliers will arrive with unequal integration maturity (API, EDI, SFTP+CSV, email). The system must treat the channel as an adapter behind one internal contract, so that upgrading a supplier from email to API changes an adapter and no core logic. A supplier whose channel forces a permanently manual trigger is a commercial risk to record in `00-product/vision.md`, not an architectural exception.

## Anti-patterns (hard no)
- A manual step that is the only writer of a state transition.
- Data that exists only in a UI export or a supplier's email attachment.
- A process whose correctness depends on doing steps in the right order by hand.
- Supplier-specific logic anywhere outside its adapter.
- "We will add the integration later" without the event/contract defined now.
