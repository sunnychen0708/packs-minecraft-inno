#!/usr/bin/env python3
"""Build GitHub Release notes from pack file trees, not commit ancestry.

The repository's history was rewritten in October 2026. Old release tags still
point at the original commits, so merge-base or GitHub-generated PR notes can
include unrelated changes. Direct git diff of the two pack trees works even
when the tags and current main have divergent histories.
"""

from __future__ import annotations

import argparse
import collections
import re
import subprocess
from pathlib import Path

MAX_LISTED_FILES = 80
STATUS_LABELS = {"A": "added", "M": "modified", "D": "removed", "T": "modified"}


def git(*args: str) -> bytes:
    return subprocess.check_output(("git", *args))


def parse_tag(pack: str, tag: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(re.escape(pack) + r"-v(\d+)\.(\d+)(?:\.(\d+))?", tag)
    if not match:
        return None
    return tuple(int(number or "0") for number in match.groups())


def previous_release_tag(pack: str, current_tag: str) -> str | None:
    current_version = parse_tag(pack, current_tag)
    if current_version is None:
        raise ValueError(f"Invalid release tag for {pack}: {current_tag}")
    # ls-remote lists annotated tags twice, with ^{} on the peeled line.
    lines = git("ls-remote", "--tags", "origin", f"refs/tags/{pack}-v*")
    versions: list[tuple[tuple[int, int, int], str]] = []
    for line in lines.decode("utf-8").splitlines():
        ref = line.split("\t", 1)[-1]
        if not ref.startswith("refs/tags/"):
            continue
        name = ref.removeprefix("refs/tags/")
        version = parse_tag(pack, name)
        if version is not None and version < current_version:
            versions.append((version, name))
    return max(versions)[1] if versions else None


def ensure_tag_available(tag: str) -> None:
    local = subprocess.run(
        ("git", "rev-parse", "--verify", "--quiet", f"{tag}^{{commit}}"),
        capture_output=True,
        check=False,
    )
    if local.returncode == 0:
        return
    # Fetch only the previous tag; avoid fetching hundreds of old commits.
    subprocess.run(
        ("git", "fetch", "--no-tags", "--depth=1", "origin",
         f"refs/tags/{tag}:refs/tags/{tag}"),
        check=True,
    )


def changed_pack_files(root: str, previous: str | None) -> list[tuple[str, str]]:
    if previous is None:
        raw = git("ls-tree", "-r", "--name-only", "-z", "HEAD", "--", root)
        return [("A", p.decode("utf-8")) for p in raw.split(b"\0") if p]

    # Do not use merge-base, git log, or GitHub's generated release notes:
    # file trees can be compared directly even across rewritten Git history.
    raw = git("diff", "--no-renames", "--name-status", "-z",
              f"{previous}^{{commit}}", "HEAD", "--", root)
    parts = raw.split(b"\0")
    if parts[-1:] == [b""]:
        parts.pop()
    if len(parts) % 2:
        raise ValueError("Unexpected git diff --name-status -z output")
    changes = []
    for i in range(0, len(parts), 2):
        status = parts[i].decode("ascii")[0]
        path = parts[i + 1].decode("utf-8")
        if status not in STATUS_LABELS:
            raise ValueError(f"Unsupported diff status: {status} for {path}")
        changes.append((status, path))
    return sorted(changes, key=lambda item: item[1])


def render_notes(pack: str, current_tag: str, root: str,
                 previous: str | None, changes: list[tuple[str, str]]) -> str:
    title = (f"## Changes since `{previous}`" if previous
             else "## Initial release")
    lines = [
        title, "",
        f"Compared the actual contents of `{root}/` at "
        + (f"`{previous}` and `{current_tag}`." if previous
           else f"`{current_tag}`."),
        "This comparison does not depend on shared commit history.", "",
    ]
    if not changes:
        lines.append("No pack source files changed compared with the previous release.")
    else:
        counts = collections.Counter(status for status, _ in changes)
        lines.extend([
            f"**Pack files changed: {len(changes)}** "
            f"({counts['A']} added, {counts['M'] + counts['T']} modified, "
            f"{counts['D']} removed).",
            "",
            f"<details><summary>Changed files ({len(changes)})</summary>",
            "",
        ])
        for status, path in changes[:MAX_LISTED_FILES]:
            relative_path = path.removeprefix(root + "/")
            lines.append(f"- `{relative_path.replace(chr(96), '')}` — "
                         f"{STATUS_LABELS[status]}")
        remaining = len(changes) - MAX_LISTED_FILES
        if remaining > 0:
            lines.append(f"- ...and {remaining} more files (included in the counts above).")
        lines.extend(["", "</details>"])
    lines.extend(["", "Release notes list source-file changes, not inferred "
                  "gameplay behavior or PR authors.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", help="Pack directory name")
    parser.add_argument("tag", help="Release tag, e.g. warehouse-v4.8")
    parser.add_argument("output", type=Path, help="Markdown notes output path")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.pack):
        parser.error("Invalid pack name")
    if parse_tag(args.pack, args.tag) is None:
        parser.error("Tag must match pack-vMAJOR.MINOR[.PATCH]")

    if Path("datapacks", args.pack).is_dir():
        root = f"datapacks/{args.pack}"
    elif Path("resourcepacks", args.pack).is_dir():
        root = f"resourcepacks/{args.pack}"
    else:
        parser.error(f"Pack directory not found: {args.pack}")

    previous = previous_release_tag(args.pack, args.tag)
    if previous:
        ensure_tag_available(previous)
    changes = changed_pack_files(root, previous)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_notes(args.pack, args.tag, root, previous, changes),
        encoding="utf-8",
    )
    print(f"Release notes: {previous or '(initial)'} -> {args.tag}; "
          f"{len(changes)} pack files changed")


if __name__ == "__main__":
    main()
