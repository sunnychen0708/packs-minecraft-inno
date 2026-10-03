#!/usr/bin/env python3
"""Isolated vanilla 26.3 behavioral regression for Warehouse."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import threading
import time
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datapacks/warehouse"
CODES = ["00", "10", "20", "30", "40", "50", "60"] + [
    f"{region}{slot}" for region in range(1, 7) for slot in range(1, 10)
]
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


def integration(java: Path, server: Path) -> None:
    work = ROOT / "dist" / ("warehouse-runtime-" + uuid.uuid4().hex[:8])
    work.mkdir(parents=True)
    packs = work / "world/datapacks"
    packs.mkdir(parents=True)

    with zipfile.ZipFile(packs / "warehouse.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path in PACK.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(PACK).as_posix())

    harness = packs / "regression"
    funcs = harness / "data/warehouse_server_test/function"
    funcs.mkdir(parents=True)
    (harness / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "min_format": [121, 0],
                    "max_format": [121, 0],
                    "description": "Warehouse 26.3 server regression",
                }
            }
        ),
        encoding="utf-8",
    )

    actor = "@e[type=minecraft:armor_stand,tag=wh_server_actor,limit=1]"
    lines = [
        "scoreboard objectives add whst dummy",
        "scoreboard players set #pass whst 0",
        "scoreboard players set #fail whst 0",
        "scoreboard players set #enabled wh_sys 0",
        "kill @e[type=minecraft:armor_stand,tag=wh_server_actor]",
        'summon minecraft:armor_stand 0 80 0 {Tags:["wh_server_actor"],NoGravity:1b,Invisible:1b}',
    ]
    assertions: list[str] = []

    def check(condition: str, label: str) -> None:
        assertions.append(label)
        lines.extend(
            [
                "scoreboard players set #ok whst 0",
                f"execute {condition} run scoreboard players set #ok whst 1",
                "execute if score #ok whst matches 1 run scoreboard players add #pass whst 1",
                f"execute if score #ok whst matches 1 run say WHST_PASS_{label}",
                "execute unless score #ok whst matches 1 run scoreboard players add #fail whst 1",
                f"execute unless score #ok whst matches 1 run say WHST_FAIL_{label}",
            ]
        )

    check(f"if entity {actor}", "test_actor_spawned")
    check("if data storage warehouse:meta {v42:1b,v44:1b,search_ready:1b}", "search_index_ready")
    check('if data storage warehouse:search_index terms."- Pigstep"', "search_index_populated")
    check("if score #search_index wh_sys matches 72", "search_index_all_shards")

    for code in CODES:
        lines.extend(
            [
                f"data modify storage warehouse:chests c{code}.registered set value 1b",
                f"data modify storage warehouse:chests c{code}.valid set value 1b",
            ]
        )
    lines.extend(
        [
            "data modify storage warehouse:chests c11.a_x set value 123",
            "data modify storage warehouse:chests c11.a_y set value 64",
            "data modify storage warehouse:chests c11.a_z set value -45",
            'data modify storage warehouse:chests c11.dimension set value "minecraft:the_nether"',
            'data modify storage warehouse:chests c11.name set value "CI_INTERNAL_NAME"',
            'data modify storage warehouse:boxnames c11 set value "CI_CUSTOM_NAME"',
            'data modify storage warehouse:rules overrides."minecraft:stone" set value 42',
        ]
    )

    lines.append(f"execute as {actor} at @s run function warehouse:admin/reset_registrations")

    for code in CODES:
        check(
            f"if data storage warehouse:chests c{code}{{registered:0b,valid:0b}}",
            f"reset_c{code}",
        )

    check(
        'if data storage warehouse:chests c11{a_x:123,a_y:64,a_z:-45,dimension:"minecraft:the_nether",name:"CI_INTERNAL_NAME"}',
        "registration_metadata_preserved",
    )
    check(
        'if data storage warehouse:boxnames {c11:"CI_CUSTOM_NAME"}',
        "custom_boxname_preserved",
    )
    check(
        'if data storage warehouse:rules {overrides:{"minecraft:stone":42}}',
        "classification_override_preserved",
    )

    lines.extend(
        [
            f"scoreboard players set {actor} wh_target 11",
            f'execute as {actor} at @s run function warehouse:register/save_nonzero {{code:11,a_x:5,a_y:70,a_z:5,b_x:6,b_y:70,b_z:5,dimension:"minecraft:overworld"}}',
        ]
    )
    check(
        'if data storage warehouse:chests c11{registered:1b,valid:1b,a_x:5,a_y:70,a_z:5,b_x:6,b_y:70,b_z:5,dimension:"minecraft:overworld"}',
        "reregister_c11",
    )
    check(
        'if data storage warehouse:boxnames {c11:"CI_CUSTOM_NAME"}',
        "reregister_keeps_custom_boxname",
    )
    check(
        'if data storage warehouse:rules {overrides:{"minecraft:stone":42}}',
        "reregister_keeps_classification_override",
    )

    # Shared Warehouse API: count/take/refund plain items across registered sources.
    lines.extend(
        [
            "setblock 5 70 5 minecraft:chest",
            "setblock 6 70 5 minecraft:chest",
            "setblock 7 70 5 minecraft:chest",
            "setblock 8 70 5 minecraft:chest",
            "setblock 9 70 5 minecraft:chest",
            "setblock 10 70 5 minecraft:chest",
            'data modify block 5 70 5 Items set value [{Slot:0b,id:"minecraft:stone",count:20},{Slot:1b,id:"minecraft:stone",count:7,components:{"minecraft:custom_data":{warehouse_api_test:1b}}}]',
            'data modify block 6 70 5 Items set value [{Slot:0b,id:"minecraft:stone",count:12}]',
            'data modify block 7 70 5 Items set value [{Slot:0b,id:"minecraft:stone",count:40}]',
            'data modify block 9 70 5 Items set value [{Slot:0b,id:"minecraft:stone",count:7,components:{"minecraft:custom_data":{warehouse_api_entry_custom:1b}}}]',
            "data modify storage warehouse:chests c12.registered set value 1b",
            "data modify storage warehouse:chests c12.valid set value 1b",
            'data modify storage warehouse:chests c12.dimension set value "minecraft:overworld"',
            "data modify storage warehouse:chests c12.a_x set value 7",
            "data modify storage warehouse:chests c12.a_y set value 70",
            "data modify storage warehouse:chests c12.a_z set value 5",
            "data modify storage warehouse:chests c12.b_x set value 8",
            "data modify storage warehouse:chests c12.b_y set value 70",
            "data modify storage warehouse:chests c12.b_z set value 5",
            # Duplicate registration of the same physical source with A/B reversed.
            "data modify storage warehouse:chests c13.registered set value 1b",
            "data modify storage warehouse:chests c13.valid set value 1b",
            'data modify storage warehouse:chests c13.dimension set value "minecraft:overworld"',
            "data modify storage warehouse:chests c13.a_x set value 8",
            "data modify storage warehouse:chests c13.a_y set value 70",
            "data modify storage warehouse:chests c13.a_z set value 5",
            "data modify storage warehouse:chests c13.b_x set value 7",
            "data modify storage warehouse:chests c13.b_y set value 70",
            "data modify storage warehouse:chests c13.b_z set value 5",
            "data modify storage warehouse:chests c00.registered set value 1b",
            "data modify storage warehouse:chests c00.valid set value 1b",
            'data modify storage warehouse:chests c00.dimension set value "minecraft:overworld"',
            "data modify storage warehouse:chests c00.a_x set value 9",
            "data modify storage warehouse:chests c00.a_y set value 70",
            "data modify storage warehouse:chests c00.a_z set value 5",
            "data modify storage warehouse:chests c00.b_x set value 10",
            "data modify storage warehouse:chests c00.b_y set value 70",
            "data modify storage warehouse:chests c00.b_z set value 5",
            f'execute as {actor} run function warehouse:api/count_item {{item_id:"minecraft:stone"}}',
        ]
    )
    check('if data storage warehouse:api result{ok:1b,complete:1b}', "api_count_ok")
    check('if data storage warehouse:api result{item_id:"minecraft:stone",available:72}', "api_count_plain_72")
    check('if data storage warehouse:api result{sources_scanned:3,stale_sources:0,source_limit:64}', "api_count_three_sources")
    check('if data storage warehouse:api {material_source_count:3,meta:{material_source_limit:64}}', "api_material_source_snapshot_dedupes_alias")

    lines.append(f'execute as {actor} run function warehouse:api/take_item {{item_id:"minecraft:stone",count:50}}')
    check('if data storage warehouse:api result{operation:"take_item",ok:1b,complete:1b,requested:50,taken:50,remaining:0,stale_sources:0}', "api_take_exact_amount")
    check('if data block 5 70 5 Items[{Slot:1b,id:"minecraft:stone",count:7,components:{"minecraft:custom_data":{warehouse_api_test:1b}}}]', "api_take_preserves_custom_stack")

    lines.append(f'execute as {actor} run function warehouse:api/count_item {{item_id:"minecraft:stone"}}')
    check('if data storage warehouse:api result{ok:1b,complete:1b,available:22,stale_sources:0}', "api_count_after_take")

    # Insufficient withdrawal is all-or-nothing.
    lines.append(f'execute as {actor} run function warehouse:api/take_item {{item_id:"minecraft:stone",count:23}}')
    check('if data storage warehouse:api result{operation:"take_item",ok:0b,complete:0b,requested:23,taken:0,remaining:23,available:22,error:"insufficient_stock"}', "api_take_insufficient_is_atomic")
    lines.append(f'execute as {actor} run function warehouse:api/count_item {{item_id:"minecraft:stone"}}')
    check('if data storage warehouse:api result{ok:1b,complete:1b,available:22}', "api_take_insufficient_changed_nothing")

    lines.append(f'execute as {actor} run function warehouse:api/refund_item {{item_id:"minecraft:stone",count:50}}')
    check('if data storage warehouse:api result{operation:"refund_item",ok:1b,complete:1b,requested:50,inserted:50,remaining:0}', "api_refund_to_entry")
    check('if data block 9 70 5 Items[{id:"minecraft:stone",count:50}]', "api_refund_materialized_in_entry")
    check('if data block 9 70 5 Items[{Slot:0b,id:"minecraft:stone",count:7,components:{"minecraft:custom_data":{warehouse_api_entry_custom:1b}}}]', "api_refund_preserves_custom_entry_stack")

    lines.append(f'execute as {actor} run function warehouse:api/count_item {{item_id:"minecraft:stone"}}')
    check('if data storage warehouse:api result{ok:1b,complete:1b,available:72,stale_sources:0}', "api_count_after_refund")

    # A stale registration must not silently look like a complete inventory total.
    lines.extend(
        [
            "setblock 8 70 5 air",
            f'execute as {actor} run function warehouse:api/count_item {{item_id:"minecraft:stone"}}',
        ]
    )
    check('if data storage warehouse:api result{ok:0b,complete:0b,available:50,sources_scanned:3,stale_sources:1,source_limit:64}', "api_count_rejects_stale_source")
    lines.append(f'execute as {actor} run function warehouse:api/take_item {{item_id:"minecraft:stone",count:1}}')
    check('if data storage warehouse:api result{operation:"take_item",ok:0b,complete:0b,taken:0,error:"source_unavailable"}', "api_take_refuses_stale_snapshot")

    # Durable refund queue: a full c00 accepts the refund debt, then drains after space appears.
    lines.append("data remove storage warehouse:api pending_refunds")
    for slot in range(27):
        lines.append(f'item replace block 9 70 5 container.{slot} with minecraft:cobblestone 64')
        lines.append(f'item replace block 10 70 5 container.{slot} with minecraft:cobblestone 64')
    lines.append(f'execute as {actor} run function warehouse:api/refund_item {{item_id:"minecraft:stone",count:10}}')
    check('if data storage warehouse:api result{operation:"refund_item",ok:1b,complete:1b,inserted:0,queued:10,remaining:0,deferred:1b}', "api_refund_full_entry_queues")
    check('if data storage warehouse:api pending_refunds[{item_id:"minecraft:stone",count:10}]', "api_refund_pending_persisted")
    lines.extend(
        [
            "item replace block 9 70 5 container.0 with minecraft:air",
            "function warehouse:api/pending_refunds/tick",
        ]
    )
    check('unless data storage warehouse:api pending_refunds[0]', "api_refund_pending_drained")
    check('if data block 9 70 5 Items[{Slot:0b,id:"minecraft:stone",count:10}]', "api_refund_pending_materialized")

    # Phase 4: resolve a looked-at block without changing it, then Pick up to one vanilla stack.
    for code in CODES:
        lines.extend(
            [
                f"data modify storage warehouse:chests c{code}.registered set value 0b",
                f"data modify storage warehouse:chests c{code}.valid set value 0b",
            ]
        )
    lines.extend(
        [
            "setblock 15 70 5 minecraft:stone",
            "setblock 16 70 5 minecraft:bedrock",
            "setblock 20 70 5 minecraft:chest",
            "setblock 21 70 5 minecraft:chest",
            'data modify block 20 70 5 Items set value [{Slot:0b,id:"minecraft:stone",count:20}]',
            "data modify storage warehouse:chests c11.registered set value 1b",
            "data modify storage warehouse:chests c11.valid set value 1b",
            'data modify storage warehouse:chests c11.dimension set value "minecraft:overworld"',
            "data modify storage warehouse:chests c11.a_x set value 20",
            "data modify storage warehouse:chests c11.a_y set value 70",
            "data modify storage warehouse:chests c11.a_z set value 5",
            "data modify storage warehouse:chests c11.b_x set value 21",
            "data modify storage warehouse:chests c11.b_y set value 70",
            "data modify storage warehouse:chests c11.b_z set value 5",
            f"execute as {actor} positioned 15 70 5 run function warehouse:api/resolve_block",
        ]
    )
    check(
        'if data storage warehouse:api result{operation:"resolve_block",ok:1b,complete:1b,item_id:"minecraft:stone",max_stack:64}',
        "api_resolve_block_stone",
    )
    check("if block 15 70 5 minecraft:stone", "api_resolve_block_preserves_source")
    check(
        "unless entity @e[type=minecraft:armor_stand,tag=wh_resolve_probe]",
        "api_resolve_probe_cleanup",
    )

    lines.append(f"execute as {actor} positioned 15 70 5 run function warehouse:pick/hit")
    check(
        'if data storage warehouse:pick result{ok:1b,item_id:"minecraft:stone",count:20}',
        "pick_takes_available_below_stack",
    )
    check("unless data block 20 70 5 Items[{id:"minecraft:stone"}]", "pick_removed_twenty")

    lines.extend(
        [
            'data modify block 20 70 5 Items set value [{Slot:0b,id:"minecraft:stone",count:64}]',
            f"execute as {actor} positioned 15 70 5 run function warehouse:pick/hit",
        ]
    )
    check(
        'if data storage warehouse:pick result{ok:1b,item_id:"minecraft:stone",count:64}',
        "pick_caps_at_full_stack",
    )
    check("unless data block 20 70 5 Items[{id:"minecraft:stone"}]", "pick_removed_full_stack")

    lines.append(f"execute as {actor} positioned 16 70 5 run function warehouse:api/resolve_block")
    check(
        'if data storage warehouse:api result{operation:"resolve_block",ok:0b,complete:1b,error:"no_survival_item"}',
        "api_resolve_rejects_no_survival_item",
    )
    check("if block 16 70 5 minecraft:bedrock", "api_resolve_unsupported_preserves_source")

    lines.extend(
        [
            f"execute if score #pass whst matches {len(assertions)} if score #fail whst matches 0 run say WHST_REGRESSION_SUCCESS",
            "say WHST_REGRESSION_DONE",
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
        "level-type=minecraft:flat\n"
        'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n',
        encoding="utf-8",
    )

    ready = threading.Event()
    done = threading.Event()
    output: list[str] = []
    proc = subprocess.Popen(
        [str(java), "-Xms256M", "-Xmx1024M", "-jar", str(server), "--nogui"],
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
            if "WHST_REGRESSION_DONE" in line:
                done.set()

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    try:
        assert ready.wait(90), "Server did not become ready"
        assert proc.stdin is not None
        proc.stdin.write("forceload add 0 0\n")
        proc.stdin.flush()
        time.sleep(2)
        proc.stdin.write("reload\n")
        proc.stdin.flush()
        time.sleep(8)
        proc.stdin.write("forceload add 0 0\n")
        proc.stdin.write("function warehouse_server_test:run\n")
        proc.stdin.flush()
        assert done.wait(60), "Warehouse runtime regression did not complete"
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
    failures = [label for label in assertions if f"WHST_PASS_{label}" not in report]
    parse_errors = [
        line.strip()
        for line in output
        if any(pattern in line.lower() for pattern in ERROR_PATTERNS)
    ]
    assert not failures, f"Runtime assertion failures: {failures}"
    assert not parse_errors, f"Runtime parser/datapack errors: {parse_errors[:20]}"
    assert "WHST_REGRESSION_SUCCESS" in report
    print(
        f"PASS Warehouse vanilla 26.3 runtime regression: {len(assertions)} assertions; evidence: {work}",
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--server-jar", type=Path, required=True)
    parser.add_argument("--accept-eula", action="store_true", required=True)
    args = parser.parse_args()
    (ROOT / "dist").mkdir(exist_ok=True)
    integration(args.java.resolve(), args.server_jar.resolve())
