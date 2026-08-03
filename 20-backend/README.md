---
doc: backend-index
purpose: Magento 2 platform facts, constraints and known traps for the multi-website setup.
read_when: any Magento or integration work
status: draft
updated: 2026-08-04
related: [10-architecture/api-contracts/README.md]
---

# Backend (Magento 2 Open Source)

## Target stack
- Magento 2.4.8/2.4.9, PHP 8.3/8.4
- MySQL 8.4 or MariaDB 11.4
- OpenSearch 2.19+ (Elasticsearch support removed in 2.4.8)
- Valkey 8 / Redis 7.2
- Varnish 7.6/7.7
- RabbitMQ

## Dropshipping implications
- No owned stock (INV-05). Sellable quantity is a projection of supplier offers, never hand-authored.
- Magento MSI is the natural fit: one Source per supplier, Stock per website, with a source-selection algorithm. Evaluate custom MSI source-selection against the sourcing rules in `10-architecture/domain-model.md` before committing.
- Reservation strategy is the main oversell lever (INV-09). Decide cart vs checkout vs PO-acknowledgement reservation in Phase -1.
- Order splitting across suppliers must be modelled explicitly; Magento's native multi-shipment handling is not sufficient on its own.

## Multi-website rules
- One instance, 10-20 websites (ASM-01 - an assumption pending measurement, not an invariant). One website = one tenant.
- Separate root category per website; products shared across websites, categories not.
- Keep config-scope overrides shallow. Every unnecessary store-view-scoped setting multiplies config rows and debugging cost.
- Indexers in "Update by Schedule" (mview) only. Full reindex across 20 websites is not operationally viable.
- Varnish varies cache per domain/store; more store views means lower hit rate. Target hit rate >= 80%. Keep private content minimal.

## GraphQL
- Enable the resolver-results cache (improved in 2.4.8). Expect 30-70% response-time reduction on cacheable queries.
- Enforce query depth and complexity limits; paginate every list.
- Disable introspection in production.
- Known trap: FPC invalidation for GraphQL can serve stale data (Magento GitHub issue #40823). Test invalidation on every reindex path.
- Pre-auth custom resolvers need: nginx rate limiting, Cloudflare Turnstile, neutral response payloads (no user enumeration), artificial response delay.

## Sizing
- Starting point for 20 websites: 16 cores / 32-128 GB RAM / NVMe, dedicated.
- DB RAM >= half the database size.
- TODO(human): current SKU count, expected traffic per tenant - required to firm this up.

## Open items
- OPEN: shared vs per-website customer accounts.
- OPEN: pricing strategy per website (shared price with website-scope overrides?).
- OPEN: order increment ID scheme per website.
- OPEN: MSI vs a custom stock projection - depends on ADR-0005 and ADR-0006.
