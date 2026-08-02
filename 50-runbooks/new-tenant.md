---
doc: runbook-new-tenant
purpose: RB-new-tenant. Procedure for launching storefront N+1.
read_when: onboarding a new tenant
status: draft
updated: 2026-08-02
related: [30-frontend/README.md, 20-backend/README.md]
---

# RB-new-tenant

Target: hours, not weeks (SC-03). Target automation level L2 (VC-06).

## Steps
1. Magento: create website, store, store view. Assign root category. Set locale, currency, tax scope.
2. Magento: assign assortment. Rule-driven, not hand-picked (VC-03).
3. Config repo: add tenant entry - domain, theme tokens, layout archetype, layout map, feature flags.
4. Cloudflare: add domain, TLS, route to the storefront Worker.
5. SEO: verify per-domain sitemap and robots, self-referencing canonicals, JSON-LD present in initial HTML.
6. Smoke: PLP, PDP, search, add-to-cart, checkout, account. Visual regression baseline captured.
7. CWV check on the new domain against the route-archetype budgets.
8. Flip state SM-tenant-onboarding to `live`.

## Automation debt
Each step above that is still manual must be listed here with a planned automation approach.
- TODO(Claude): fill this table once the steps are real.
