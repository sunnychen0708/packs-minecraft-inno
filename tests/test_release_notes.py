"""Regression checks for source-tree release notes after history squashing."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "generate-release-notes.py"


def git(directory: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args), cwd=directory, check=True,
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def put(base: Path, path: str, value: str) -> None:
    target = base / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value, encoding="utf-8")


class ReleaseNotesRegression(unittest.TestCase):
    def test_diverged_tag_and_pack_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            bare = directory / "origin.git"
            source = directory / "source"
            checkout = directory / "checkout"

            git(directory, "init", "--bare", str(bare))
            git(bare, "symbolic-ref", "HEAD", "refs/heads/main")
            git(directory, "init", "-b", "main", str(source))
            git(source, "config", "user.name", "Test")
            git(source, "config", "user.email", "test@example.com")

            put(source, "datapacks/warehouse/changed.mcfunction", "old")
            put(source, "datapacks/warehouse/deleted.mcfunction", "old")
            put(source, "datapacks/utilities/unchanged.mcfunction", "old")
            git(source, "add", ".")
            git(source, "commit", "-m", "Old release")
            git(source, "tag", "-a", "warehouse-v4.7", "-m", "v4.7")
            git(source, "tag", "-a", "utilities-v3.8", "-m", "other pack")
            git(source, "remote", "add", "origin", str(bare))
            git(source, "push", "origin", "main", "--tags")

            # Rewrite all history. The previous release tag is NOT an
            # ancestor of this main, but the actual file trees are comparable.
            git(source, "checkout", "--orphan", "rewrite")
            put(source, "datapacks/warehouse/changed.mcfunction", "new")
            (source / "datapacks/warehouse/deleted.mcfunction").unlink()
            put(source, "datapacks/warehouse/added.mcfunction", "new")
            put(source, "datapacks/utilities/unchanged.mcfunction", "other")
            git(source, "add", "-A")
            git(source, "commit", "-m", "Squashed history")
            git(source, "branch", "-M", "main")
            git(source, "push", "--force", "origin", "main")
            git(directory, "clone", "--depth", "1",
                bare.as_uri(), str(checkout))

            notes_file = checkout / "notes.md"
            result = subprocess.run(
                (sys.executable, str(SCRIPT), "warehouse",
                 "warehouse-v4.8", str(notes_file)),
                cwd=checkout, capture_output=True, text=True, check=True,
            )
            notes = notes_file.read_text(encoding="utf-8")
            self.assertIn("warehouse-v4.7", result.stdout)
            self.assertIn("3** (1 added, 1 modified, 1 removed)", notes)
            self.assertIn("changed.mcfunction", notes)
            self.assertIn("deleted.mcfunction", notes)
            self.assertIn("added.mcfunction", notes)
            self.assertNotIn("unchanged.mcfunction", notes)
            self.assertNotIn("utilities", notes)

    def test_version_aware_tag_selection(self) -> None:
        spec = importlib.util.spec_from_file_location("release_notes", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual((4, 10, 0), module.parse_tag("warehouse", "warehouse-v4.10"))
        self.assertEqual((4, 7, 2), module.parse_tag("warehouse", "warehouse-v4.7.2"))
        self.assertIsNone(module.parse_tag("warehouse", "utilities-v3.8"))


if __name__ == "__main__":
    unittest.main()
