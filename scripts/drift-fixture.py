#!/usr/bin/env python3
"""Build a throwaway copy of the corpus with known drift injected.

Usage: python3 scripts/drift-fixture.py <target_dir>

Prints one EXPECT line per injected defect, then a NOISE manifest naming every
class of false positive the copy knowingly contains. The drift auditor is run
against the copy and must report every EXPECT line. A pair with no injection
here is uncovered, and the agent's instructions say so rather than implying
coverage.

This script deletes its target directory. Every guard on that deletion is in
`check_target` and in the SENTINEL rule below; read both before changing either.
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Written into the target after copying, and required before any rmtree. A
# directory without it was not built by this script, so this script does not
# get to delete it. The path guards below are a list of shapes someone thought
# of; this one is a positive proof of ownership and does not depend on that
# list being complete.
SENTINEL = ".drift-fixture"


# Never copied into a fixture, and why. The reason is data: an entry without
# one cannot be added.
#   dot-prefixed names - tooling, not corpus. `.superpowers/` holds the SDD
#                        briefs, which name every injection in plain text.
#   __pycache__        - build artefact.
#   ANSWER_KEY         - the two drift-audit documents quote this file's source
#                        verbatim, so copying them hands the agent under test
#                        its own answers. Excluding them costs nothing: a
#                        fixture run grades the agent, it does not audit the
#                        corpus.
ANSWER_KEY = {
    "40-devops/drift-audit-plan.md",
    "40-devops/drift-audit-spec.md",
    "scripts/drift-fixture.py",
    "scripts/tests/test-drift-fixture.sh",
}


def _ignore(directory, names):
    root = ROOT.resolve()
    here = pathlib.Path(directory).resolve()
    ignored = set()
    for name in names:
        if name.startswith(".") or name == "__pycache__":
            ignored.add(name)
            continue
        rel_path = (here / name).relative_to(root).as_posix()
        if rel_path in ANSWER_KEY:
            ignored.add(name)
        if re.fullmatch(r"audit-\d{4}-\d{2}-\d{2}\.md", name) and here == root:
            ignored.add(name)
    return ignored


def check_target(target):
    """Refuse any target whose deletion would destroy something that is not a fixture.

    The first version refused descendants of the corpus only. `..` from the
    docs root is an ancestor, reached `shutil.rmtree`, and would have deleted
    the whole workspace including the workspace-root `.claude/` symlinks - and
    `..` is the exact path shape used elsewhere in this repo. Refuse in both
    directions, plus the two other shapes a typo produces.
    """
    resolved = target.resolve()
    root = ROOT.resolve()
    if resolved == root or root in resolved.parents:
        sys.exit(f"refusing to build a fixture inside the corpus: {resolved}")
    if resolved in root.parents:
        sys.exit(f"refusing: {resolved} contains the corpus, and building here deletes it")
    if resolved == pathlib.Path.home().resolve():
        sys.exit(f"refusing to build a fixture over the home directory: {resolved}")
    if resolved == pathlib.Path(resolved.anchor):
        sys.exit(f"refusing to build a fixture over the filesystem root: {resolved}")
    return resolved


def clear_target(resolved):
    """Delete a previous fixture. Anything without the sentinel is not one."""
    if not resolved.exists():
        return
    if not resolved.is_dir():
        sys.exit(f"refusing to delete {resolved}: not a directory")
    if not (resolved / SENTINEL).exists():
        sys.exit(
            f"refusing to delete {resolved}: no {SENTINEL} sentinel, so this "
            "directory was not built by drift-fixture.py. Pick an empty target "
            "or remove it by hand."
        )
    shutil.rmtree(resolved)


def inject(path, old, new, pair, description):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        sys.exit(f"fixture is stale: anchor not found in {path.name}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"EXPECT {pair} {path.name} {description}")


# Strings that only exist in the corpus because this fixture put them there.
# If one is readable anywhere except the file it was injected into, the copy
# hands the agent under test an answer it did not have to find.
# PR-4 has no entry: its injected value is `status: draft`, which legitimately
# occurs throughout the corpus. That pair is not covered by this check, and
# saying so is the point - an uncovered case named is not the same as a
# covered one.
LEAK_NEEDLES = {
    "prints the current phase's item 1": "40-devops/README.md",
    "INV-99": "60-decisions/ADR-0001-storefront-stack.md",
    "Every table must be alphabetised": "CONVENTIONS.md",
}


def assert_no_leak(target):
    problems = []
    for needle, injected_into in LEAK_NEEDLES.items():
        for path in sorted(target.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(target).as_posix()
            if rel == injected_into:
                continue
            try:
                if needle in path.read_text(encoding="utf-8"):
                    problems.append(f"{needle!r} is readable in {rel}")
            except (UnicodeDecodeError, OSError):
                continue
    if problems:
        sys.exit("fixture leaks its own answers:\n  " + "\n  ".join(problems))


# Prose references to files the copy excludes. Excluding a file does not remove
# the sentence pointing at it. Anchored rather than pattern-matched: a stale
# anchor exits loudly, and there is exactly one of these.
PROSE_REPAIRS = (
    (
        "40-devops/README.md",
        ", see `40-devops/drift-audit-spec.md`",
        "",
        "prose reference to the excluded spec",
    ),
)


def repair_references(target):
    """Remove references the copy cannot resolve, and return what was removed.

    `docs-check.py` run inside an unrepaired fixture exits 1 on four broken
    references, because `INDEX.md` still routes to the three excluded
    documents. A reader of that run cannot tell a fixture artefact from an
    agent regression. Repairing the routing is simpler and more honest than
    copying the answer key and redacting it: those files are genuinely not in
    the copy, so the copy should not claim they are.

    Table rows are matched by rule, not by anchor, so a new audit report or a
    new routing row does not silently stale this function.
    """
    removed = []
    index = target / "INDEX.md"
    kept = []
    for line in index.read_text(encoding="utf-8").splitlines(keepends=True):
        refs = re.findall(r"`([0-9a-zA-Z][\w/\-.]*\.md)`", line)
        dangling = [r for r in refs if not (target / r).exists()]
        if line.startswith("|") and dangling:
            removed.append(f"INDEX.md: routing row for {', '.join(dangling)}")
            continue
        kept.append(line)
    index.write_text("".join(kept), encoding="utf-8")

    for rel, old, new, why in PROSE_REPAIRS:
        path = target / rel
        text = path.read_text(encoding="utf-8")
        if old not in text:
            sys.exit(f"fixture is stale: repair anchor not found in {rel}: {old!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        removed.append(f"{rel}: {why}")
    return removed


# False positives this fixture knowingly manufactures. Excluding a directory
# does not delete the sentences describing it, so the copy asserts mechanisms
# that are not in the copy. Declared so a reader of a fixture run can tell a
# fixture artefact from an agent regression. Counted against the copy at run
# time rather than written down: a hardcoded count is the failure mode this
# repository has measured, see the spec's "Why this exists".
NOISE_CLASSES = (
    (
        "tooling-not-copied",
        re.compile(r"\.github/|\.beads/|\.claude/|\.superpowers/|SessionStart|issues\.jsonl"),
        "dot-directories are excluded as tooling, so every sentence describing a workflow, "
        "a hook, an agent, a skill or the beads export has nothing in the copy to check "
        "against. A PR-1 finding of the form 'described but the mechanism is absent' is a "
        "fixture artefact.",
    ),
    (
        "answer-key-not-copied",
        re.compile(r"drift.audit|drift.fixture|AUD-\d+"),
        "the drift-audit spec and plan, this script, its test, and the audit report are "
        "excluded because they name every injection. Sentences citing them, and every "
        "AUD-nn id the report defines, resolve to nothing in the copy. A PR-3 finding on "
        "those ids is a fixture artefact.",
    ),
)


def print_noise_manifest(target, repaired):
    for name, pattern, reason in NOISE_CLASSES:
        hits = {}
        for path in sorted(target.rglob("*.md")):
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            count = sum(1 for line in lines if pattern.search(line))
            if count:
                hits[path.relative_to(target).as_posix()] = count
        print(f"NOISE {name} {sum(hits.values())} line(s) in {len(hits)} file(s) - {reason}")
        for rel, count in sorted(hits.items()):
            print(f"NOISE   {rel}: {count}")
    print(
        f"NOISE repaired-routing {len(repaired)} reference(s) removed - the copy's routing "
        "table is not the corpus's. Removed rather than left dangling so docs-check.py "
        "inside the copy stays clean; a doc-vs-doc finding about a missing routing row is "
        "a fixture artefact."
    )
    for item in repaired:
        print(f"NOISE   {item}")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: drift-fixture.py <target_dir>")
    target = pathlib.Path(sys.argv[1])
    resolved = check_target(target)
    clear_target(resolved)
    shutil.copytree(ROOT, target, ignore=_ignore)
    (target / SENTINEL).write_text(
        "Built by scripts/drift-fixture.py. Deleting this file makes the fixture "
        "undeletable by that script, which is the point.\n",
        encoding="utf-8",
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

    repaired = repair_references(target)
    assert_no_leak(target)
    print_noise_manifest(target, repaired)


if __name__ == "__main__":
    main()
