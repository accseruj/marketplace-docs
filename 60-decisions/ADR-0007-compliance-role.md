---
doc: adr-0007
purpose: Which role the operator takes under EU product-safety law, and therefore where goods may be sourced from.
read_when: onboarding a supplier, evaluating a sourcing channel, considering private label
status: frozen
updated: 2026-08-03
---

# ADR-0007: Compliance role in the supply chain - distributor only

- Status: accepted
- Date: 2026-08-03
- Deciders: human
- Related: INV-04, INV-05, INV-06, 00-product/market-selection.md, 00-product/automation-charter.md

## Context
GPSR, Regulation (EU) 2023/988, applies since 2024-12-13 to every non-food consumer product placed on the EU market. It assigns obligations by role, not by company size, and the role follows from where the goods come from and whose name is on them. The operator is a single person running a feed-driven catalog (INV-06, `00-product/vision.md`), so the deciding question is not which role is cheapest in fees but which role is executable at all without a compliance team.

Reference material and the regulatory citations are in `00-product/market-selection.md`.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A: Distributor - source only from EU-established suppliers who have already placed the goods on the EU market | Obligations reduce to verification, preservation of condition, and assistance with withdrawals and recalls. No technical file. No Responsible Person to appoint | Gross margin capped by EU distributor pricing. Assortment limited to what EU distributors already carry |
| B: Importer - source directly from non-EU manufacturers | Highest margin. Assortment not limited by EU distribution | Per-product verification of manufacturer compliance, own name and contact on the product, technical documentation, EU Responsible Person named on product or packaging, serious-incident reporting within two working days. Not executable by one person across a feed of thousands of SKUs |
| C: Private label - own brand applied to distributor goods | Margin and differentiation. Escapes direct price comparison | Reclassifies the operator as manufacturer, with full manufacturer obligations including documented risk analysis per product. Strictly worse than B on compliance load |

## Decision
Option A. The operator is a distributor under GPSR and takes no other role.

## Consequences
- Positive: obligations are verification-shaped, not documentation-shaped. Verifying that a product bears required identification and manufacturer/importer labelling is a data check that fits the content-quality gate (VC-04) as a publishability rule.
- Positive: supplier onboarding (VC-01) gains a hard, checkable gate instead of a judgement call. A supplier that cannot evidence the goods are already on the EU market is rejected, not negotiated with.
- Positive: no Responsible Person appointment, no technical documentation store, no Safety Business Gateway integration at launch.
- Negative: gross margin is capped by EU distributor cost. Direct-from-manufacturer margin is unavailable, and the business case must close without it.
- Negative: assortment is limited to what EU distributors carry. Differentiation must come from niche selection, content and UX - never from exclusive product.
- Negative: rebranding as a way to escape price comparison is closed off permanently.
- Follow-up: the supplier adapter contract must carry manufacturer/importer identification and labelling evidence as feed fields. It is catalog data, not paperwork, and it must not arrive by email (automation charter anti-patterns).
- Follow-up: INV-10 and INV-11 recorded in `INDEX.md`.

## Revisit triggers
- A chosen vertical's margin proves unworkable at EU distributor cost and the business case depends on direct import. Option B is then re-costed with the per-product compliance workload stated explicitly, not assumed away.
- Volume reaches a point where the compliance function can be bought as a service rather than performed by the operator.
- GPSR guidance or case law moves the distributor/importer boundary for dropshipping specifically.
