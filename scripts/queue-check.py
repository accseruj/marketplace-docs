#!/usr/bin/env python3
"""Work-queue checks. Run from the docs repo root: python3 scripts/queue-check.py

Enforces 40-devops/work-queue-spec.md:
  WQ-C1  every issue with a parent carries exactly one layer label
Reads .beads/issues.jsonl, which is tracked in git. Never invokes bd: CI
installs Python only, and a check that shells out to a missing binary is a
green tick with nothing behind it.
Exit code 1 on any error.
"""
import argparse, json, pathlib, sys

LAYERS = frozenset({"infrastructure", "frontend", "backend",
                    "catalog", "feeds", "sourcing", "product"})

def load_issues(root):
    path = root / ".beads" / "issues.jsonl"
    if not path.exists():
        return []
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
        if i.get("status") == "closed" or parent_of(i) is None:
            continue
        found = sorted(set(i.get("labels") or []) & LAYERS)
        if len(found) != 1:
            errors.append(f"WQ-C1 {i['id']}: has a parent but carries {len(found)} layer labels {found}")
    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument("--subjects-file", default=None)
    args = ap.parse_args()
    root = pathlib.Path(args.root)

    issues = load_issues(root)
    errors = check_layers(issues)

    print(f"checked {len(issues)} issues\n")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print("  " + e)
        print()
    print("ok" if not errors else "FAILED")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
