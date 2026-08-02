---
doc: domain-model
purpose: Entities, their owning component, and their state machines.
read_when: designing anything that changes data or process state
status: draft
updated: 2026-08-02
related: [00-product/automation-charter.md, 60-decisions/ADR-0006-product-identity.md]
---

# Domain model

## Entities and owners

| Entity | Owner | Notes |
|---|---|---|
| Supplier | Catalog data layer | Channel type, terms, lead times, cutoffs, coverage |
| SupplierFeedBatch | Feed ingestion | One delivery of one feed; needs its own state machine |
| SupplierOffer | Catalog data layer | One supplier's proposition for one item: cost, stock, lead time, origin |
| CanonicalProduct | Catalog data layer | What the shopper sees. Relationship to offers is ADR-0006 |
| Assortment rule | Catalog data layer | Which canonical products appear on which tenant |
| PriceRule | Catalog data layer or Magento (ADR-0005) | Cost -> retail, per tenant, with floor-margin guardrail |
| Product (sellable) | Magento 2 | Projection of a canonical product into a website scope |
| Customer, Cart, Order | Magento 2 | |
| SourcingDecision | Order routing | Which offer fulfils which order line |
| PurchaseOrder | Order routing | Operator -> supplier. One order may produce several |
| Shipment / Tracking | Order routing | Per PO; merged for the customer view |
| ReturnRequest | TBD | TODO(human): policy first |

## State machines
Each must be explicit and persisted (automation-readiness test #2).

- SM-feed-batch: `received -> validated -> quarantined | accepted -> applied -> reconciled`
- SM-offer: `active -> stale -> unavailable -> withdrawn`; staleness is time-driven and alertable (INV-09)
- SM-canonical-product: `draft -> incomplete -> publishable -> published -> unpublished -> retired`
- SM-order: Magento native, extended: `placed -> sourced -> po_issued -> acknowledged -> shipped -> delivered -> closed`, with branches `sourcing_failed`, `po_rejected`, `partially_fulfilled`, `cancelled`
- SM-purchase-order: `draft -> submitted -> acknowledged -> shipped -> closed`, branches `rejected`, `backordered`, `cancelled`
- SM-tenant-onboarding: `configured -> staged -> smoke_passed -> live`

TODO(Claude): once ADR-0005 and ADR-0006 are decided, write full transition tables - allowed actors, guard conditions, and the event emitted on each transition. This is the highest-value remaining Phase -1 artefact.

## Critical model questions
- OPEN: does one CanonicalProduct hold many SupplierOffers (multi-sourcing, requires matching), or is each supplier item its own product (no matching, but duplicate listings)? This is ADR-0006 and it determines the shape of nearly everything else.
- OPEN: sourcing strategy - cheapest offer, fastest offer, or supplier priority? Does it re-evaluate at checkout, or at order placement?
- OPEN: how is sellable stock computed from offers - sum across suppliers, max, or best-offer only?
- OPEN: is stock reserved at cart, at checkout, or not at all until PO acknowledgement? This is the main oversell lever.

## Identity and idempotency
- Every cross-component entity needs a stable external key: supplier item id, canonical product id, Magento SKU, PO reference.
- Every message carries an idempotency key and a correlation id.
- OPEN: canonical key strategy across supplier -> catalog layer -> Magento -> supplier PO.
