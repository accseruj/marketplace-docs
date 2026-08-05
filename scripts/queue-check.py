#!/usr/bin/env python3
"""Work-queue checks. Run from the docs repo root: python3 scripts/queue-check.py

Enforces 40-devops/work-queue-spec.md:
  WQ-C1  every epic, and every issue with a parent, carries exactly one layer
         label, and no issue carries a label outside the WQ-04 vocabulary (error)
  WQ-C2  every roadmap phase has a matching phase epic (error)
  WQ-C3  every open issue has required sections in its description (error)
  WQ-C4  every open issue named in a commit subject (warning)
Reads .beads/issues.jsonl, which is tracked in git. Never invokes bd: CI
installs Python only, and a check that shells out to a missing binary is a
green tick with nothing behind it.
Exit code 1 on errors; warnings do not affect exit code.
"""
import argparse, json, pathlib, re, subprocess, sys

LAYERS = frozenset({"infrastructure", "frontend", "backend",
                    "catalog", "feeds", "sourcing", "product"})

def load_issues(root):
    path = root / ".beads" / "issues.jsonl"
    if not path.exists():
        # Returning [] here made every check vacuous: a mistyped --root printed
        # "checked 0 issues / ok" and exited 0, which is the green tick with
        # nothing behind it this design rejects. The absent file is the failure.
        sys.exit(f"queue-check: no export at {path}\n"
                 "  Run `bd export -o .beads/issues.jsonl`, or point --root at the docs repo root.")
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out

def parent_of(issue):
    # The export carries no parent field; the link is a dependency row.
    # Reading the dot in the id would work today and break the day an id
    # legitimately contains one.
    for dep in issue.get("dependencies") or []:
        if dep.get("type") == "parent-child" and dep.get("issue_id") == issue.get("id"):
            return dep.get("depends_on_id")
    return None

def check_layers(issues):
    errors = []
    for i in issues:
        if i.get("status") == "closed":
            continue
        labels = i.get("labels") or []
        # WQ-04 says the layer is the only label axis and that an epic carries
        # only its layer label. Both were prose with no instrument until this
        # line: a second axis could have been introduced without anything
        # saying so, and an off-vocabulary label on an epic propagates to every
        # child created under it.
        outside = sorted(set(labels) - LAYERS)
        if outside:
            errors.append(f"WQ-C1 {i['id']}: carries labels outside the WQ-04 vocabulary {outside}")
        # An epic is judged on its own label rather than on a parent it does not
        # have. WQ-04 puts the layer on the epic, so an unlabelled epic is the
        # violation the rule exists to catch; skipping every parentless issue
        # left WQ-C1's own stated falsifier unable to fire.
        if i.get("issue_type") != "epic" and parent_of(i) is None:
            continue
        found = sorted(set(labels) & LAYERS)
        if len(found) != 1:
            why = "is an epic" if i.get("issue_type") == "epic" else "has a parent"
            errors.append(f"WQ-C1 {i['id']}: {why} but carries {len(found)} layer labels {found}")
    return errors

# Mirrors `bd lint`'s requirements rather than calling it. Four lines of
# duplication buys a check that runs where bd is not installed.
REQUIRED_SECTIONS = {
    "task": ["Acceptance Criteria"],
    "feature": ["Acceptance Criteria"],
    "bug": ["Steps to Reproduce", "Acceptance Criteria"],
    "epic": ["Success Criteria"],
}

def check_sections(issues):
    errors = []
    for i in issues:
        if i.get("status") == "closed":
            continue
        body = i.get("description") or ""
        for section in REQUIRED_SECTIONS.get(i.get("issue_type", ""), []):
            # The section must open a line, as Task 5 writes it. A bare
            # substring match passes on "no acceptance criteria yet, TBD",
            # which is the state the check exists to catch.
            if not re.search(rf"^\s*{re.escape(section)}\s*:", body, re.M | re.I):
                errors.append(f"WQ-C3 {i['id']}: {i.get('issue_type')} is missing section '{section}'")
    return errors

def phase_headings(roadmap_text):
    names = []
    for line in roadmap_text.splitlines():
        m = re.match(r"^##\s+(Phase\s.+?)\s*$", line)
        if m:
            names.append(re.sub(r"\s*\(current\)\s*$", "", m.group(1)))
    return names

def check_phases(issues, roadmap_text):
    wanted = phase_headings(roadmap_text)
    have = {i["title"].strip() for i in issues
            if i.get("issue_type") == "epic" and i.get("title", "").startswith("Phase ")}
    errors = []
    for name in wanted:
        if name not in have:
            errors.append(f"WQ-C2 roadmap phase {name!r} has no epic with that exact title")
    for title in sorted(have - set(wanted)):
        errors.append(f"WQ-C2 phase epic {title!r} matches no roadmap heading")
    return errors

def commit_subjects(root, subjects_file):
    if subjects_file:
        return pathlib.Path(subjects_file).read_text(encoding="utf-8").splitlines()
    try:
        out = subprocess.run(["git", "-C", str(root), "log", "--format=%s"],
                             capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []          # no git history reachable: nothing to check, not an error
    return out.stdout.splitlines()

def check_orphans(issues, subjects):
    open_ids = {i["id"] for i in issues if i.get("status") != "closed"}
    errors = []
    for subject in subjects:
        for ref in re.findall(r"\(([a-z0-9]+-[a-z0-9.]+)\)", subject):
            if ref in open_ids:
                errors.append(f"WQ-C4 {ref}: named in a commit subject but still open - {subject[:60]!r}")
    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument("--subjects-file", default=None)
    args = ap.parse_args()
    root = pathlib.Path(args.root)

    issues = load_issues(root)
    subjects = commit_subjects(root, args.subjects_file)
    roadmap = root / "00-product" / "roadmap.md"
    roadmap_text = roadmap.read_text(encoding="utf-8") if roadmap.exists() else ""
    errors = check_layers(issues) + check_sections(issues) + check_phases(issues, roadmap_text)
    warnings = check_orphans(issues, subjects)

    print(f"checked {len(issues)} issues\n")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print("  " + e)
        print()
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print("  " + w)
        print()
    print("ok" if not errors else "FAILED")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
