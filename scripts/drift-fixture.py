#!/usr/bin/env python3
"""Build a throwaway copy of the corpus with known drift injected.

Usage: python3 scripts/drift-fixture.py <target_dir>

Prints one EXPECT line per injected defect. The drift auditor is run against
the copy and must report every EXPECT line. A pair with no injection here is
uncovered, and the agent's instructions say so rather than implying coverage.
"""
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def inject(path, old, new, pair, description):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        sys.exit(f"fixture is stale: anchor not found in {path.name}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"EXPECT {pair} {path.name} {description}")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: drift-fixture.py <target_dir>")
    target = pathlib.Path(sys.argv[1])
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(
        ROOT, target,
        ignore=shutil.ignore_patterns(".git", ".beads", "__pycache__"),
    )

    # PR-1 doc vs mechanism: describe session-brief.sh doing what it no longer does
    inject(
        target / "40-devops" / "README.md",
        "which prints `bd ready` and the last three commits",
        "which prints the current phase's item 1 from `00-product/roadmap.md`",
        "PR-1",
        "describes session-brief.sh printing a roadmap item; it prints bd ready",
    )

    # PR-3 ID reference vs definition: cite an invariant that does not exist
    inject(
        target / "60-decisions" / "ADR-0001-storefront-stack.md",
        "- Related: INV-02,",
        "- Related: INV-99, INV-02,",
        "PR-3",
        "cites INV-99, which is defined nowhere",
    )

    # PR-4 status across surfaces: frontmatter contradicts body and INDEX
    inject(
        target / "60-decisions" / "ADR-0001-storefront-stack.md",
        "status: frozen",
        "status: draft",
        "PR-4",
        "frontmatter says draft; body says accepted and INDEX says Accepted",
    )

    # PR-6 rule without instrument: a new rule no check enforces
    inject(
        target / "CONVENTIONS.md",
        "## Docs hygiene pass",
        "## Table ordering\nEvery table must be alphabetised by its first column.\n\n"
        "## Docs hygiene pass",
        "PR-6",
        "adds a rule with no check in docs-check.py and no not-mechanisable note",
    )


if __name__ == "__main__":
    main()
