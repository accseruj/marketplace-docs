---
doc: glossary
purpose: Project-specific terms. Prevents ambiguity across sessions.
read_when: an unfamiliar term appears
status: living
updated: 2026-08-02
---

# Glossary

## Platform
- **Tenant** - one customer-facing storefront (own domain, assortment, layout, UX flow). Maps 1:1 to a Magento *website*.
- **Layout archetype** - a reusable page-structure family shared by several tenants. Archetype changes structure and flow; theme changes tokens only.
- **Layout map** - per-tenant config declaring which blocks render, in what order, on each route archetype.
- **Route override** - per-tenant replacement of a route implementation when the layout map is insufficient.

## Commerce
- **Supplier** - an external company holding stock and shipping to the end customer. Never transacts on the storefront (INV-04).
- **Supplier feed** - a batch or streamed dataset from one supplier: products, cost, stock, lead time.
- **Supplier offer** - one supplier's sellable proposition for one item: cost, availability, lead time, shipping origin.
- **Canonical product** - the product a customer sees. May be backed by one or several supplier offers. See ADR-0006.
- **Sourcing decision** - choosing which supplier offer fulfils a given order line.
- **Purchase order (PO)** - the operator's order placed with a supplier to fulfil customer order lines.
- **Split order** - a customer order whose lines are sourced from more than one supplier, producing multiple POs and shipments.
- **Oversell** - accepting an order that cannot be sourced. The primary correctness failure of this model (INV-09).
- **Freshness** - age of stock/price data relative to reality. A correctness property, not a performance one.

## Process
- **Value chain (VC)** - the supplier-to-delivery stages in `00-product/automation-charter.md`.
- **Automation level (L0-L3)** - see automation charter.
- **INV-xx** - project invariant, listed in `INDEX.md`.
- **ADR** - Architecture Decision Record, MADR format, frozen once accepted.
