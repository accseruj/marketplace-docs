---
doc: c4-container
purpose: Deployable units, runtimes, data stores and the repos that own them. Level 2 of C4.
read_when: any question about where code or data lives
status: draft
updated: 2026-08-02
related: [40-devops/README.md, 60-decisions/ADR-0002-deployment-model.md, 60-decisions/ADR-0005-catalog-data-layer.md]
---

# C4 L2 - Containers

| Container | Runtime | Repo | Owns | Notes |
|---|---|---|---|---|
| Storefront app | Next.js (App Router) on Cloudflare Workers via OpenNext | `storefront` (monorepo) | All tenant rendering | Multi-tenant, hostname routing. ADR-0002 |
| Shared UI package | TypeScript | `storefront/packages/ui` | Component library | shadcn-style ownership |
| Tenant config | TypeScript, versioned in git | `storefront/packages/config` | Layout maps, tokens, feature flags, route overrides | Not in a database |
| Commerce core | Magento 2 Open Source, PHP 8.4, Docker | `m2` | Catalog scope, prices, orders, customers, stock projection | One instance, 10-20 websites. INV-01 |
| Catalog data layer | TBD - see ADR-0005 | TBD | Canonical products, supplier offers, matching, enrichment state | BLOCKING decision |
| Feed ingestion + supplier adapters | TBD - see ADR-0005 | TBD | Feed intake, validation, quarantine, normalisation | One adapter per supplier channel |
| Order routing / sourcing | TBD | TBD | Sourcing decision, order splitting, PO lifecycle | Core of the dropshipping model |
| Event bus | RabbitMQ | infra | Async contracts between components | |
| Search | OpenSearch 2.19+ | infra | Catalog search | Elasticsearch removed in Magento 2.4.8 |
| Cache/session | Valkey 8 / Redis 7.2 | infra | | |
| HTTP cache | Varnish 7.6/7.7 | infra | Magento FPC + GraphQL | Per-domain vary |
| Image service | imgproxy behind Cloudflare CDN | infra | On-the-fly transforms | Avoids per-transform vendor pricing |

## Data ownership rules
- Supplier offers (cost, availability, lead time): catalog data layer.
- Canonical product content: catalog data layer, projected into Magento for sale.
- Retail price, orders, customers, carts: Magento.
- Sellable stock shown to shoppers: derived from supplier offers, projected into Magento. Never authored by hand.
- Purchase orders and supplier fulfilment state: order routing component.
- Tenant presentation config: git, not a database.

## Open structural question
Whether the catalog data layer and order routing are separate services or Magento modules is ADR-0005 / ADR-0006 territory. Nothing downstream should be built until both are decided.
