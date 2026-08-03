---
doc: vision
purpose: Why the project exists, the business model, what success is, what is out of scope.
read_when: any product or prioritisation question
status: draft
updated: 2026-08-03
related: [00-product/automation-charter.md, 00-product/roadmap.md]
---

# Vision

## One-liner
A greenfield dropshipping platform: 10-20 niche storefronts on a single Magento 2 Open Source instance, all first-party, sourced from multiple suppliers, operated by one person, with the goal state that no human touches the path from supplier feed to delivered order.

## Business model
- First-party only. No third-party sellers on the sites (INV-04). The operator is the merchant of record.
- Dropshipping. No owned warehouse or stock (INV-05). Suppliers hold inventory and ship to the customer.
- Vertical storefronts. Each tenant is a niche (clothing, tableware, ...) fed by several suppliers.
- Revenue = margin between supplier cost and storefront price, minus acquisition and payment cost.

## Why this shape
- Multiple niche storefronts multiply market coverage without multiplying operating cost - if per-storefront cost trends to near-zero.
- Dropshipping removes capital lock-up in inventory, and moves the hard problems to data: feed quality, stock freshness, order routing, lead-time accuracy.
- Luma-class frontends fail Core Web Vitals; organic search is a primary acquisition channel, so frontend performance is a revenue variable, not a preference.

## Success criteria
- SC-01 10-20 storefronts live on one Magento instance, each with its own assortment, layout and UX flow.
- SC-02 Core Web Vitals pass (field/CrUX) on every storefront: LCP < 2.5s, INP < 200ms, CLS < 0.1.
- SC-03 Launching storefront N+1 **inside an already-live market** is a configuration change measured in hours, not weeks. Entering a new country is not: EPR registration is per member state and per stream, and a non-established seller must appoint an Authorised Representative there. See `00-product/market-selection.md` HF-05.
- SC-04 Total infrastructure cost scales sublinearly with storefront count.
- SC-05 Onboarding a new supplier is a configuration + mapping task, not a code change.
- SC-06 Oversell rate below a defined threshold. TODO(human): set the threshold.
- SC-07 Automation level per value-chain stage reaches L2 or higher (see automation charter).
- SC-08 Stable long-term profitability. TODO(human): define the concrete financial target and horizon.

## Constraints
- Single operator. No human team. Capacity is the binding constraint on every plan.
- Preparatory phase is intentionally unbounded in time; correctness of foundations outranks speed.
- Priority order for platform decisions: infrastructure cost > Core Web Vitals/SEO > maintenance effort > time-to-launch.

## Structural risks of the model
These are inherent to dropshipping and must be designed for, not discovered later.
- Stock staleness -> oversell -> cancellations -> marketplace/payment penalties and SEO-irrelevant reputation damage.
- Price drift -> selling below cost.
- Multi-supplier orders -> split shipments, multiple tracking numbers, partial fulfilment.
- Lead-time variance -> delivery promises that cannot be kept.
- Returns -> unclear ownership when the operator holds no warehouse. TODO(human): returns policy is a prerequisite for the returns design.
- Supplier feed schema drift -> silent catalog corruption.
- Supplier concentration -> a single supplier's outage removes a storefront's assortment.

## Out of scope (for now)
- Third-party seller onboarding.
- Owned warehouse or 3PL fulfilment.
- Second Magento instance or catalog split.
- Native mobile apps.

## Launch shape (decided 2026-08-03)
- First storefront targets one large EU country. Single market, single currency, single tax regime, one primary language.
- 1-2 suppliers on the first vertical.
- Mixed supplier channels: part REST/JSON API, part CSV/XML over SFTP. The adapter rule in `00-product/automation-charter.md` applies from day one.
- Selection criteria for the first vertical, in no priority order: catalog complexity, operational risk, supplier maturity, organic competition. All four weigh equally.

## Open questions
- OPEN: which large EU country, and which vertical. Subject of the first-vertical research; the two are decided together.
- OPEN: per-supplier feed cadence, and delta vs full-snapshot.
- OPEN: whether the API-channel supplier exposes real-time stock/price or only a catalog endpoint. This changes the freshness architecture.
- OPEN: who is the shipper of record on the parcel (operator branding vs supplier branding)?
- OPEN: payment flow - does the operator pay suppliers per order, on account, or prepaid balance?
