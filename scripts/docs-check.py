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

# .claude holds Claude Code skills and settings. They are tooling config, not
# documentation: their frontmatter follows the agent-skill schema, not this
# repo's, and they are reached by the agent runtime rather than by INDEX.md.
SKIP_DIRS = {".git", ".github", ".claude", ".beads"}

# Files whose .md references are legitimately allowed to dangle.
# The reason is data, not a comment: an entry without one cannot be added.
# A list that keeps growing means the check models the corpus wrongly - see
# the doc_class proposal in bd issue docs-8gf.
NO_LINK_CHECK = {
    r"CLAUDE\.template\.md": "paths are relative to a code repo, not to this one",
    r"90-archive/.*": "retired files keep their original content by rule, so their links point at a world that no longer exists",
    r"audit-\d{4}-\d{2}-\d{2}\.md": "an audit names the files it proposes creating, which by definition do not exist yet",
}
for _pat, _reason in NO_LINK_CHECK.items():
    if not _reason.strip():
        raise SystemExit(f"docs-check: link-check exemption {_pat!r} has no reason")

def link_check_exempt(rel):
    return any(re.fullmatch(pat, rel) for pat in NO_LINK_CHECK)

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
    # exemptions and their reasons are in NO_LINK_CHECK above
    # also skipped: sections listing files that are planned but not yet written
    if not link_check_exempt(rel):
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

# 5. every invariant carries a derivation, every assumption a falsifier with a
#    threshold. CONVENTIONS: "Every asserted claim names its falsifier".
#    Warnings, not errors: a gap flagged as TODO(human) is the established way
#    to own an unanswered question here, and a permanently red check trains
#    people to ignore it. What this catches is the gap nobody marked.
#    Scan only the declaration list, not the retirement pointers that follow it -
#    "- INV-01 -> ASM-01" records a demotion, it does not assert a constraint.
inv_section = index_text.split("## Project invariants", 1)[-1].split("\nRetired from this list", 1)[0]
inv_line = re.compile(r"^- (INV-\d+) (.+)$", re.M)
for m in inv_line.finditer(inv_section):
    inv, body = m.group(1), m.group(2)
    if not re.search(r"Derived|derivation|See ADR-\d+", body):
        errors.append(f"INDEX.md: {inv} states a constraint with no derivation")
    if not re.search(r"[Rr]evisit trigger", body) and "ADR-" not in body:
        warnings.append(f"INDEX.md: {inv} names no revisit trigger")

asm_path = ROOT / "00-product" / "assumptions.md"
if asm_path.exists():
    asm_text = asm_path.read_text(encoding="utf-8")
    for block in re.split(r"^## ", asm_text, flags=re.M)[1:]:
        head = block.splitlines()[0].strip()
        aid = head.split(" ")[0]
        if not aid.startswith("ASM-"):
            continue
        falsifiers = [l for l in block.splitlines() if re.search(r"[Ff]alsifier", l)]
        if not falsifiers:
            errors.append(f"assumptions.md: {aid} has no falsifier line")
            continue
        for l in falsifiers:
            if re.search(r"TODO\(|none exists|no threshold|Incomplete", l):
                warnings.append(f"assumptions.md: {aid} falsifier is incomplete - {l.strip()[:90]}")

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
