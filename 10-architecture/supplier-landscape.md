---
doc: supplier-landscape
purpose: What named NL dropship suppliers in the fastening and hand-tool vertical actually publish - fees, feed formats, identifier quality - measured rather than assumed.
read_when: before deciding ADR-0005, ADR-0006, sourcing scope, or returns policy; before contacting a supplier
status: draft
updated: 2026-08-05
related: [00-product/market-selection.md, 00-product/automation-charter.md, 60-decisions/ADR-0005-catalog-data-layer.md, 60-decisions/ADR-0006-product-identity.md, 60-decisions/ADR-0007-compliance-role.md]
---

# Supplier landscape - NL, fastening and hand tools

Desk research only. No supplier account was held and no feed file was retrieved; every fact below comes from a public page or a published contract. `bd` issue docs-jvy remains open for the feed itself.

## How to re-derive anything here
- Catalogue counts: `curl -s https://www.wovar.nl/sitemap.xml`, then count `<loc>` in the child sitemaps.
- Identifier coverage: fetch product pages, read the `EAN code` row of `table.spec-table`, or the Apollo blob keys `WVR1_ERP_EAN_code` / `WVR1_Generaldata_Barcode_1`.
- Contract terms: the PDF cited in SUP-01, extracted to text.
- Sampling was seeded (`random.seed(20260805)`), so the same 40 URLs are reproducible from the sitemap.

**Do not read `itemProp="gtin13"` from the microdata.** It belongs to the related-products carousel and always renders `content="-"`. Reading it produces 0% EAN coverage on a catalogue that in fact carries 98%. This false negative was produced and caught on 2026-08-05.

## Candidates

| ID | Supplier | Vertical fit | Dropship programme | Feed | Status observed 2026-08-05 |
|---|---|---|---|---|---|
| SUP-01 | Handelsonderneming Van Doleweerd VOF, Oss, KvK 17146505 | Ijzerwaren, fastening | **Yes, contract published** | XML, CSV or TXT | `doleweerd.nl` returns HTTP 500 (WordPress fatal); `dealer.doleweerd.nl` returns 404 |
| SUP-02 | Wovar, `wovar.nl` | **Best fit** - fastening, hardware, hand tools | **No** - business account, full-pallet wholesale, project quotes only | none published | Live |
| SUP-03 | Drobbs / `dropshipspecialist.nl` | Partial - broad home and garden, tools a slice | Yes | CSV, XML, API | Live |
| SUP-04 | `gereedschapdropshipping.nl` | Good - tools, workshop, PPE, consumables | Advertised | not published | TLS certificate expired; HTTP 403 to automated requests |

No candidate satisfies both "right vertical" and "dropship feed available" at once. SUP-02 has the assortment and no programme; SUP-01 has the programme and a broken web presence.

## SUP-01 contract terms
Source: `Voorwaarden dropshipment / productfeed`, Handelsonderneming Van Doleweerd VOF, version 17 February 2019. Seven years old - treat every figure as indicative until reconfirmed.

- SL-01 Dropship fee is **EUR 8,50 per Order excl. VAT**, all-in: handling, packaging, shipping, insurance to EUR 500 incl. VAT (art. 4.2).
- SL-02 The feed is a file - XML, CSV or TXT - carrying article numbers, product names, brand names, descriptions, photos, advice prices and stock (art. 1.1). No EAN in the enumerated field list.
- SL-03 Update cadence is not stated. Products are updated automatically and discontinued products are disabled (art. 3.4). Full-snapshot versus delta is not stated.
- SL-04 A one-off feed setup fee applies; the amount is negotiated, not published (art. 4.5). Format is guaranteed unchanged for six months after payment (art. 11.1).
- SL-05 Orders are placed **only through the dealer portal**. Telephone and e-mail are refused, and a placed order cannot be amended (art. 5.3).
- SL-06 Feed prices are not authoritative. Purchase prices change daily; the price in the portal at the moment of ordering governs (art. 4.3).
- SL-07 Resale price is constrained: at most 10% below the advice price, 20% during a temporary promotion, or the feed is cut off (art. 3.2, 3.3).
- SL-08 Partial delivery is at the supplier's discretion when not everything is in stock (art. 6.3). A multi-line order is therefore not guaranteed to be one parcel.
- SL-09 Consumer returns go to the webshop, never to the supplier; the supplier accepts returns only from the webshop and only under its own terms (art. 7.1, 7.2).
- SL-10 Cut-off is 12:00 on working days for same-day dispatch; 12:00-16:00 is best effort and not guaranteed (art. 6.2).
- SL-11 Delivery is limited to NL, BE and DE, and non-NL destinations may not exceed 10% of shipments (art. 6.5).
- SL-12 The reseller must accept new terms within five working days or the feed may be stopped (art. 1.3).
- SL-13 Orders are collected daily and invoiced together (art. 9.1).
- SL-32 On the supplier's request, the webshop must correct incorrect product information within three working days (art. 3.8). An obligation with a deadline, landing on the operator, on a corpus generated from the feed.

Every figure above was re-extracted with `pdftotext -layout` on 2026-08-05 and matches. The first extraction used a hand-rolled parser that rendered the euro sign as `#`; the amounts survived that unharmed, but the tool is named here so the next reader uses the right one.

