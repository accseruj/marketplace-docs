---
doc: supplier-landscape
purpose: What named NL suppliers in the fastening and hand-tool vertical actually publish - reseller terms, fees, feed formats, identifier quality - verified rather than assumed.
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
- Contract terms: the PDF cited in SUP-01, extracted with `pdftotext -layout -enc UTF-8`.
- Trading status: `python3 scripts/supplier-probe.py --probe <host>...`. It reports DNS, HTTP status on both schemes, certificate expiry, the live `<title>` and the last archived `<title>`, and classifies the host. It deliberately does not infer what a supplier sells - see below.
- A SUSPECT verdict means read the archived title, then open the site in a real browser. Bot protection and a dead host look identical to `curl`: `vertools.nl` answers 403 to every automated request and loads normally in a browser after a Cloudflare interstitial that clears itself.
- Sampling was seeded (`random.seed(20260805)`), so the same 40 URLs are reproducible from the sitemap.

**Do not read `itemProp="gtin13"` from the microdata.** It belongs to the related-products carousel and always renders `content="-"`. Reading it produces 0% EAN coverage on a catalogue that in fact carries 98%. This false negative was produced and caught on 2026-08-05.

**Take a supplier's vertical from the supplier's own page, never from a search-result summary.** The first version of this file classified SUP-01 from a description that belonged to a different company in the same result set. `scripts/supplier-probe.py` reports titles verbatim and classifies only liveness for this reason.

## Round 1 - suppliers that advertise dropshipping
Searched by the term "dropshipping". That framing is what produced the wrong answer; round 2 corrects it.

| ID | Supplier | Vertical fit | Dropship programme | Feed | Status observed 2026-08-05 |
|---|---|---|---|---|---|
| SUP-01 | Handelsonderneming Van Doleweerd VOF, Oss, KvK 17146505; continued as Doleweerd B.V. | **None** - scooter parts and accessories | Contract published, now moot | XML, CSV or TXT | **Bankrupt.** Activities ceased; `doleweerd.nl` returns HTTP 500 |
| SUP-02 | Wovar, `wovar.nl` | **Best fit** - fastening, hardware, hand tools | **No** - business account, full-pallet wholesale, project quotes only | none published | Live |
| SUP-03 | Drobbs / `dropshipspecialist.nl` | Partial - broad home and garden, tools a slice | Yes | CSV, XML, API | Live |
| SUP-04 | `gereedschapdropshipping.nl` | **Best on paper** - tools, workshop, PPE, consumables | Was a real programme | product list with descriptions, images, article codes | **Defunct.** Last archive capture 2022-01-23; TLS certificate expired 2024-10-10 and never renewed; HTTP 403 on every path |

Both suppliers that published a dropship programme in or near this vertical are dead. SUP-01 is bankrupt and was never in this vertical anyway; SUP-04 has not been archived since January 2022 with a certificate unrenewed since October 2024.

## Round 2 - wholesalers in the vertical, whatever they call themselves
Searched by what they sell rather than by how they sell it, and every host verified with `scripts/supplier-probe.py` before anything was written about it. Eleven live NL wholesalers in fastening and hand tools, none of which round 1 surfaced.

| ID | Supplier | What its own page says | Reseller offer as published | Verdict |
|---|---|---|---|---|
| SUP-05 | `wovar.nl` (= SUP-02) | Fastening, hardware, hand tools; 6.704 product URLs | Business account; pallet wholesale; project quotes | LIVE |
| SUP-06 | `vertools.nl` | "Specialist in bevestigingsmaterialen", ~15.000 articles, A-brands | none published | LIVE, behind Cloudflare |
| SUP-07 | `schroevengroothandel.nl` | "Meer dan 8000 soorten" screws, warehouse Heiloo | Business account, valid btw-id required, free-shipping floor EUR 90 | LIVE |
| SUP-08 | `schroevenkopen.nl` / `bevestigingspartner.nl` (M&B Bevestigingsmaterialen, since 1995) | Fastening for construction, industry, installation | Wholesale in full pallets and bulk only; "wij regelen de volledige import" | LIVE |
| SUP-09 | `schroevenland.nl` | Screw specialist; runs Magento | Business page, no programme published | LIVE |
| SUP-10 | `dkhgroothandel.nl` | "Groot in bevestigingsmaterialen" | none published | LIVE |
| SUP-11 | `wemekamp-groothandel.nl` | Fastening and tools | none published | LIVE |
| SUP-12 | `marree.nl` | Technische groothandel, Harderwijk | Account registration | LIVE |
| SUP-13 | `ijzerwarenmiddennederland.nl` | Professional tools and machines since 2004 | none published | LIVE |
| SUP-14 | `ijzerwarenunie.nl` | B2B purchasing platform, construction and industry | B2B platform | LIVE |
| SUP-15 | `mastermate.nl` | Technical wholesale; B2B eshop at `eshop.mastermate.nl` | Login-gated B2B shop | LIVE |

