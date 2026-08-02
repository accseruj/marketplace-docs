---
doc: api-contracts
purpose: The contracts that let independent parts of the system change without breaking each other.
read_when: changing anything that crosses a component boundary
status: draft
updated: 2026-08-02
---

# API contracts

Rule: a contract change and its consumers change in the same PR, or the contract is versioned.

## Planned contents
- `supplier-feed.md` - the ONE internal feed contract that every supplier adapter must produce, regardless of channel (API/EDI/SFTP/email). Includes required fields, units, currency, lead time, validation rules, quarantine behaviour.
- `supplier-order.md` - the ONE internal purchase-order contract every adapter must consume, plus the acknowledgement and tracking events it must emit.
- `catalog-magento.md` - how canonical products, prices and derived stock are projected into Magento website scope.
- `graphql-schema.md` - custom Magento resolvers, deprecation policy, complexity/depth limits, cache tags, auth model.
- `events.md` - RabbitMQ topics, payload schemas, idempotency keys, retry/DLQ policy. IDs like `EV-order-placed`, `EV-offer-stale`.

## Why the two supplier contracts come first
Supplier heterogeneity is the main source of long-term complexity in a dropshipping model. If every supplier adapter maps onto one internal feed contract and one internal PO contract, onboarding supplier N+1 is configuration (SC-05). If it does not, supplier-specific logic leaks into the core and the system stops scaling with suppliers - which is the same failure as not scaling with storefronts.

## Contract checklist
Every contract document must state: producer, consumer(s), transport, schema, versioning policy, idempotency key, failure mode, retry policy, observability (metric + audit record).

TODO(Claude): create these five files once ADR-0005 and ADR-0006 are decided. Do not stub them empty - each requires real decisions.
