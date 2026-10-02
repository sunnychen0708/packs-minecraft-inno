#!/usr/bin/env python3
"""Real release-to-release Warehouse world upgrade audit.

Boots an official Minecraft 26.3 server with an older released Warehouse ZIP,
writes persistent Warehouse/world state, shuts down cleanly, replaces only the
Warehouse ZIP with v4.2, and verifies the same world after restart.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
import zipfile

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


def write_harness(pack_dir: Path, sentinel: str) -> list[str]:
    funcs = pack_dir / "data/warehouse_upgrade_test/function"
    funcs.mkdir(parents=True, exist_ok=True)
    (pack_dir / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "min_format": [121, 0],
                    "max_format": [121, 0],
                    "description": "Warehouse release upgrade audit",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    historical = ["v03","v04","v06","v07","v08","v09","v10","v11","v13","v100","v12","v14","v21","v22","v30","v34","v40"]

    seed = [
        "scoreboard objectives add whup dummy",
        "function warehouse:system/off",
        "forceload add 0 0",
        "kill @e[type=minecraft:armor_stand,tag=wh_upgrade_actor]",
        'summon minecraft:armor_stand 0 80 0 {Tags:["wh_upgrade_actor"],NoGravity:1b,Invisible:1b}',
        "setblock 3 80 1 minecraft:chest",
        "setblock 3 80 3 minecraft:chest",
        "setblock 1 80 1 minecraft:chest",
        "setblock 1 80 3 minecraft:chest",
        "item replace block 3 80 1 container.0 with minecraft:diamond 23",
        "data modify storage warehouse:chests c31.a_x set value 3",
        "data modify storage warehouse:chests c31.a_y set value 80",
        "data modify storage warehouse:chests c31.a_z set value 1",
        "data modify storage warehouse:chests c31.b_x set value 3",
        "data modify storage warehouse:chests c31.b_y set value 80",
        "data modify storage warehouse:chests c31.b_z set value 3",
        'data modify storage warehouse:chests c31.dimension set value "minecraft:overworld"',
        "data modify storage warehouse:chests c31.registered set value 1b",
        "data modify storage warehouse:chests c31.valid set value 1b",
        'data modify storage warehouse:chests c31.name set value "UPGRADE_INTERNAL"',
        "data modify storage warehouse:chests c00.a_x set value 1",
        "data modify storage warehouse:chests c00.a_y set value 80",
        "data modify storage warehouse:chests c00.a_z set value 1",
        "data modify storage warehouse:chests c00.b_x set value 1",
        "data modify storage warehouse:chests c00.b_y set value 80",
        "data modify storage warehouse:chests c00.b_z set value 3",
        'data modify storage warehouse:chests c00.dimension set value "minecraft:overworld"',
        "data modify storage warehouse:chests c00.registered set value 1b",
        "data modify storage warehouse:chests c00.valid set value 1b",
        'data modify storage warehouse:boxnames c31 set value "UPGRADE_CUSTOM_NAME"',
        'data modify storage warehouse:rules overrides."minecraft:stone" set value 42',
        'data modify storage warehouse:migration queue set value [{item_id:"minecraft:stone",from:31,to:42}]',
        'data modify storage warehouse:migration active set value {item_id:"minecraft:diamond",from:11,to:42,legacy_keep:1b}',
        'data modify storage warehouse:names map."minecraft:stone" set value "UPGRADE_STONE_NAME"',
        f'data modify storage warehouse:meta upgrade_sentinel set value "{sentinel}"',
        "data modify storage warehouse:meta initialized set value 1b",
    ]
    seed += [f"data modify storage warehouse:meta {m} set value 1b" for m in historical]
    seed += [
        "data remove storage warehouse:meta v42",
        "data remove storage warehouse:meta search_ready",
        "data remove storage warehouse:meta search_rebuilding",
        "scoreboard players set #enabled wh_sys 0",
        "scoreboard players set #cursor wh_sys 37",
        "scoreboard players set #compact_code wh_tmp 17",
        "scoreboard players set #compact_slot wh_tmp 23",
        "scoreboard players set UpgradePlayer wh_target 31",
        "scoreboard players set UpgradePlayer wh_rule_item 777",
        "say WHUP_SEED_DONE",
    ]
    (funcs / "seed.mcfunction").write_text("\n".join(seed) + "\n", encoding="utf-8")

    labels: list[str] = []
    verify: list[str] = ["scoreboard players set #pass whup 0", "scoreboard players set #fail whup 0"]

    def check(condition: str, label: str) -> None:
        labels.append(label)
        verify.extend(
            [
                "scoreboard players set #ok whup 0",
                f"execute {condition} run scoreboard players set #ok whup 1",
                "execute if score #ok whup matches 1 run scoreboard players add #pass whup 1",
                f"execute if score #ok whup matches 1 run say WHUP_PASS_{label}",
                "execute unless score #ok whup matches 1 run scoreboard players add #fail whup 1",
                f"execute unless score #ok whup matches 1 run say WHUP_FAIL_{label}",
            ]
        )

    check('if entity @e[type=minecraft:armor_stand,tag=wh_upgrade_actor,limit=1]', "actor_persisted")
    check(
        f'if data storage warehouse:meta {{upgrade_sentinel:"{sentinel}",v40:1b,v42:1b,search_ready:1b}}',
        "meta_and_new_migration",
    )
    check(
        'if data storage warehouse:chests {c31:{a_x:3,a_y:80,a_z:1,b_x:3,b_y:80,b_z:3,dimension:"minecraft:overworld",registered:1b,valid:1b,name:"UPGRADE_INTERNAL"}}',
        "c31_registration",
    )
    check(
        'if data storage warehouse:chests {c00:{a_x:1,a_y:80,a_z:1,b_x:1,b_y:80,b_z:3,dimension:"minecraft:overworld",registered:1b,valid:1b}}',
        "c00_registration",
    )
    check('if data storage warehouse:boxnames {c31:"UPGRADE_CUSTOM_NAME"}', "custom_boxname")
    check('if data storage warehouse:rules {overrides:{"minecraft:stone":42}}', "classification_override")
    check(
        'if data storage warehouse:migration {queue:[{item_id:"minecraft:stone",from:31,to:42}],active:{item_id:"minecraft:diamond",from:11,to:42,legacy_keep:1b}}',
        "migration_state",
    )
    check('if data storage warehouse:names {map:{"minecraft:stone":"UPGRADE_STONE_NAME"}}', "custom_name_map")
    check("if score #enabled wh_sys matches 0", "system_enabled_state")
    check("if score #cursor wh_sys matches 37", "sort_cursor")
    check("if score #compact_code wh_tmp matches 17", "compact_code")
    check("if score #compact_slot wh_tmp matches 23", "compact_slot")
    check("if score UpgradePlayer wh_target matches 31", "score_holder_target")
    check("if score UpgradePlayer wh_rule_item matches 777", "score_holder_rule")
    check("if items block 3 80 1 container.0 minecraft:diamond", "physical_item")
    verify.extend(
        [
            "scoreboard players set #count whup 0",
            "execute store result score #count whup run data get block 3 80 1 Items[{Slot:0b}].count 1",
        ]
    )
    check("if score #count whup matches 23", "physical_count")
    check('if data storage warehouse:search_index terms."- Pigstep"', "rebuilt_search_index")
    verify += [
        f"execute if score #pass whup matches {len(labels)} if score #fail whup matches 0 run say WHUP_UPGRADE_SUCCESS",
        "say WHUP_VERIFY_DONE",
    ]
    (funcs / "verify.mcfunction").write_text("\n".join(verify) + "\n", encoding="utf-8")
    return labels


def run_server(java: Path, server_jar: Path, work: Path, commands: list[tuple[str, str, float]], log_name: str) -> str:
    output: list[str] = []
    ready = threading.Event()
    markers: dict[str, threading.Event] = {marker: threading.Event() for _, marker, _ in commands if marker}

    proc = subprocess.Popen(
        [str(java), "-Xms256M", "-Xmx1024M", "-jar", str(server_jar), "--nogui"],
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
            for marker, event in markers.items():
                if marker in line:
                    event.set()

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    try:
        assert ready.wait(120), f"{log_name}: server did not become ready"
        assert proc.stdin is not None
        for command, marker, delay in commands:
            if delay:
                time.sleep(delay)
            proc.stdin.write(command + "\n")
            proc.stdin.flush()
            if marker:
                assert markers[marker].wait(90), f"{log_name}: timeout waiting for {marker}"
    finally:
        if proc.poll() is None:
            try:
                assert proc.stdin is not None
                proc.stdin.write("stop\n")
                proc.stdin.flush()
                proc.wait(timeout=45)
            except Exception:
                proc.terminate()
        thread.join(timeout=5)

    report = "".join(output)
    (work / log_name).write_text(report, encoding="utf-8")
    return report


def audit_one(old_zip: Path, new_zip: Path, java: Path, server_jar: Path, label: str) -> Path:
    root = Path(tempfile.mkdtemp(prefix=f"warehouse-upgrade-{label}-"))
    world_packs = root / "world/datapacks"
    world_packs.mkdir(parents=True)
    harness = world_packs / "upgrade-harness"
    sentinel = label.upper() + "_KEEP"
    labels = write_harness(harness, sentinel)

    shutil.copy2(old_zip, world_packs / "warehouse.zip")
    (root / "eula.txt").write_text("eula=true\n", encoding="utf-8")
    (root / "server.properties").write_text(
        "server-ip=127.0.0.1\n"
        "server-port=0\n"
        "online-mode=false\n"
        "white-list=true\n"
        "view-distance=2\n"
        "simulation-distance=2\n"
        "level-type=minecraft:flat\n"
        'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n',
        encoding="utf-8",
    )

    # The legacy phase may contain known legacy warnings/errors; its purpose is
    # only to create and save a real world with old-pack data.
    old_report = run_server(
        java,
        server_jar,
        root,
        [
            ("forceload add 0 0", "", 1.0),
            ("function warehouse_upgrade_test:seed", "WHUP_SEED_DONE", 1.0),
        ],
        f"{label}-old.log",
    )
    assert "WHUP_SEED_DONE" in old_report

    shutil.copy2(new_zip, world_packs / "warehouse.zip")
    new_report = run_server(
        java,
        server_jar,
        root,
        [
            ("forceload add 0 0", "", 1.0),
            ("function warehouse_upgrade_test:verify", "WHUP_VERIFY_DONE", 9.0),
        ],
        f"{label}-v42.log",
    )

    failures = [name for name in labels if f"WHUP_PASS_{name}" not in new_report]
    explicit = [line.strip() for line in new_report.splitlines() if "WHUP_FAIL_" in line]
    parser_errors = [
        line.strip()
        for line in new_report.splitlines()
        if any(pattern in line.lower() for pattern in ERROR_PATTERNS)
    ]
    server_errors = [line.strip() for line in new_report.splitlines() if "/ERROR]" in line]

    assert not failures, f"{label}: missing upgrade assertions: {failures}"
    assert not explicit, f"{label}: explicit failures: {explicit}"
    assert not parser_errors, f"{label}: v4.2 parser/runtime errors: {parser_errors[:20]}"
    assert not server_errors, f"{label}: v4.2 server ERROR lines: {server_errors[:20]}"
    assert "WHUP_UPGRADE_SUCCESS" in new_report
    print(f"UPGRADE_PASS {label}->v4.2 assertions={len(labels)} evidence={root}", flush=True)
    return root


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-v40", type=Path, required=True)
    ap.add_argument("--old-v41", type=Path, required=True)
    ap.add_argument("--new-v42", type=Path, required=True)
    ap.add_argument("--java", type=Path, required=True)
    ap.add_argument("--server-jar", type=Path, required=True)
    args = ap.parse_args()

    audit_one(args.old_v40.resolve(), args.new_v42.resolve(), args.java.resolve(), args.server_jar.resolve(), "v40")
    audit_one(args.old_v41.resolve(), args.new_v42.resolve(), args.java.resolve(), args.server_jar.resolve(), "v41")


if __name__ == "__main__":
    main()