- SL-33 **Rewritten 2026-08-05 after round 2. The vertical has depth; what it lacks is the dropship-with-feed model.** Eleven live NL wholesalers in fastening and hand tools were verified, so the "strong EU distributor base" in `00-product/market-selection.md` is supported. Not one of them publishes a dropshipping programme. Every reseller offer found is the same shape: a business account with trade pricing, or bulk and pallet wholesale delivered to the reseller's own warehouse. The first version of this line said no supplier existed, which was an artefact of searching for the word "dropshipping" rather than for the trade. *Falsifier: an NL wholesaler in this vertical that publishes a dropship programme with a product feed - one such supplier changes the plan from "negotiate" to "sign up".*
- SL-34 **A dropship programme is a business that can fail, not an infrastructure that persists.** Two of the four round-1 candidates died inside four years, one of them between two monthly crawls. Supplier onboarding cost is therefore recurring, not one-off, and SC-05's "supplier N+1 is configuration" is load-bearing for survival rather than for growth. Check trading status before every supplier decision, not once. *Falsifier: a five-year survival rate for NL dropship suppliers materially better than the 2-of-4 seen here; this sample is too small to carry the rate itself, only the mechanism.*
- SL-35 **The launch supplier will have to be negotiated, not selected.** No published programme means the first supplier relationship is a conversation about dropshipping with a wholesaler that does not advertise one, not a signup form. That changes what Phase -1 must produce - a supplier willing to ship to the end customer on the operator's behalf and to expose a feed - and it is a commercial task with a lead time, not a research task. *Falsifier: SL-33's falsifier; a published programme removes the negotiation.*
- SL-36 **Matchable identifiers depend on the supplier's brand model, not on the vertical.** SUP-05 is own-brand throughout (SL-19), so its EANs are shared with nobody. SUP-06 and SUP-08 carry third-party manufacturer brands - Dynaplus, Proftec, Rotadrill, Simpson Strong-Tie, DEWALT - whose GTINs are the manufacturer's and therefore appear in every distributor's catalogue. ADR-0006's matching stage is cheap against the second kind and impossible against the first, which makes brand model a supplier-selection criterion and not a detail. *Falsifier: two distributors carrying the same third-party article under different GTINs, which would break matching even in the favourable case.*
- SL-37 **An industry product-data pool may already exist for this vertical.** ERP vendors serving NL ijzerwaren and gereedschap wholesalers advertise integration with `EZ-BASE` and `nexMart` as external article databases. If suppliers already publish structured article data to a shared pool, the per-supplier adapter problem in `10-architecture/api-contracts/README.md` may be partly solved upstream. Unverified - this comes from an ERP vendor's marketing page, not from EZ-BASE. *Falsifier: EZ-BASE turning out to be closed to non-members, or to carry only a fraction of the vertical.*
- SL-38 **"We handle the full import from abroad" recurs.** SUP-05 and SUP-08 both advertise it. Buying from them keeps the operator a distributor (SL-29). Accepting their offer to import to the operator's specification makes the operator the importer under REG-03. The trap is common enough in this vertical to be a standing rule rather than a note about one supplier.

## SUP-01 contract terms
Source: `Voorwaarden dropshipment / productfeed`, Handelsonderneming Van Doleweerd VOF, version 17 February 2019, extracted with `pdftotext -layout`.

Read this section as evidence about **how NL dropship contracts are written**, not about this vertical and not about a supplier anyone can still use.

- SUP-01 sold scooter parts and accessories - `<title>` on every archived snapshot reads "Groothandel in scooteronderdelen en -accessoires". This file's first version called it an ijzerwaren wholesaler. That was wrong: the description was lifted from a different company in the same search results and mapped onto this one. A supplier's vertical is a claim about the supplier, and it needs the supplier's own page.
- Doleweerd B.V. was declared bankrupt and has ceased trading; the site now carries only a notice directing questions to the curator. The snapshot of 2026-04-17 is a normal shopfront and the snapshot of 2026-05-11 is the bankruptcy notice, which brackets the failure to that window.
- Its assortment would have failed HF-03 and HF-04 regardless: scooter parts carry electrical components and batteries.
- The terms below are therefore retained for one reason only - they are a real, published, complete NL dropship contract, and the surveyed alternatives publish nothing comparable.

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

- SL-23 **The market prices the order, not the line.** SL-01 and SL-14 are both per-order fees. A per-line cheapest-offer rule that splits a basket across two suppliers pays the fixed fee twice, and the fee is a large share of a fastening-basket's value. Feeds directly into `bd` issue docs-dqt (AUD-04). **Weak on vertical:** neither data point comes from fastening or hand tools - SUP-01 sold scooter parts and SUP-03 sells home and garden. The claim is that NL dropship suppliers tariff this way, not that this vertical does. *Falsifier: a named NL dropship supplier whose tariff is per line or per unit rather than per order.*
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
- OPEN: whether any of SUP-05 to SUP-15 will dropship on request. None publishes a programme, which is not the same as refusing one. This is now the central question and it is answered by asking, not by searching. Start with SUP-06 (largest catalogue, third-party brands) and SUP-05 (measured identifier quality, ERP behind the shop).
- OPEN: what SUP-14 and SUP-15 expose behind their B2B logins. A login-gated purchasing platform is the most likely place in this vertical to find a real feed and an order API, and it is invisible from outside.
- OPEN: whether EZ-BASE or nexMart is reachable by a small reseller, and what article data it carries (SL-37).
- OPEN: whether any surveyed supplier exposes an order API rather than a portal. Determines SL-25.
- OPEN: whether a B2B feed carries EAN where SL-02's field list omits it. Only a real feed answers this.
- OPEN: delta versus full snapshot, and cadence, for every candidate. Unanswerable from public pages; it is the core of docs-jvy.
