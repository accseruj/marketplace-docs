---
doc: adr-0005
purpose: Where canonical product data, supplier offers and matching live.
read_when: BLOCKING - before any catalog, ingestion or ordering work
status: draft
updated: 2026-08-02
---

# ADR-0005: Catalog data layer - dedicated service or Magento-native

- Status: proposed - BLOCKING, needs decision in Phase -1
- Date: 2026-08-02
- Deciders: human
- Related: INV-06, ADR-0006, 10-architecture/c4-container.md

## Context
The system is greenfield with no external PIM (INV-06). Something must own supplier offers, canonical product content, matching, enrichment state, assortment rules and pricing rules. Magento can hold products, but it is a commerce engine, not a data-integration platform: it has no native concept of a supplier offer, and its EAV write path is slow at feed volumes.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Magento-native (custom modules + MSI sources per supplier) | One system to operate; no sync layer; MSI already models multi-source stock | EAV write throughput at feed scale; offer/matching model bent onto a foreign schema; couples catalog logic to Magento upgrades |
| Dedicated catalog service (own DB, projects into Magento) | Right schema for offers and matching; fast bulk writes; Magento stays a commerce engine; replaceable | Second system to build and operate solo; a projection/sync layer with its own failure modes |
| Off-the-shelf open-source PIM | Enrichment UI for free | Reintroduces a heavy external dependency the project just removed; still no offer/sourcing model |

## Decision
TODO(human): not yet decided.

## Decision inputs needed
- Expected SKU count per supplier and total.
- Feed frequency and delta vs full-snapshot.
- Whether several suppliers will offer the same item (if yes, matching is mandatory and pushes toward a dedicated service).
- How much manual enrichment the operator expects to do, and in what UI.

## Consequences
To be filled on decision. Note that this ADR and ADR-0006 are coupled - decide them together.

## Revisit triggers
- Feed volume exceeds what the chosen write path sustains.
- Magento upgrade friction caused by catalog customisation.
