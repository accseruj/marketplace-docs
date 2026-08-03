---
doc: index
purpose: Routing table. Read this first in every session; it says which files to open for a given task.
read_when: always, at session start
status: living
updated: 2026-08-03
---

# INDEX

## Read-order for any session
1. `INDEX.md` (this file)
2. `CONVENTIONS.md` - how these docs are written and updated
3. `00-product/automation-charter.md` - the north star every decision is tested against
4. The task-specific files from the routing table below

## Routing table

| If the task is about... | Read |
|---|---|
| Why the project exists, success criteria, business model | `00-product/vision.md` |
| Automation goal, automation-readiness test | `00-product/automation-charter.md` |
| What we build next, phase gates | `00-product/roadmap.md` |
| Which market and which vertical launches first, EU compliance filters | `00-product/market-selection.md` |
| Term I don't recognize | `00-product/glossary.md` |
| System boundaries, external actors | `10-architecture/c4-context.md` |
| Services, repos, runtimes, data stores | `10-architecture/c4-container.md` |
| Entities, ownership, state machines | `10-architecture/domain-model.md` |
| Supplier feeds, order routing, contracts | `10-architecture/api-contracts/README.md` |
| "Why did we choose X" | `60-decisions/` (see index below) |
| Magento multistore, MSI, indexers, GraphQL security | `20-backend/README.md` |
| Tenancy, design system, rendering, SEO | `30-frontend/README.md` |
| Environments, CI/CD, hosting, monitoring, Claude tooling | `40-devops/README.md` |
| Doing an operational procedure | `50-runbooks/` |
| A specific storefront's niche, suppliers, pricing, SEO | `70-tenants/<slug>.md` |
| Reconstructing why something was once true | `60-decisions/` first, `90-archive/` only if needed |
| Writing a new feature spec | `00-product/prd/TEMPLATE.md` then `10-architecture/tech-spec/TEMPLATE.md` |
| Recording a decision | `60-decisions/TEMPLATE.md` |

## Decision index
| ADR | Title | Status |
|---|---|---|
| 0001 | Storefront stack | Accepted |
| 0002 | Storefront deployment model | Accepted |
| 0003 | Hosting platform | Proposed (PoC-gated) |
| 0004 | Documentation system | Accepted |
| 0005 | Catalog data layer - PIM or Magento-native | Proposed - BLOCKING |
| 0006 | Product identity model - canonical product with supplier offers | Accepted |
| 0007 | Compliance role in the supply chain - distributor only | Accepted |

## Documentation health
Living docs carry no history; `60-decisions/` is the history; git is the version record. Retirement rules and the hygiene checklist are in `CONVENTIONS.md`. Run `python3 scripts/docs-check.py` at every phase gate — it also runs in CI on push, PR and weekly.

## Project invariants
Facts that must not be violated by any design. Changing one requires a new ADR.
- INV-01 One Magento 2 Open Source instance serves all websites. No second Magento instance.
- INV-02 Storefronts are headless; Magento renders no customer-facing HTML.
- INV-03 Every state transition in the value chain is writable by an API or event, never only by a human in a UI. See `00-product/automation-charter.md`.
- INV-04 First-party sales only. No third-party sellers transact on the storefronts. The operator is the merchant of record on every order.
- INV-05 Dropshipping. No owned warehouse, no owned stock. All physical inventory is held by suppliers and shipped by them.
- INV-06 Greenfield. The system has no dependency on, and no integration with, any pre-existing PIM or ERP. Every capability is built inside this system's boundary.
- INV-07 No proprietary vendor runtime in the critical path.
- INV-08 Priority order for platform decisions: infrastructure cost > Core Web Vitals/SEO > maintenance effort > time-to-launch of a new storefront.
- INV-09 The system never displays availability it cannot source. Stock and price freshness are correctness requirements, not optimisations.
- INV-10 The operator is a distributor under GPSR, never an importer and never a manufacturer. Every supplier must have already placed the goods on the EU market. See ADR-0007.
- INV-11 No own brand, no private label, no rebranding of supplier goods. Applying own branding would reclassify the operator as manufacturer. See ADR-0007.
