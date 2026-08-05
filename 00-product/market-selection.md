---
doc: market-selection
purpose: Candidate first market and first vertical, scored against the launch criteria and against EU product-compliance law.
read_when: choosing or revisiting the first market/vertical; before ADR-0005 sizing inputs
status: draft
updated: 2026-08-05
related: [00-product/vision.md, 00-product/automation-charter.md, 60-decisions/ADR-0005-catalog-data-layer.md, 60-decisions/ADR-0007-compliance-role.md]
---

# Market and vertical selection

## Selection criteria
Set by the operator, all weighted equally:
- MC-01 Catalog complexity - avoid size grids, colourways, thousands of variants, heavy editorial content.
- MC-02 Operational risk - avoid high return rates, fragile and bulky goods, sharp seasonality.
- MC-03 Supplier maturity - suppliers with real feeds, EAN coverage, usable stock signals.
- MC-04 Organic competition - a niche a solo operator can rank in without a content or link budget.

Derived from the operator's constraints, not stated but binding:
- MC-05 Content must be generatable from structured attributes. The operator works in English and translates with an LLM; a vertical whose copy is emotional or brand-voice driven cannot be produced at 10-20 storefronts by one person.
- MC-06 Compliance surface must be minimal. See hard filters below.

## Regulatory facts
These were the decisive input and they constrain the model more than any commercial consideration.

- REG-01 GPSR, Regulation (EU) 2023/988, applies since 2024-12-13 to every non-food consumer product placed on the EU market.
- REG-02 Reselling goods that an EU economic operator has already placed on the EU market makes the operator a **distributor**: verify the product carries required identification and manufacturer/importer labelling, preserve condition, assist with withdrawals and recalls.
- REG-03 Sourcing from outside the EU makes the operator the **importer**: verify manufacturer compliance, add own name and contact details to the product, hold technical documentation, name an EU Responsible Person on product or packaging, report serious incidents through the Safety Business Gateway within two working days.
- REG-04 Selling under own name or trademark reclassifies the operator as **manufacturer**, with full manufacturer obligations including documented risk analysis per product.
- REG-05 EPR has no EU-level registry. Registration is per member state and per stream: packaging, WEEE, batteries.
- REG-06 From 2026-08-12 a seller not established in a member state must appoint an EPR Authorised Representative in each member state where it sells. PPWR, Regulation (EU) 2025/40, applies from the same date.
- REG-07 Battery EPR registration deadline was 2025-08-18; full battery labelling - capacity, lifespan, QR, recycling - from 2026-08-18.
- REG-08 Germany: the withdrawal button under the new §356a BGB is mandatory since 2026-06-19. Non-compliance exposes up to 4% of annual turnover plus competitor warning letters.
- REG-09 Germany's Abmahnung system lets competitors and associations enforce commercially, typically €1,000-3,000 per warning. Common triggers: incorrect withdrawal policy, missing unit prices, misleading strikethrough prices, incomplete legal notices.

## Hard filters
Each filter removes a whole class of work from the first launch. They are cheap now and expensive to retrofit.

- HF-01 Source only from suppliers who have already placed the goods on the EU market. Keeps the operator a distributor under REG-02 instead of an importer under REG-03. Now permanent as INV-10; see ADR-0007.
- HF-02 No own brand, no private label, no rebranding of supplier goods. REG-04 would reclassify the operator as manufacturer. Now permanent as INV-11; see ADR-0007.
- HF-03 First vertical carries no electrical or electronic goods. Removes the WEEE EPR stream and the CE/EPREL workload.
- HF-04 First vertical carries no batteries and no goods sold with batteries. Removes the battery EPR stream and REG-07 labelling.
- HF-05 One market at launch. Every additional country multiplies EPR registrations across three streams and requires an Authorised Representative under REG-06.

HF-05 is why SC-03 in `00-product/vision.md` carries a within-one-market qualifier. Storefront N+1 in a live market is hours. Country N+1 is a compliance project.

## Candidate markets

| Market | E-commerce size | Marketplace gravity | Legal exposure to a foreign solo operator | Supplier depth | Language feasibility |
|---|---|---|---|---|---|
| Germany | Largest in the EU | Amazon dominant | **Highest.** Abmahnung (REG-09) plus §356a (REG-08). Enforcement is by competitors, not only regulators | Deepest | German legal text via LLM is direct Abmahnung exposure |
| Poland | Fast growth | **Highest.** Allegro reaches over 80% of Polish online shoppers; marketplaces are 50-60% of online sales | Regulator-led (UOKiK), no competitor-driven warning industry | **Deepest feeds in the EU.** 270+ integrated distributors, XML with EAN, hourly stock sync, BaseLinker ecosystem | Polish-language SEO via LLM; low AOV; Ceneo price transparency |
| Netherlands | USD 36.5bn in 2025 | Moderate. bol EUR 5.17bn + Amazon.nl EUR 3.70bn against a much larger total | Regulator-led (ACM). No Abmahnung analogue | Real cluster of EU-warehoused dropship distributors with API/XML feeds, several headquartered there | Highest English proficiency in the EU; Dutch is well served by LLM translation |

