---
doc: adr-0006
purpose: Whether several supplier offers collapse into one shopper-visible product.
read_when: BLOCKING - before any catalog, pricing, sourcing or ordering work
status: draft
updated: 2026-08-02
---

# ADR-0006: Product identity model - canonical product vs supplier offer

- Status: proposed - BLOCKING, needs decision in Phase -1
- Date: 2026-08-02
- Deciders: human
- Related: ADR-0005, 10-architecture/domain-model.md, INV-09

## Context
Each vertical storefront is fed by several suppliers. If two suppliers can deliver the same item, the system must decide whether the shopper sees one product or two listings. This single choice determines the shape of matching, pricing, stock computation, sourcing, order splitting and returns.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A: 1 supplier item = 1 product | Simplest; no matching; no sourcing logic at order time | Duplicate listings compete with each other; cannibalised SEO; no failover when a supplier runs out; worse margin (cannot pick cheapest) |
| B: canonical product with many offers, best offer selected | One clean listing; supplier failover; margin optimisation; correct multi-supplier stock | Requires product matching (the hard part); sourcing decision logic; price can change when the winning offer changes |
| C: hybrid - canonical only where a reliable match key exists (GTIN/EAN/MPN), otherwise 1:1 | Pragmatic; matching only where it is trustworthy | Two code paths; inconsistent behaviour to reason about |

## Decision
TODO(human): not yet decided.

## Decision inputs needed
- Do suppliers provide GTIN/EAN/MPN reliably? Without a trustworthy match key, option B's matching becomes fuzzy and expensive.
- How much overlap is expected between suppliers in the same vertical?
- Is supplier failover a commercial requirement, or acceptable to lose the sale?

## Consequences
To be filled on decision.

## Revisit triggers
- Supplier overlap turns out materially different from the assumption used to decide.
