---
doc: adr-0002
purpose: How the storefront is deployed across 10-20 tenants.
read_when: questioning multi-tenancy or repo structure
status: frozen
updated: 2026-08-02
---

# ADR-0002: Single multi-tenant storefront application

- Status: accepted
- Date: 2026-08-02
- Deciders: human
- Related: ADR-0001, INV-06

## Context
Options for serving 10-20 tenants from a shared component library where layouts and UX flows differ. Single operator; CI cost, dependency drift and onboarding effort all scale with the number of deployed applications.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| (a) Single multi-tenant app, hostname routing | One build; one dependency set; minimal function count; tenant onboarding is a config change (hours) | Blast radius - one bug affects all tenants; cache keys must be tenant-scoped |
| (b) Monorepo, one app per tenant | Full isolation; maximum UX divergence; small blast radius | 20 builds, 20 function sets, 20 dependency sets; onboarding in days; worst on all four priorities |
| (c) Hybrid - one app per layout archetype | Bounded blast radius; good divergence | More moving parts than (a) |

## Decision
Start with (a). Evolve to (c) if and only if specific tenants outgrow layout maps and route overrides.

## Consequences
- Positive: lowest CI and runtime cost; single dependency surface; tenant N+1 is a config entry.
- Negative / accepted: blast radius. Mandatory mitigations - canary deploys, per-tenant feature flags, visual regression gating merges, fast rollback.
- Follow-up: tenant resolution tech spec; cache-key scheme with tenant in the key; visual regression harness.

## Revisit triggers
- Three or more tenants require routing/flow divergence that layout maps and route overrides cannot express.
- A single deploy causes a cross-tenant production incident that mitigations did not contain.
