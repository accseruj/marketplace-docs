---
doc: index
purpose: Routing table. Read this first in every session; it says which files to open for a given task.
read_when: always, at session start
status: living
updated: 2026-08-04
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
| What the project believes but has not tested, and how each would be disproved | `00-product/assumptions.md` |
| What to work on next | `bd ready` (ADR-0008). Not a file. |
| Phases and exit gates | `00-product/roadmap.md` |
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
| Dispositioning the 2026-08-04 foundational audit | `audit-2026-08-04.md`. Temporary; retire to `90-archive/` once every finding is dispositioned. |

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
| 0008 | Work tracking - beads, replacing GitHub Issues and Projects | Accepted |

## Documentation health
Living docs carry no history; `60-decisions/` is the history; git is the version record. Retirement rules and the hygiene checklist are in `CONVENTIONS.md`. Run `python3 scripts/docs-check.py` at every phase gate — it also runs in CI on push, PR and weekly.

## Project invariants
Constraints the project chose and will not violate. Changing one requires a new ADR. Each names where it was derived; an invariant with no derivation is an assumption in disguise and belongs in `00-product/assumptions.md`. These are commitments, not empirical claims - they cannot be falsified, only abandoned, so each carries a revisit trigger rather than a test. See `CONVENTIONS.md`, "Every asserted claim names its falsifier".
- INV-02 Storefronts are headless; Magento renders no customer-facing HTML. Derived in ADR-0001.
- INV-03 Every state transition in the value chain is writable by an API or event, never only by a human in a UI. Derived in `00-product/automation-charter.md` - readiness test #3 and anti-pattern #1. OPEN: the charter is a living doc, so this derivation can move without an ADR; decide whether that is acceptable.
- INV-04 First-party sales only. No third-party sellers transact on the storefronts. The operator is the merchant of record on every order. Derived in `00-product/vision.md` business model; cited by ADR-0007, which depends on it for the GPSR role. Revisit trigger: a decision to onboard third-party sellers, which would reopen ADR-0007 entirely.
- INV-05 Dropshipping. No owned warehouse, no owned stock. All physical inventory is held by suppliers and shipped by them. Derived in `00-product/vision.md` business model; cited by ADR-0001, ADR-0003 and ADR-0007. Revisit trigger: acquiring stock or 3PL fulfilment, currently out of scope.
- INV-06 Greenfield. The system has no dependency on, and no integration with, any pre-existing PIM or ERP. Every capability is built inside this system's boundary. Derived in `00-product/vision.md`; it is what forces ADR-0005 to exist. Revisit trigger: acquiring or inheriting a system that already owns catalog data.
- INV-07 No proprietary vendor runtime in the critical path. Its derivation exists - ADR-0001's options table rejects Vue Storefront and Front-Commerce on exactly this ground, and ADR-0003 cites it in consequences - but all three sites label it INV-05 by mistake. Correcting that label is what completes the derivation; blocked on `bd` issue docs-cn2, since both ADRs are frozen.
- INV-09 The system never displays availability it cannot source. Stock and price freshness are correctness requirements, not optimisations. Derived from the oversell risk in `00-product/vision.md`; cited by ADR-0005 and ADR-0006. Revisit trigger: none foreseen - abandoning it means accepting oversell as normal, which SC-06 forbids.
- INV-10 The operator is a distributor under GPSR, never an importer and never a manufacturer. Every supplier must have already placed the goods on the EU market. See ADR-0007.
- INV-11 No own brand, no private label, no rebranding of supplier goods. Applying own branding would reclassify the operator as manufacturer. See ADR-0007.

Retired from this list on 2026-08-04, having been asserted rather than derived. Both are now in `00-product/assumptions.md` with the test that would disprove them.
- INV-01 -> ASM-01, one Magento instance for all websites. An unmeasured capacity bet.
- INV-08 -> ASM-02, the platform priority order. No derivation, and its second term depends on ASM-03.
