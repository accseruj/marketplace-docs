---
doc: tenants-index
purpose: Where per-storefront knowledge lives, and the boundary between tenant docs and tenant config.
read_when: working on a specific storefront
status: living
updated: 2026-08-02
related: [30-frontend/README.md, 50-runbooks/new-tenant.md]
---

# Tenants

One file per tenant: `70-tenants/<slug>.md`. Copy `TEMPLATE.md`.

## The boundary (do not blur this)
- **Docs hold the WHY**: niche, positioning, target market, supplier mix, pricing policy, SEO strategy, commercial constraints, decisions specific to this storefront.
- **Code config holds the WHAT**: domain, theme tokens, layout archetype, layout map, feature flags, route overrides. Lives in `storefront/packages/config`, versioned with the code.
- A value must exist in exactly one of the two. If a token value appears in a tenant doc, that is a bug.

## Loading policy
Tenant docs are NOT loaded into Claude project knowledge by default. They are read on demand when the task concerns that tenant. Twenty tenant files in permanent context would crowd out the architecture that applies to all of them.

## Cross-tenant patterns
If the same fact appears in three tenant docs, it is not tenant-specific - promote it to the relevant platform doc and delete it from the three.