## SUP-03 published terms
- SL-14 Shipping is **EUR 6,95 per order** to NL and EUR 7,95 to BE, plus EUR 5 per 10 kg above 23 kg.
- SL-15 Entry requires a KvK number, a VAT number and a minimum annual turnover of EUR 5.000. There is no minimum order value.
- SL-16 Assortment is 2.000+ products; feed is CSV, XML or API. Cadence not stated.

## SUP-02 measured catalogue
Measured 2026-08-05 from the public webshop, not from a B2B feed. A B2B feed may expose more or fewer fields.

- SL-17 6.704 product URLs and 1.610 category URLs in the NL sitemap, `lastmod` 2026-08-04. The site claims "5000+ artikelen direct leverbaar uit eigen voorraad"; the two figures are consistent if some URLs are variants.
- SL-18 EAN present on **39 of 40** sampled products (98%). Article number `WV######` present on the same 39.
- SL-19 Brand field: Wovar on 34 of 40, Lavuzo on 4, unread on 2. Both are the supplier's own marks.
- SL-20 Sampled EANs cluster in a narrow prefix block, consistent with issuance under one GS1 company prefix held by the brand owner. A GS1 prefix identifies the member organisation the brand owner joined, **not** the country of origin - so no origin claim is made here.
- SL-21 The catalogue contains electrical goods: 12V LED garden lighting and electric desk frames, roughly 40 URLs by slug keyword.
- SL-22 Wovar describes itself as the importer - "wij verzorgen voor u de volledige import uit het buitenland" - and offers to import third-party specifications on request.

## What this changes

- SL-23 **The market prices the order, not the line.** SL-01 and SL-14 are both per-order fees. A per-line cheapest-offer rule that splits a basket across two suppliers pays the fixed fee twice, and the fee is a large share of a fastening-basket's value. Feeds directly into `bd` issue docs-dqt (AUD-04). *Falsifier: a named NL dropship supplier whose tariff is per line or per unit rather than per order.*
- SL-24 **Consolidation cannot be assumed.** SL-08 makes partial delivery the supplier's choice. Any sourcing model that assumes one order equals one parcel is assuming a term no surveyed contract grants. *Falsifier: a contract clause guaranteeing single-parcel dispatch of an in-stock multi-line order.*
- SL-25 **Portal-only ordering collides with INV-03.** SL-05 gives no API and no event for the one transition that matters most - placing the purchase order. The automation charter's readiness test #3 fails against this supplier as contracted. Either the invariant admits a documented exception surface, or suppliers without an order API are disqualified, which shrinks an already thin candidate list. This is a decision, not a detail; it needs its own issue. *Falsifier: a dealer portal that turns out to expose a documented order API, or a supplier in this vertical that publishes one.*
- SL-26 **Returns land on the operator.** SL-09 means a dropshipping model with no warehouse still needs a return address, an inspection step and a restocking route. Feeds into `bd` issue docs-1kr. *Falsifier: a supplier contract in this vertical that accepts consumer returns directly.*
- SL-27 **Feed price is a display price, not a sourcing price.** SL-06 means the feed cannot be the price of record. INV-09 - never display availability that cannot be sourced - extends to price if the gap between feed and portal is material. *Falsifier: a supplier whose feed price is contractually binding at order time.*
- SL-28 **Hard filters cut at catalogue level, not supplier level.** SL-21 shows the best-fit supplier carries EEE, which HF-03 excludes. Category and brand exclusion during ingestion is therefore a compliance control with an audit trail, not a merchandising preference. Both SUP-01 (art. 3.1) and SUP-02 allow selecting part of the assortment, so the filter is exercisable.
- SL-29 **Buying from an importer keeps the operator a distributor; buying through one does not.** SL-22 means the goods are already placed on the EU market, satisfying HF-01 and INV-10. The same supplier's offer to import to specification would make the operator the importer under REG-03. Record the boundary before any sourcing conversation.

## Contradicts what the repo currently says
- SL-30 `00-product/market-selection.md` MC-03 credits hand tools with "Excellent MPN + EAN". Coverage is excellent (SL-18) but the identifiers are own-brand (SL-19, SL-20). ADR-0006's canonical-product-with-supplier-offers model assumes offers from different suppliers can be matched onto one product; for an own-brand catalogue there is nothing to match, because no other distributor carries that article. The identifier question is not "is there an EAN" but "is the EAN shared".
- SL-31 `00-product/market-selection.md` names dropXL, Everspring, Warmako and Zoodrop as evidence of NL supplier depth. None of them is in the fastening or hand-tool vertical; they are home-and-garden and pet. The supplier-depth claim for the chosen vertical rests on the four candidates in this file, one of which has no dropship programme and one of which is unreachable.

## OPEN
- OPEN: SUP-01's terms are from 2019 and its website is down. Is the company still trading and is the dropship programme still offered? KvK 17146505 is the check.
- OPEN: SUP-04 blocks automated access and needs a manual visit; it is the only remaining candidate with both the right vertical and an advertised programme.
- OPEN: whether any surveyed supplier exposes an order API rather than a portal. Determines SL-25.
- OPEN: whether a B2B feed carries EAN where SL-02's field list omits it. Only a real feed answers this.
- OPEN: delta versus full snapshot, and cadence, for every candidate. Unanswerable from public pages; it is the core of docs-jvy.
