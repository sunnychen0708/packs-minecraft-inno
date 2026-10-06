#!/usr/bin/env python3
"""Cross-pack compatibility gate for Utilities + Warehouse + Copy/Paste."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import threading
import time
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACK_NAMES = ("utilities", "warehouse", "copy-paste")
PACKS = {name: ROOT / "datapacks" / name for name in PACK_NAMES}

OBJECTIVE_ADD_RE = re.compile(
    r"\bscoreboard\s+objectives\s+add\s+([A-Za-z0-9_.+\-]+)\b"
)
STORAGE_WRITE_RE = re.compile(
    r"\bdata\s+(?:modify|remove)\s+storage\s+([a-z0-9_.-]+:[a-z0-9_./-]+)"
)
ALLOWED_SHARED_DATA_PATHS = {
    "minecraft/tags/function/load.json",
    "minecraft/tags/function/tick.json",
}
ALLOWED_FOREIGN_STORAGE_WRITES = {
    "copy-paste": {"warehouse:api"},
}
ERROR_PATTERNS = (
    "failed to load function",
    "failed to parse",
    "couldn't parse command",
    "unknown function",
    "failed to load datapacks",
    "errors in currently selected datapacks",
    "couldn't load tag",
    "invalid macro",
    "whilst instantiating",
    "missing argument",
    "command execution stopped due to limit",
)


def data_files(pack: Path) -> set[str]:
    root = pack / "data"
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
    }


def namespaces(pack: Path) -> set[str]:
    root = pack / "data"
    return {p.name for p in root.iterdir() if p.is_dir()}


def objective_definitions(pack: Path) -> set[str]:
    found: set[str] = set()
    for path in (pack / "data").rglob("*.mcfunction"):
        text = path.read_text(encoding="utf-8")
        found.update(OBJECTIVE_ADD_RE.findall(text))
    return found


def foreign_storage_writes(pack_name: str, pack: Path) -> set[str]:
    owned = namespaces(pack) - {"minecraft"}
    foreign: set[str] = set()
    for path in (pack / "data").rglob("*.mcfunction"):
        text = path.read_text(encoding="utf-8")
        for storage_id in STORAGE_WRITE_RE.findall(text):
            namespace = storage_id.split(":", 1)[0]
            if namespace not in owned:
                foreign.add(storage_id)
    return foreign


def check_tags(pack_name: str, pack: Path) -> None:
    for tag_name in ("load", "tick"):
        path = pack / "data/minecraft/tags/function" / f"{tag_name}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("replace", False) is False, (
            f"{pack_name} replaces minecraft:{tag_name} instead of merging it"
        )
        values = data.get("values", [])
        assert values, f"{pack_name} has an empty minecraft:{tag_name} tag"


def static_compatibility() -> None:
    for name, pack in PACKS.items():
        assert pack.is_dir(), f"Missing datapack: {pack}"
        check_tags(name, pack)

    files = {name: data_files(pack) for name, pack in PACKS.items()}
    for i, left in enumerate(PACK_NAMES):
        for right in PACK_NAMES[i + 1 :]:
            overlap = files[left] & files[right]
            unexpected = overlap - ALLOWED_SHARED_DATA_PATHS
            assert not unexpected, (
                f"{left} and {right} define the same data resources: "
                f"{sorted(unexpected)[:20]}"
            )

    ns = {name: namespaces(pack) - {"minecraft"} for name, pack in PACKS.items()}
    for i, left in enumerate(PACK_NAMES):
        for right in PACK_NAMES[i + 1 :]:
            overlap = ns[left] & ns[right]
            assert not overlap, (
                f"{left} and {right} own the same namespace(s): {sorted(overlap)}"
            )

    objectives = {
        name: objective_definitions(pack)
        for name, pack in PACKS.items()
    }
    for i, left in enumerate(PACK_NAMES):
        for right in PACK_NAMES[i + 1 :]:
            overlap = objectives[left] & objectives[right]
            assert not overlap, (
                f"{left} and {right} define the same scoreboard objective(s): "
                f"{sorted(overlap)}"
            )

    for name, pack in PACKS.items():
        foreign = foreign_storage_writes(name, pack)
        allowed = ALLOWED_FOREIGN_STORAGE_WRITES.get(name, set())
        unexpected = {
            storage_id
            for storage_id in foreign
            if storage_id not in allowed
        }
        assert not unexpected, (
            f"{name} writes foreign command storage outside the declared API: "
            f"{sorted(unexpected)}"
        )

    print(
        "PASS cross-pack static compatibility: "
        + ", ".join(
            f"{name}={len(objectives[name])} objectives"
            for name in PACK_NAMES
        ),
        flush=True,
    )


def zip_pack(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in source.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(source).as_posix())


def runtime_compatibility(java: Path, server: Path) -> None:
    work = ROOT / "dist" / ("all-datapacks-runtime-" + uuid.uuid4().hex[:8])
    work.mkdir(parents=True)
    packs = work / "world/datapacks"
    packs.mkdir(parents=True)

    for name, source in PACKS.items():
        zip_pack(source, packs / f"{name}.zip")

    harness = packs / "compatibility-test"
    funcs = harness / "data/compat_test/function"
    funcs.mkdir(parents=True)
    (harness / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "min_format": [121, 0],
                    "max_format": [121, 0],
                    "description": "All datapacks 26.3 compatibility regression",
                }
            }
        ),
        encoding="utf-8",
    )

    lines = [
        "scoreboard objectives add compatst dummy",
        "scoreboard players set #pass compatst 0",
        "scoreboard players set #fail compatst 0",
    ]
    assertions: list[str] = []

    def check(condition: str, label: str) -> None:
        assertions.append(label)
        lines.extend(
            [
                "scoreboard players set #ok compatst 0",
                f"execute {condition} run scoreboard players set #ok compatst 1",
                "execute if score #ok compatst matches 1 run scoreboard players add #pass compatst 1",
                f"execute if score #ok compatst matches 1 run say COMPAT_PASS_{label}",
                "execute unless score #ok compatst matches 1 run scoreboard players add #fail compatst 1",
                f"execute unless score #ok compatst matches 1 run say COMPAT_FAIL_{label}",
            ]
        )

    # Representative objectives prove all three load chains coexist.
    lines.extend(
        [
            "scoreboard players set #probe help 0",
            "scoreboard players set #probe sunny_id 0",
            "scoreboard players set #probe wh_sys 0",
            "scoreboard players set #probe pick 0",
            "scoreboard players set #probe mcc_id 0",
            "scoreboard players set #probe copypaste 0",
        ]
    )
    check("if score #probe help matches 0", "utilities_help_objective")
    check("if score #probe sunny_id matches 0", "utilities_nav_objective")
    check("if score #probe wh_sys matches 0", "warehouse_system_objective")
    check("if score #probe pick matches 0", "warehouse_pick_objective")
    check("if score #probe mcc_id matches 0", "copy_paste_id_objective")
    check("if score #probe copypaste matches 0", "copy_paste_ui_objective")

    util_version = re.search(r"v(\d+\.\d+(?:\.\d+)?)", json.loads((PACKS["utilities"] / "pack.mcmeta").read_text(encoding="utf-8"))["pack"]["description"]).group(1)
    check(
        f'if data storage sunny_nav:meta {{version:"26.3-{util_version}"}}',
        "utilities_storage_initialized",
    )
    check(
        "if data storage warehouse:meta {initialized:1b,v44:1b,search_ready:1b}",
        "warehouse_storage_initialized",
    )
    check("if score #slot mcc_id matches 256", "copy_paste_storage_lane_initialized")

    # Exercise the shared Warehouse API while all three packs are loaded.
    lines.append('function warehouse:api/count_item {item_id:"minecraft:stone"}')
    check(
        'if data storage warehouse:api result{ok:1b,complete:1b,item_id:"minecraft:stone",available:0,source_limit:64}',
        "warehouse_shared_api_available",
    )

    lines.extend(
        [
            f"execute if score #pass compatst matches {len(assertions)} if score #fail compatst matches 0 run say COMPAT_REGRESSION_SUCCESS",
            "say COMPAT_REGRESSION_DONE",
        ]
    )
    (funcs / "run.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (work / "eula.txt").write_text("eula=true\n", encoding="utf-8")
    (work / "server.properties").write_text(
        "server-ip=127.0.0.1\n"
        "server-port=0\n"
        "online-mode=false\n"
        "white-list=true\n"
        "view-distance=2\n"
        "simulation-distance=2\n"
        "max-tick-time=-1\n"
        "level-type=minecraft:flat\n"
        'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n',
        encoding="utf-8",
    )

    ready = threading.Event()
    done = threading.Event()
    output: list[str] = []
    proc = subprocess.Popen(
        [str(java), "-Xms512M", "-Xmx3072M", "-jar", str(server), "--nogui"],
        cwd=work,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    def reader() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            output.append(line)
            if "Done (" in line:
                ready.set()
            if "COMPAT_REGRESSION_DONE" in line:
                done.set()

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    try:
        assert ready.wait(90), "Combined server did not become ready"
        assert proc.stdin is not None
        proc.stdin.write("reload\n")
        proc.stdin.flush()
        # Warehouse builds 72 search-index shards over ticks.
        time.sleep(15)  # Warehouse search index builds 72 shards over ticks
        proc.stdin.write("function compat_test:run\n")
        proc.stdin.flush()
        assert done.wait(60), "Combined datapack compatibility regression did not complete"
    finally:
        if proc.poll() is None:
            assert proc.stdin is not None
            proc.stdin.write("stop\n")
            proc.stdin.flush()
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.terminate()
        thread.join(timeout=5)

    report = "".join(output)
    (work / "console.log").write_text(report, encoding="utf-8")
    failures = [
        label
        for label in assertions
        if f"COMPAT_PASS_{label}" not in report
    ]
    parse_errors = [
        line.strip()
        for line in output
        if any(pattern in line.lower() for pattern in ERROR_PATTERNS)
    ]
    assert not failures, f"Combined runtime assertion failures: {failures}"
    assert not parse_errors, f"Combined runtime parser/datapack errors: {parse_errors[:20]}"
    assert "COMPAT_REGRESSION_SUCCESS" in report
    print(
        f"PASS all-datapacks vanilla 26.3 compatibility: "
        f"{len(assertions)} runtime assertions; evidence: {work}",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", type=Path)
    parser.add_argument("--server-jar", type=Path)
    parser.add_argument("--accept-eula", action="store_true")
    args = parser.parse_args()

    static_compatibility()

    if args.java or args.server_jar or args.accept_eula:
        assert args.java and args.server_jar and args.accept_eula, (
            "--java, --server-jar, and --accept-eula must be supplied together"
        )
        (ROOT / "dist").mkdir(exist_ok=True)
        runtime_compatibility(args.java.resolve(), args.server_jar.resolve())


if __name__ == "__main__":
    main()
