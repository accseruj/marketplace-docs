# docs — single source of truth

This repository is the memory of the project. Claude has no memory between sessions; these files are that memory.

- Entry point for any session: `INDEX.md`
- Format rules: `CONVENTIONS.md`
- Docs are written in English, deliberately, for token efficiency and terminology consistency.

Layout:
```
00-product/       why and what
10-architecture/  how, at system level
20-backend/       Magento 2 + integrations
30-frontend/      storefront platform
40-devops/        environments, CI/CD, hosting
50-runbooks/      operational procedures
60-decisions/     ADRs — frozen, append-only
```

Also here:
```
scripts/docs-check.py   hygiene check — frontmatter, orphans, broken links, TODO/OPEN inventory
scripts/tests/          test suites for the scripts, run in CI
.github/workflows/      runs the hygiene check and both test suites on push, PR, and weekly
.github/pull_request_template.md
```

Run the check any time: `python3 scripts/docs-check.py`

Attach this repo to code repos as a git submodule, or clone alongside and point each repo's `CLAUDE.md` at it.
