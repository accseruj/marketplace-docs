---
doc: adr-0005
purpose: Where canonical product data, supplier offers and matching live.
read_when: BLOCKING - before any catalog, ingestion or ordering work
status: draft
updated: 2026-08-03
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

## Constraints already fixed
- ADR-0006 is accepted: `CanonicalProduct` with many `SupplierOffer`s. Something must own both entities plus the matching and offer-selection stages before the first storefront goes live. Magento has no native concept of either.
- Launch shape: 1-2 suppliers on the first vertical, mixed channels (REST/JSON API and CSV/XML over SFTP). Feed volume is therefore small at launch and is not by itself an argument for a dedicated service.
- Magento `sku` is an opaque canonical id (ADR-0006 ID-01), so whichever component generates canonical ids is upstream of Magento by definition.

## Decision inputs needed
- Expected SKU count per supplier and total. Blocked on the first-vertical research.
- Feed frequency, and delta vs full-snapshot per channel.
- How much manual enrichment the operator expects to do, and in what UI.
- Whether the offer store must serve reads at storefront request time (freshness path, INV-09) or only feed a projection.

## Consequences
To be filled on decision. Note that this ADR and ADR-0006 are coupled - decide them together.

## Revisit triggers
- Feed volume exceeds what the chosen write path sustains.
- Magento upgrade friction caused by catalog customisation.
