---
doc: adr-0003
purpose: Where the storefront and its images run.
read_when: questioning hosting or infra cost
status: draft
updated: 2026-08-02
---

# ADR-0003: Cloudflare Workers via OpenNext for the storefront

- Status: proposed - gated on Phase 0 PoC
- Date: 2026-08-02
- Deciders: human
- Related: INV-06, ADR-0002, 00-product/roadmap.md

## Context
Infrastructure cost is priority #1. Twenty storefronts multiply bandwidth, image transforms and function invocations - the three line items that historically dominate managed-platform bills.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Cloudflare Workers + OpenNext | No egress charge; free static assets; low per-request cost; Cloudflare's preferred Next.js path | Worker size limit; CPU-time cost on heavy SSR; adapter feature lag behind Next.js releases |
| Vercel | Best Next.js fidelity | Image optimisation and invocation costs scale badly at 20 tenants; per-seat |
| Netlify | Simple | Credit model, bandwidth cost higher than Cloudflare |
| Self-hosted Node (Hetzner + Coolify/Dokploy) | Predictable flat cost; no lock-in | Ops burden on a single operator |

## Decision
Proposed: Cloudflare Workers via `@opennextjs/cloudflare`, with self-hosted imgproxy behind the Cloudflare CDN for images. Not accepted until the Phase 0 PoC measures bundle size, CPU cost per storefront, and CWV on real catalog pages.

## Consequences
- Positive: lowest expected run cost; no egress billing; no proprietary runtime (INV-05).
- Negative / accepted: dependence on adapter parity with Next.js; must keep the bundle small and dynamic holes minimal.
- Follow-up: PoC in Phase 0; fallback plan to self-hosted Node documented in `40-devops/README.md`.

## Revisit triggers
- OpenNext bundle exceeds the Worker size limit.
- Measured CPU cost per storefront exceeds budget.
- A required Next.js feature is unsupported by the adapter.
