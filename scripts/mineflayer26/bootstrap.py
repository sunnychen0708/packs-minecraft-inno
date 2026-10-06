#!/usr/bin/env python3
"""Build a reproducible Mineflayer stack with the pending Minecraft Java 26.3 fixes."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
STACK_FILE = HERE / "stack.json"
DEFAULT_DEST = REPO_ROOT / "dist" / "mineflayer-26.3-src"


def run(args: list[str], *, cwd: Path | None = None) -> None:
    shown = " ".join(str(x) for x in args)
    print(f"+ {shown}", flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def load_stack() -> dict:
    return json.loads(STACK_FILE.read_text(encoding="utf-8"))


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"required tool not found on PATH: {name}")


def checkout(dest: Path, repo: str, commit: str, *, force: bool) -> None:
    if dest.exists() and not (dest / ".git").is_dir():
        if not force:
            raise RuntimeError(f"{dest} exists but is not a git checkout; rerun with --force to replace it")
        shutil.rmtree(dest)

    if not dest.exists():
        dest.mkdir(parents=True)
        run(["git", "init"], cwd=dest)
        run(["git", "remote", "add", "origin", repo], cwd=dest)
    else:
        remotes = subprocess.run(
            ["git", "remote", "get-url", "origin"], cwd=dest, text=True, capture_output=True, check=False
        )
        if remotes.returncode != 0:
            run(["git", "remote", "add", "origin", repo], cwd=dest)
        elif remotes.stdout.strip() != repo:
            run(["git", "remote", "set-url", "origin", repo], cwd=dest)

    run(["git", "fetch", "--depth", "1", "origin", commit], cwd=dest)
    run(["git", "checkout", "--detach", "--force", "FETCH_HEAD"], cwd=dest)
    run(["git", "clean", "-fdx"], cwd=dest)


def patch_package(path: Path, *, deps: dict[str, str], overrides: dict[str, str] | None = None) -> None:
    package_file = path / "package.json"
    data = json.loads(package_file.read_text(encoding="utf-8"))
    current = data.setdefault("dependencies", {})
    current.update(deps)
    if overrides:
        data["overrides"] = {**data.get("overrides", {}), **overrides}
    package_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    for stale in ("package-lock.json", "yalc.lock"):
        p = path / stale
        if p.exists():
            p.unlink()
    yalc_dir = path / ".yalc"
    if yalc_dir.exists():
        shutil.rmtree(yalc_dir)


def install(path: Path, *, include_dev: bool = False) -> None:
    args = ["npm", "install", "--no-audit", "--no-fund"]
    if not include_dev:
        args.insert(2, "--omit=dev")
    run(args, cwd=path)


def prepare_node_minecraft_data(path: Path, cfg: dict) -> None:
    run(["git", "submodule", "update", "--init", "--recursive"], cwd=path)
    data_dir = path / "minecraft-data"
    if not (data_dir / ".git").exists():
        raise RuntimeError(f"minecraft-data submodule did not initialize: {data_dir}")
    run(["git", "remote", "set-url", "origin", cfg["data_repo"]], cwd=data_dir)
    run(["git", "fetch", "--depth", "1", "origin", cfg["data_commit"]], cwd=data_dir)
    run(["git", "checkout", "--detach", "--force", "FETCH_HEAD"], cwd=data_dir)


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one mapper patch target in {path}: found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def apply_mineflayer_mapper_fix(path: Path) -> None:
    """Apply PrismarineJS/mineflayer#4120 on top of the pinned 26.3 integration branch."""
    replace_exact(path / "lib/plugins/bed.js", "actionId: 2,", "actionId: 'stop_sleeping',")
    replace_exact(path / "lib/plugins/creative.js", "{ actionId: 1 }", "{ actionId: 'request_stats' }")
    replace_exact(path / "lib/plugins/game.js", "{ action: 0 }", "{ actionId: 'perform_respawn' }")
    replace_exact(path / "lib/plugins/health.js", "{ actionId: 0 }", "{ actionId: 'perform_respawn' }")
    replace_exact(
        path / "lib/plugins/physics.js",
        "actionId: bot.supportFeature('entityActionUsesStringMapper') ? 'start_elytra_flying' : 8,",
        "actionId: 'start_fall_flying',",
    )
    replace_exact(
        path / "lib/plugins/physics.js",
        "actionId: bot.supportFeature('entityActionUsesStringMapper')\n"
        "          ? (state ? 'start_sprinting' : 'stop_sprinting')\n"
        "          : (state ? 3 : 4),",
        "actionId: state ? 'start_sprinting' : 'stop_sprinting',",
    )
    replace_exact(
        path / "lib/plugins/physics.js",
        "actionId: state ? 0 : 1,",
        "actionId: state ? 'start_sneaking' : 'stop_sneaking',",
    )


