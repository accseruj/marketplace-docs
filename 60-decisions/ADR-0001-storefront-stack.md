---
doc: adr-0001
purpose: Choice of storefront technology for 10-20 tenants on one Magento instance.
read_when: questioning the frontend stack
status: frozen
updated: 2026-08-02
---

# ADR-0001: Storefront stack - custom Next.js App Router over Magento GraphQL

- Status: accepted
- Date: 2026-08-02
- Deciders: human
- Related: INV-02, INV-05, INV-06, ADR-0002, ADR-0003

## Context
10-20 tenants on one Magento 2 Open Source instance. Shared component library, but different layouts and UX flows per tenant. Priorities: infra cost > CWV/SEO > maintenance effort > time-to-launch. Single operator. Existing team competence is React/Next.js/GraphQL. Luma fails Core Web Vitals in field data.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Luma optimised | No new runtime | Knockout/RequireJS/jQuery; fails 2 of 3 CWV |
| Hyva Theme | Free since 2025-11-10 (OSL/AFL 3.0); licences per installation not per site; single stack; strong CWV | Server-rendered PHP; limited for divergent UX flows; second-best CWV ceiling |
| PWA Studio / Venia | Free, official | Maintenance mode since 2024; Adobe steers new projects elsewhere |
| Vue Storefront / Alokai | Mature | SaaS-oriented, opaque pricing, lock-in - violates INV-05 |
| Front-Commerce | Mature | Proprietary, paid, reported support/contract risk - violates INV-05 |
| Adobe Edge Delivery Services | Free boilerplate, edge speed, native multistore | Depends on Adobe Catalog Service and document-authoring model; foreign to this stack |
| Custom Next.js App Router + GraphQL | Full control, no lock-in, matches team skill, best cost/CWV control | Two runtimes to operate (PHP + Node); more upfront build |

## Decision
Build a custom Next.js (App Router) headless storefront over Magento 2 GraphQL.

## Consequences
- Positive: no vendor lock-in; full control of rendering and caching; cheapest hosting path (ADR-0003); UX flows can diverge per tenant.
- Negative: two runtimes to operate solo; all commerce UI must be built rather than inherited; blast-radius risk (see ADR-0002).
- Follow-up: tenancy tech spec; design system; checkout scope decision.

## Revisit triggers
- Solo operation of two runtimes proves unsustainable in Phase 1.
- Tenants turn out to need only theme-level differences, not flow-level - then Hyva on native multistore becomes the better trade (runner-up).
