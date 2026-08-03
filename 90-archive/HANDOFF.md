---
doc: archived-setup-handoff
purpose: Original workspace setup instructions and the first Phase -1 work queue. Retired.
read_when: rarely - reconstructing how the workspace was originally set up
status: superseded
updated: 2026-08-03
---

ARCHIVED: 2026-08-03. Reason: carried a second Phase -1 work queue that drifted out of sync with the real one, and setup steps that are now done. Superseded by: `00-product/roadmap.md` for the queue, `10-architecture/c4-container.md` for the repo table, `40-devops/README.md` for the project-knowledge sync, and `CONVENTIONS.md` section "Session close" for the rule that there is exactly one queue.

# Handoff — setup and first work queue

## What's here
- `docs/` — the documentation skeleton. This becomes its own git repo.
- `claude-project-instructions.md` — paste into the new Claude Project's custom instructions.

## Fast path
```bash
cd <where you unpacked this>
bash setup.sh ~/projects/marketplace
```
Copies `docs/` into place, initialises git, runs the hygiene check, and prints the manual steps that follow. Idempotent.

The rest of this file explains what the script does and what it cannot do.

## Unpacking note
The download archive contains an `mnt/user-data/outputs/` wrapper — that's the container path the files were produced in, not part of the structure. Flatten it so that `docs/` sits at the top:

```bash
cd ~/projects/marketplace
mv docs/mnt/user-data/outputs/docs docs.tmp
mv docs/mnt/user-data/outputs/*.md .
rm -rf docs
mv docs.tmp docs
ls docs        # should show INDEX.md, CONVENTIONS.md, 00-product, 10-architecture, ...
```

(Also note the directory is currently spelled `makretplace` — worth renaming to `marketplace` before anything references it.)

## Repositories
This project is greenfield. It shares no repository with the previous system.

| Repo | Contains |
|---|---|
| `docs` | This documentation. Single source of truth. |
| `commerce` | Magento 2 Open Source instance, custom modules |
| `storefront` | Next.js monorepo — `apps/storefront`, `packages/ui`, `packages/config`, `packages/magento-client`, `packages/seo` |
| `infra` | Docker, CI, Cloudflare/OpenNext config, imgproxy, monitoring |
| catalog layer / order routing | Repo shape depends on ADR-0005 and ADR-0006. Do not create these yet. |

## Setup steps
1. `cd ~/projects/marketplace/docs && git init`, commit, push to GitHub (private).
2. Create the empty `commerce`, `storefront`, `infra` repos when their phase starts — not before.
3. In each code repo, copy `docs/CLAUDE.template.md` to `CLAUDE.md` and fill the placeholders. Point it at the docs repo (git submodule, or a sibling clone).
4. Create the Claude Project, paste `claude-project-instructions.md` into Instructions, and connect the `docs` GitHub repo to project knowledge (see below).
5. Create a GitHub Project board: Backlog / Shaping / Doing (WIP=1) / Review / Done.

## Keeping project knowledge current
Do not upload individual markdown files — they go stale the moment you edit them. Instead, in the project's knowledge section use "+" → GitHub, connect the `docs` repo, and select only the foundation files:

```
INDEX.md
CONVENTIONS.md
00-product/vision.md
00-product/automation-charter.md
00-product/roadmap.md
10-architecture/domain-model.md
10-architecture/c4-container.md
60-decisions/*.md
```

Refreshing is then one "Sync now" click for everything, instead of delete-and-reupload per file. Sync before starting any significant chat. Everything not in that list stays in git and is read on demand in Claude Code.

## Immediate work queue (Phase -1)
Ordered by how much they unblock. Nothing else should start before these.

1. **Answer the supplier-reality questions** in `docs/00-product/vision.md`: how many suppliers at launch, which channels (API/EDI/SFTP/email), do they supply reliable GTIN/EAN/MPN, batch or real-time stock. These are the inputs the two blocking ADRs need.
2. **Decide ADR-0006 — product identity model.** One shopper-visible product backed by many supplier offers, or one listing per supplier item? Determines matching, pricing, stock computation, sourcing, order splitting and returns.
3. **Decide ADR-0005 — catalog data layer.** Magento-native modules, or a dedicated service that projects into Magento? Coupled to ADR-0006; decide them together.
4. **Returns policy.** A commercial decision that blocks the returns design in a model with no warehouse.
5. **Domain model state machines** — transition tables, allowed actors, event per transition.
6. **Reservation strategy** — cart, checkout, or PO acknowledgement. The main oversell lever.
7. **Fill `10-architecture/api-contracts/`** — the two supplier contracts first.
8. **Backend sizing inputs** — SKU count per supplier, expected traffic per tenant.
9. **PRD for the flagship storefront.**
10. **Author the six Claude Code skills** listed in `docs/40-devops/README.md`.

## What was deliberately left as TODO/OPEN
The skeleton marks unknowns explicitly rather than guessing. Every `TODO(human)` needs your input; every `TODO(Claude)` I can draft once its inputs exist; every `OPEN` is a question that needs a decision.

```bash
grep -rn "TODO(\|OPEN:" docs/
```