def write_ready_marker(dest: Path, stack: dict) -> None:
    (dest / ".stack-ready.json").write_text(
        json.dumps({"stack": stack, "node": node_version(), "npm": npm_version()}, indent=2) + "\n",
        encoding="utf-8",
    )


def capture(*args: str) -> str:
    return subprocess.check_output(list(args), text=True).strip()


def node_version() -> str:
    return capture("node", "--version")


def npm_version() -> str:
    return capture("npm", "--version")


def verify(dest: Path, stack: dict) -> None:
    script = r"""
const path = require('path')
const root = process.argv[1]
const md = require(path.join(root, 'node-minecraft-data'))('26.3')
if (!md) throw new Error('minecraft-data returned no 26.3 data')
if (md.version.version !== 777) throw new Error(`expected protocol 777, got ${md.version.version}`)
if (md.blocksArray.length !== 1286) throw new Error(`expected 1286 blocks, got ${md.blocksArray.length}`)
if (md.itemsArray.length !== 1658) throw new Error(`expected 1658 items, got ${md.itemsArray.length}`)
if (md.entitiesArray.length !== 161) throw new Error(`expected 161 entities, got ${md.entitiesArray.length}`)
const mineflayer = require(path.join(root, 'mineflayer'))
if (!mineflayer || typeof mineflayer.createBot !== 'function') throw new Error('mineflayer createBot missing')
console.log(JSON.stringify({
  version: md.version.minecraftVersion,
  protocol: md.version.version,
  blocks: md.blocksArray.length,
  items: md.itemsArray.length,
  entities: md.entitiesArray.length,
  mineflayer: require(path.join(root, 'mineflayer/package.json')).version
}, null, 2))
"""
    run(["node", "-e", script, str(dest)])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--force", action="store_true", help="replace non-git paths inside the destination")
    parser.add_argument("--skip-install", action="store_true", help="only checkout and patch the source trees")
    parser.add_argument("--verify-only", action="store_true", help="verify an already-built stack")
    args = parser.parse_args()

    for tool in ("git", "node", "npm"):
        ensure_tool(tool)
    stack = load_stack()
    dest = args.dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)

    if args.verify_only:
        verify(dest, stack)
        return 0

    mapping = {
        "node-minecraft-data": stack["node_minecraft_data"],
        "node-minecraft-protocol": stack["minecraft_protocol"],
        "prismarine-chunk": stack["prismarine_chunk"],
        "prismarine-physics": stack["prismarine_physics"],
        "mineflayer": stack["mineflayer"],
    }
    for name, cfg in mapping.items():
        checkout(dest / name, cfg["repo"], cfg["commit"], force=args.force)

    prepare_node_minecraft_data(dest / "node-minecraft-data", stack["node_minecraft_data"])
    apply_mineflayer_mapper_fix(dest / "mineflayer")

    local_md = "file:../node-minecraft-data"
    patch_package(dest / "node-minecraft-protocol", deps={"minecraft-data": local_md})
    patch_package(dest / "prismarine-physics", deps={"minecraft-data": local_md})
    patch_package(
        dest / "mineflayer",
        deps={
            "minecraft-data": local_md,
            "minecraft-protocol": "file:../node-minecraft-protocol",
            "prismarine-chunk": "file:../prismarine-chunk",
            "prismarine-physics": "file:../prismarine-physics",
        },
        overrides={"minecraft-data": "$minecraft-data"},
    )

    if args.skip_install:
        print(f"sources prepared at {dest}; npm install skipped")
        return 0

    # Install leaves generated node-minecraft-data files in place first, then consumers use that local package.
    # node-minecraft-data's prepare step generates data/types and needs its dev dependencies.
    install(dest / "node-minecraft-data", include_dev=True)
    for name in ("node-minecraft-protocol", "prismarine-chunk", "prismarine-physics", "mineflayer"):
        install(dest / name)

    verify(dest, stack)
    write_ready_marker(dest, stack)
    print(f"Mineflayer 26.3 stack ready: {dest}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
