---
doc: assumptions
purpose: Load-bearing assumptions the project has not verified, what rests on each, and the test that would disprove it.
read_when: before accepting an ADR, before a phase gate, whenever a decision cites an assumption as if it were settled
status: living
updated: 2026-08-04
related: [INDEX.md, 00-product/vision.md, 60-decisions/ADR-0001-storefront-stack.md]
---

# Assumptions

An invariant is a constraint the project chose and will not violate. An assumption is a belief the project depends on and has not tested. Both look identical in a document; only one of them can be wrong without anyone noticing.

Entries here were promoted out of the invariant list on 2026-08-04, or discovered by the foundational audit the same day. Each names what would falsify it. An entry with no falsifier is a defect in this file.

## ASM-01 - one Magento instance serves all websites
Was INV-01. Reclassified 2026-08-04: it is a capacity bet nobody has measured.

- Statement: one Magento 2 Open Source instance serves all 10-20 websites. No second instance.
- What rests on it: ADR-0001 (headless storefronts against one GraphQL endpoint), SC-01, SC-04, the entire infrastructure cost model, and the single `Commerce core` container in `10-architecture/c4-container.md`.
- Falsifier, measurable at Phase 0: indexer wall time at N websites against real catalog size; GraphQL p95 under multi-website scope resolution; admin usability at 20 store views. TODO(human): set the threshold at which a second instance or a catalog split becomes correct.
- Status: untested. No Magento instance exists yet.
- If false: ADR-0001 and ADR-0002 hold, but the cost model and SC-04 do not, and INV-01's replacement is an ADR on catalog partitioning.

## ASM-02 - the platform priority order
Was INV-08. Reclassified 2026-08-04: it has no derivation, and its second term depends on ASM-03.

- Statement: infrastructure cost > Core Web Vitals/SEO > maintenance effort > time-to-launch of a new storefront.
- What rests on it: ADR-0001, ADR-0002 and ADR-0003 each resolved a trade-off using this order. It is the project's tie-breaker.
- Dependency: the second term is load-bearing only while organic search is the acquisition engine (ASM-03). Under the paid-traffic fallback the operator chose on 2026-08-04, Core Web Vitals still matter - for conversion and for paid quality scoring - but they stop being the acquisition engine, and time-to-launch gains direct revenue value because paid traffic can be switched on the day a storefront exists.
- Falsifier: settle the acquisition channel. If paid becomes primary rather than a fallback, this order is re-derived, not patched.
- Status: retained as the working tie-breaker. No longer treated as unquestionable.

## ASM-03 - attribute-generated content can win Dutch organic
Discovered by the 2026-08-04 audit. The single most consequential unexamined premise in the project.

- Statement: copy generated from structured attributes, in a language the operator does not speak, built on distributor feeds available to every competitor, can win organic search in Dutch.
- What rests on it: the acquisition model, ASM-02 through its second term, and through ASM-02 the trade-offs settled in ADR-0001, ADR-0002 and ADR-0003. MC-05 in `00-product/market-selection.md` made attribute-generated content a binding constraint on vertical selection because of it.
- Failure mode 1, loud: the content does not rank. Measurable, but lagging by months and confounded with niche competitiveness - a bad ranking does not say whether the copy or the niche was wrong.
- Failure mode 2, silent: the content is poor and nothing reveals it. The operator cannot read the output language, and as of 2026-08-04 has no reviewer and no quality signal of any kind. This mode produces months of output with no internal indication of failure.
- Falsifier for mode 1: **not** the keyword analysis on its own. Corrected 2026-08-04 - the first version named `bd` issue docs-pjl, whose scope is search volume and top-10 domain strength. That measures whether the niche is winnable, not whether this content model wins it, and so cannot separate "the niche is too hard" from "attribute-generated copy does not rank" - the confound named directly below. A discriminating observation is required: whether any top-10 page is itself built on the same distributor descriptions, and whether any player ranks without a content budget of its own. Both are now in docs-pjl's scope.
- Falsifier for mode 2: **none exists.** Nearest cheap instrument is paid native-speaker review of a sample of generated pages before launch. TODO(human): decide whether to buy it.
- Fallback if false: paid traffic, chosen 2026-08-04. Consequence: SC-08 stops being deferrable. Distributor margin must cover paid customer acquisition cost, and nothing in the corpus establishes that it does.

## Verified-fact debt
A different class: statements presented as fact that were never checked against a primary source. Tracked as work, not as assumptions.

- Version claims in `10-architecture/c4-container.md` - `bd` issue docs-rt4.
- Market-share and return-rate figures in `00-product/market-selection.md` - `bd` issue docs-ruf.

## Promotion and demotion
- An assumption becomes an invariant only through an ADR that records the evidence. Passing a test is not enough on its own; the reasoning has to be frozen.
- An invariant becomes an assumption when someone establishes it was never derived. That demotion is recorded here with the date and the reason, as ASM-01 and ASM-02 are.
