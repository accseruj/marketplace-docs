---
doc: c4-context
purpose: System boundary and external actors. Level 1 of C4.
read_when: any question about what is inside vs outside the system
status: draft
updated: 2026-08-02
related: [10-architecture/c4-container.md]
---

# C4 L1 - System context

```mermaid
graph TD
  SHOPPER[Shopper] --> SF[Storefront platform]
  OPERATOR[Operator - single human] --> ADMIN[Admin surfaces]
  SUPPLIER[Suppliers] -->|feeds: API/EDI/SFTP/email| ING[Feed ingestion]
  SF --> CORE[Commerce core - Magento 2]
  ADMIN --> CORE
  ING --> CAT[Catalog data layer]
  CAT --> CORE
  CORE -->|purchase orders| SUPPLIER
  SUPPLIER -->|acknowledgement, tracking| CORE
  CORE --> PSP[Payment providers]
  SHOPPER --> PSP
```

## External actors
- Shopper - buys on one of the tenants.
- Operator - the single human; the goal is to remove him from the loop.
- Supplier - holds stock, receives purchase orders, ships to the shopper. Integration maturity varies per supplier; each gets an adapter behind one internal contract.
- Payment providers - OPEN: which PSPs, per market.
- Carriers - not integrated directly; tracking arrives from the supplier. TODO(human): confirm, or decide that carrier APIs are needed for delivery events.

## System boundary
Inside: storefront platform, Magento 2, catalog data layer, feed ingestion and supplier adapters, order routing/sourcing, event bus, supporting services.
Outside: supplier systems, payment providers, carriers, Cloudflare edge.

Explicitly not in this system: any pre-existing PIM or ERP (INV-06). Every capability those would have provided is built inside the boundary or explicitly deferred.
