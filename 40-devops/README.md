---
doc: devops-index
purpose: Environments, CI/CD, hosting, monitoring, and the Claude Code tooling setup.
read_when: infrastructure, deployment or tooling work
status: draft
updated: 2026-08-03
related: [60-decisions/ADR-0003-hosting-platform.md]
---

# DevOps

## Environments
- Local: Windows host + WSL (Ubuntu), everything in Docker, repos under `~/work/`.
- TODO(human): decide staging topology - shared staging Magento or per-branch preview?
- Production: Magento on a dedicated server; storefront on Cloudflare Workers (ADR-0003, PoC-gated).

## Hosting decisions
- Storefront: Cloudflare Workers via `@opennextjs/cloudflare`. No egress cost, static assets free.
- Images: self-hosted imgproxy behind the Cloudflare CDN. Explicitly not a per-transform vendor service.
- Fallback if the Worker path fails PoC: self-hosted Node on Hetzner + Coolify or Dokploy.

## CI/CD
- Turborepo remote cache.
- Pipeline: lint -> typecheck -> unit -> build -> visual regression -> canary tenant -> full rollout.
- TODO(Claude): write the pipeline spec once Phase 0 starts.

## Monitoring
- Required per value-chain stage: one metric that makes failure visible without a human noticing (automation-readiness test #5).
- Alerts link directly to a runbook in `50-runbooks/`.

## Claude Code setup
Skills to author in Phase -1 (these carry project conventions; they matter more than agents):
- `magento-graphql` - resolver patterns, schema conventions, cache tags, complexity limits, security checklist.
- `magento-multistore` - create website/store/store-view, root category, assortment assignment, reindex.
- `storefront-tenant` - add a tenant: layout map, tokens, domain, sitemap/robots, smoke checks.
- `deploy-runbook` - CI, OpenNext deploy, canary, rollback.
- `adr` - write an ADR in the project's MADR format.
- `cwv-audit` - run Lighthouse/CrUX checks, thresholds, common regression causes.

Authored: `session-close` - the four-step procedure in `CONVENTIONS.md`. Lives in `.claude/skills/session-close/` in this repo, symlinked into the workspace root so it loads from where Claude Code is launched.

Hooks:
- `SessionStart` runs `scripts/session-brief.sh`, which prints `bd ready` and the last three commits into the model's context. Wired in `.claude/settings.json` at the workspace root, above this repo. Removes the "where did we stop" round-trip at the start of every session.

Beads JSONL export is enabled in `.beads/config.yaml` (`export.auto: true`, `git-add: true`), writing `.beads/issues.jsonl`. That file is the only copy of the issue graph that git carries; the Dolt database is gitignored. Regenerate with `bd export -o .beads/issues.jsonl`.

Project knowledge on claude.ai: connect this repo via "+" -> GitHub and select only `INDEX.md`, `CONVENTIONS.md`, `00-product/{vision,automation-charter,roadmap,market-selection}.md`, `10-architecture/{domain-model,c4-container}.md`, `60-decisions/*.md`. Refreshing is then one "Sync now" for everything. Never upload individual files - they go stale on the next edit. Everything outside that list is read on demand in Claude Code.

Subagents (context isolation, not roles): `researcher`, `code-reviewer`, `security-auditor`, `test-runner`, `visual-regression`, `magento-log-triage`.

Tools: bash (WSL/Docker/n98-magerun2) + GitHub baseline; Playwright and Cloudflare added when the phase needs them. Every added MCP server costs context before the first call.

Project tracking: beads (`bd`), database in this repo under `.beads/` (ADR-0008). Each issue links its PRD or ADR. GitHub Issues and Projects are not used. Issues sync with `bd dolt push`, not with `git push`.
