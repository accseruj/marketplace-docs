#!/usr/bin/env python3
"""Docs hygiene check. Run from the docs repo root: python3 scripts/docs-check.py

Enforces the rules in CONVENTIONS.md:
  - every .md file has well-formed frontmatter with the required keys
  - every file is reachable from the INDEX.md routing table (no orphans)
  - no broken relative cross-references
  - reports TODO(...) / OPEN: markers and their file
  - reports living docs whose `updated:` is older than STALE_DAYS
Exit code 1 on structural errors; marker counts are informational.
"""
import re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
STALE_DAYS = 90
REQUIRED = {"doc", "purpose", "read_when", "status", "updated"}
VALID_STATUS = {"draft", "living", "frozen", "superseded"}
EXEMPT = {"README.md", "CLAUDE.md", "CLAUDE.template.md", "INDEX.md", "CONVENTIONS.md"}

errors, warnings, markers = [], [], []

def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm

SKIP_DIRS = {".git", ".github"}
md_files = sorted(p for p in ROOT.rglob("*.md") if not SKIP_DIRS & set(p.parts))
index_text = (ROOT / "INDEX.md").read_text(encoding="utf-8")

for p in md_files:
    rel = p.relative_to(ROOT).as_posix()
    text = p.read_text(encoding="utf-8")

    # 1. frontmatter
    if p.name != "README.md" or p.parent != ROOT:
        fm = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: missing frontmatter")
        else:
            missing = REQUIRED - fm.keys()
            if missing:
                errors.append(f"{rel}: frontmatter missing keys: {sorted(missing)}")
            status = fm.get("status", "")
            if status and status not in VALID_STATUS:
                errors.append(f"{rel}: invalid status '{status}'")
            upd = fm.get("updated", "")
            if re.match(r"^\d{4}-\d{2}-\d{2}$", upd):
                age = (datetime.date.today() - datetime.date.fromisoformat(upd)).days
                if status == "living" and age > STALE_DAYS:
                    warnings.append(f"{rel}: living doc not reviewed in {age} days")
            elif upd and "YYYY" not in upd:
                errors.append(f"{rel}: updated is not YYYY-MM-DD ({upd!r})")

    # 2. orphan check
    if rel not in EXEMPT and "TEMPLATE" not in p.name and "90-archive" not in rel:
        directory = p.parent.relative_to(ROOT).as_posix()
        if rel not in index_text and f"{directory}/" not in index_text:
            errors.append(f"{rel}: not reachable from the INDEX.md routing table")

    # 3. broken relative links
    # skipped: CLAUDE.template.md (paths are relative to a code repo, not here)
    # skipped: sections listing files that are planned but not yet written
    if rel != "CLAUDE.template.md":
        body, skip = [], False
        for line in text.splitlines():
            if line.startswith("##"):
                skip = "planned" in line.lower()
            if not skip:
                body.append(line)
        for target in re.findall(r"`([0-9a-zA-Z][\w/\-.]*\.md)`", "\n".join(body)):
            if "TEMPLATE" in target or "<" in target:
                continue
            if not (ROOT / target).exists() and not (p.parent / target).exists():
                errors.append(f"{rel}: broken reference -> {target}")

    # 4. markers
    for i, line in enumerate(text.splitlines(), 1):
        if "TODO(" in line or "OPEN:" in line:
            markers.append(f"{rel}:{i}: {line.strip()[:100]}")

print(f"checked {len(md_files)} files\n")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors: print("  " + e)
    print()
if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings: print("  " + w)
    print()
print(f"OPEN DECISIONS ({len(markers)}):")
for m in markers: print("  " + m)
print()
print("ok" if not errors else "FAILED")
sys.exit(1 if errors else 0)