Not scored in depth: France, Spain, Italy. Language cost and supplier accessibility are worse than all three above for this operator. `OPEN` if the operator wants them evaluated.

**Recommendation: Netherlands first.**
- The two criteria that most often kill a solo operator are legal exposure and marketplace gravity. NL is the only one of the three that is moderate on both.
- Supplier warehouse and customer in the same country collapses lead-time variance - a named structural risk in `00-product/vision.md` - makes returns to the supplier cheap, and defers cross-border VAT entirely.
- Germany is the right **second** market, entered once the machine runs and the legal texts have been reviewed by a German lawyer once. It is the wrong market to learn in.
- Poland is the strongest **supplier** country and a weak first **sales** country for an organic-led standalone shop. Its feed ecosystem is worth using from a Dutch storefront if the distributors ship EU-wide.

Cost accepted with NL: iDEAL is 60-70%+ of Dutch online transactions and is migrating to Wero. It is a launch requirement, not an option. Population is 18m, smaller than DE/PL/FR - the market is large by spend per head, not by head count.

## Candidate verticals
Return rates are European 2025-2026 benchmarks; overall EU average is 18-22%.

| Vertical | Return rate | MC-01 complexity | MC-03 identifiers | Supplier maturity | MC-04 competition | Passes HF-03/04 | Verdict |
|---|---|---|---|---|---|---|---|
| Apparel | 30-46% | Size grids, colourways | Poor GTIN | High | Brutal | yes | **Excluded on returns alone** |
| Footwear | 31-39% | Size grids | Poor | High | Brutal | yes | **Excluded** |
| Consumer electronics | 5-15% | Low | Excellent | High | Amazon gravity, price volatility | **no** | **Excluded on HF-03/HF-04** |
| Home and garden, broad | 8-25% | Medium; tableware fragile | Mixed EAN | Good (dropXL, Everspring, NL/DE) | High - category is too broad to rank in | yes | Viable only if narrowed |
| Pet supplies, non-food accessories | Low | Low | Good EAN on branded | Good (Warmako Rotterdam, NL warehouse, EDI/API; Zoodrop) | Zooplus dominates EU pet e-commerce | yes | **Alternate.** Exclude dry food and litter - bulky, grocery margins |
| Hand tools, workshop and fastening consumables | Low | Low; spec-driven, no variants | Excellent MPN + EAN | Strong EU distributor base | Segment-dependent | yes | **Primary candidate** |
| Horeca / professional non-electric kitchen | Very low | Low; spec-driven | Good | Moderate | Low | yes | Alternate. Low search volume; B2B payment-term expectations |

**Recommendation: hand tools and workshop consumables, narrowed to one segment.**
- Best fit for MC-05: the buyer wants specification, not brand voice. Product copy generates from structured attributes, which is the only content model a solo operator can run across 10-20 storefronts.
- Best fit for MC-03: MPN and EAN coverage is the strongest of any candidate, which keeps the ADR-0006 matching stage cheap when it turns on. Qualified 2026-08-05: coverage is confirmed high, but the surveyed supplier's identifiers are own-brand and therefore shared with no other distributor. Coverage was the wrong measure; see SL-30 in `10-architecture/supplier-landscape.md`.
- Passes HF-03 and HF-04 as long as powered tools are excluded. Excluding them is also what keeps returns low.
- Durable in transit, no size grids, low seasonality.
- **Supplier maturity confirmed 2026-08-05; the delivery model is the problem.** Eleven live NL wholesalers in this vertical were verified, so the distributor base is real. None of them publishes a dropshipping programme - every reseller offer is a trade account or pallet wholesale into the reseller's own warehouse. The first supplier is therefore negotiated rather than selected, which is a commercial task with a lead time. See SL-33 and SL-35 in `10-architecture/supplier-landscape.md`.

## What is not yet verified
MC-04 is the one criterion this research cannot settle from public sources. Organic competition is per-keyword, not per-category.

- Required before committing: keyword-level competition analysis for two or three concrete segments in Dutch, with search volume, top-10 domain strength, and whether bol.com and the incumbent DIY chains hold the head terms.
- Required before committing: two or three named NL-warehoused distributors in the chosen segment, with a sample feed actually retrieved and inspected. That inspection also produces the ADR-0005 sizing inputs (SKU count, delta vs full snapshot, cadence) and the ADR-0006 identifier-quality answer.
- Partially done 2026-08-05, desk research only: fifteen named candidates with their liveness verified, published reseller terms, one full dropship contract and a measured catalogue, in `10-architecture/supplier-landscape.md`. No feed retrieved, so cadence, delta-vs-snapshot and the real field list remain unanswered - and no supplier in this vertical publishes a dropship programme to sign up to, so obtaining one is a negotiation (SL-35). That survey qualifies two claims below - see SL-30 and SL-31.

## OPEN
- OPEN: which segment inside hand tools and workshop consumables. Needs the keyword analysis above.
- OPEN: France, Spain, Italy not evaluated - evaluate only if the operator rejects all three scored markets.
- OPEN: whether Polish distributors will ship into NL on dropship terms, which would combine the best feed ecosystem with the best sales market.
