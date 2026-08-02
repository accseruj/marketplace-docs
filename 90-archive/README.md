---
doc: archive-index
purpose: Where retired documents go. Read only when reconstructing history.
read_when: rarely - only when reconstructing why something was once true
status: living
updated: 2026-08-02
---

# Archive

Documents that describe components, processes or plans that no longer exist. Moved here, never deleted.

## Rules
- Every archived file keeps its original content and gains a header block:
  `ARCHIVED: YYYY-MM-DD. Reason: <one line>. Superseded by: <path or ADR-nnnn>.`
- Its frontmatter `status` becomes `superseded`.
- Archived files are removed from the `INDEX.md` routing table.
- Nothing here is authoritative. Never answer a current question from an archived file.

## What does NOT belong here
- ADRs. A rejected or superseded ADR stays in `60-decisions/` with an updated status and a link to its replacement. The ADR chain is the primary decision history; the archive is only for whole documents that lost their subject.
- Old versions of living docs. Git history is the version record - do not keep `-v2` files.
