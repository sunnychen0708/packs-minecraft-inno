#!/usr/bin/env python3
"""Comprehensive one-shot audit for the released Warehouse v4.2 datapack."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
import zipfile
from pathlib import Path

MAIN_CODES = [f"{r}{p}" for r in range(1, 7) for p in range(1, 10)]
ALL_CODES = ["00", "10", "20", "30", "40", "50", "60"] + MAIN_CODES
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


def static_audit(pack_zip: Path) -> dict[str, int]:
    with tempfile.TemporaryDirectory(prefix="warehouse-static-") as td:
        root = Path(td)
        with zipfile.ZipFile(pack_zip) as zf:
            zf.extractall(root)

        assert (root / "pack.mcmeta").is_file(), "release ZIP missing pack.mcmeta"
        assert (root / "data/warehouse/function/load.mcfunction").is_file(), "release ZIP missing Warehouse functions"
        pack = json.loads((root / "pack.mcmeta").read_text(encoding="utf-8"))
        assert "v4.2" in pack["pack"]["description"]
        assert pack["pack"]["min_format"] == [121, 0]
        assert pack["pack"]["max_format"] == [121, 0]

        json_files = list(root.rglob("*.json"))
        for path in json_files:
            json.loads(path.read_text(encoding="utf-8"))

        functions = list((root / "data/warehouse/function").rglob("*.mcfunction"))
        assert len(functions) >= 4500, f"unexpected function count: {len(functions)}"

        def func_path(identifier: str) -> Path:
            return root / "data/warehouse/function" / (identifier + ".mcfunction")

        def dialog_path(identifier: str) -> Path:
            return root / "data/warehouse/dialog" / (identifier + ".json")

        missing_functions: set[str] = set()
        missing_dialogs: set[str] = set()
        function_re = re.compile(r"(?<![\w#])(?:\$)?function\s+warehouse:([a-z0-9_./-]+)")
        schedule_re = re.compile(r"schedule\s+function\s+warehouse:([a-z0-9_./-]+)")
        dialog_re = re.compile(r"dialog\s+show\s+[^\n]*?warehouse:([a-z0-9_./-]+)")

        for path in functions:
            text = path.read_text(encoding="utf-8")
            for rx in (function_re, schedule_re):
                for ref in rx.findall(text):
                    if not ref.endswith("/") and not func_path(ref).is_file():
                        missing_functions.add(ref)
            for ref in dialog_re.findall(text):
                if "$(" not in ref and not dialog_path(ref).is_file():
                    missing_dialogs.add(ref)

        def walk(value):
            if isinstance(value, dict):
                for v in value.values():
                    yield from walk(v)
            elif isinstance(value, list):
                for v in value:
                    yield from walk(v)
            elif isinstance(value, str):
                yield value

        dialog_files = list((root / "data/warehouse/dialog").rglob("*.json"))
        for path in dialog_files:
            obj = json.loads(path.read_text(encoding="utf-8"))
            for s in walk(obj):
                for ref in function_re.findall(s):
                    if not ref.endswith("/") and not func_path(ref).is_file():
                        missing_functions.add(ref)

        assert not missing_functions, f"missing function refs: {sorted(missing_functions)[:20]}"
        assert not missing_dialogs, f"missing dialog refs: {sorted(missing_dialogs)[:20]}"

        for code in ALL_CODES:
            for rel in (
                f"view/open/{code}.mcfunction",
                f"boxname/save_{code}.mcfunction",
                f"boxname/reset_{code}.mcfunction",
                f"unregister/do_{code}.mcfunction",
            ):
                assert (root / "data/warehouse/function" / rel).is_file(), f"missing generated function {rel}"

        for code in MAIN_CODES:
            assert (root / f"data/warehouse/function/sort/route/{code}.mcfunction").is_file()
            assert (root / f"data/warehouse/tags/item/box_{code}.json").is_file()

        search_items = {
            int(p.stem)
            for p in (root / "data/warehouse/function/search/item").glob("*.mcfunction")
            if p.stem.isdigit()
        }
        rule_items = {
            int(p.stem)
            for p in (root / "data/warehouse/function/rule/item").glob("*.mcfunction")
            if p.stem.isdigit()
        }
        expected_items = set(range(1544))
        assert search_items == expected_items, f"search item files mismatch: {len(search_items)}"
        assert rule_items == expected_items, f"rule item files mismatch: {len(rule_items)}"

        shards = {
            p.stem.removeprefix("init_")
            for p in (root / "data/warehouse/function/search/index").glob("init_*.mcfunction")
        }
        assert shards == {f"{i:03d}" for i in range(72)}, f"search shard mismatch: {len(shards)}"

        return {
            "functions": len(functions),
            "json": len(json_files),
            "dialogs": len(dialog_files),
            "search_items": len(search_items),
            "rule_items": len(rule_items),
            "shards": len(shards),
        }


def make_harness(harness: Path, phase: str = "full") -> tuple[int, list[str]]:
    funcs = harness / "data/warehouse_full_test/function"
    funcs.mkdir(parents=True)
    (harness / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "min_format": [121, 0],
                    "max_format": [121, 0],
                    "description": "Warehouse v4.2 comprehensive audit harness",
                }
            }
        ),
        encoding="utf-8",
    )

    assertions: list[str] = []

    def phase(name: str):
        lines = [
            "scoreboard objectives add wfta dummy",
            "scoreboard players add #pass wfta 0",
            "scoreboard players add #fail wfta 0",
        ]

        def check(condition: str, label: str):
            full = f"{name}_{label}"
            assertions.append(full)
            lines.extend(
                [
                    "scoreboard players set #ok wfta 0",
                    f"execute {condition} run scoreboard players set #ok wfta 1",
                    "execute if score #ok wfta matches 1 run scoreboard players add #pass wfta 1",
                    f"execute if score #ok wfta matches 1 run say WFTA_PASS_{full}",
                    "execute unless score #ok wfta matches 1 run scoreboard players add #fail wfta 1",
                    f"execute unless score #ok wfta matches 1 run say WFTA_FAIL_{full}",
                ]
            )

        return lines, check

    actor = "@e[type=minecraft:armor_stand,tag=wh_full_actor,limit=1]"

    # Fresh release boot.
    lines, check = phase("fresh")
    lines += [
        "kill @e[type=minecraft:armor_stand,tag=wh_full_actor]",
        'summon minecraft:armor_stand 0 80 0 {Tags:["wh_full_actor"],NoGravity:1b,Invisible:1b}',
    ]
    check(f"if entity {actor}", "actor")
    check("if data storage warehouse:meta {v42:1b,search_ready:1b}", "v42_ready")
    check("if score #search_index wh_sys matches 72", "all_shards")
    check('if data storage warehouse:search_index terms."- Pigstep"', "known_index_term")
    lines.append("say WFTA_PHASE_FRESH_DONE")
    (funcs / "fresh.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if phase == "basic":
        # Core management functions.
        lines, check = phase("basic")
        lines += [
            "data remove storage warehouse:migration active",
            "data modify storage warehouse:migration queue set value []",
            "data modify storage warehouse:rules overrides set value {}",
            "scoreboard players set #enabled wh_sys 0",
            "setblock 1 80 1 minecraft:chest",
            "setblock 1 80 3 minecraft:chest",
            "setblock 3 80 1 minecraft:chest",
            "setblock 3 80 3 minecraft:chest",
            "setblock 5 80 1 minecraft:chest",
            "setblock 5 80 3 minecraft:chest",
            "setblock 7 80 1 minecraft:chest",
            "setblock 7 80 3 minecraft:chest",
            "setblock 9 80 1 minecraft:chest",
            "setblock 9 80 3 minecraft:chest",
            "setblock 11 80 1 minecraft:copper_chest",
            f"execute as {actor} run function warehouse:register/save_00 {{a_x:1,a_y:80,a_z:1,b_x:1,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
            f"scoreboard players set {actor} wh_target 31",
            f"execute as {actor} run function warehouse:register/save_nonzero {{code:31,a_x:3,a_y:80,a_z:1,b_x:3,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
            f"scoreboard players set {actor} wh_target 30",
            f"execute as {actor} run function warehouse:register/save_nonzero {{code:30,a_x:5,a_y:80,a_z:1,b_x:5,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
            f"scoreboard players set {actor} wh_target 42",
            f"execute as {actor} run function warehouse:register/save_nonzero {{code:42,a_x:7,a_y:80,a_z:1,b_x:7,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
            f"scoreboard players set {actor} wh_target 11",
            f"execute as {actor} run function warehouse:register/save_nonzero {{code:11,a_x:9,a_y:80,a_z:1,b_x:9,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
        ]
        check('if data storage warehouse:chests {c00:{registered:1b,valid:1b,a_x:1,a_y:80,a_z:1,b_x:1,b_y:80,b_z:3}}', "register_00")
        for code, x in (("31",3),("30",5),("42",7),("11",9)):
            check(f'if data storage warehouse:chests {{c{code}:{{registered:1b,valid:1b,a_x:{x},a_y:80,a_z:1,b_x:{x},b_y:80,b_z:3}}}}', f"register_{code}")
        check("if block 11 80 1 #warehouse:storage_chests", "copper_chest_tag")
        lines += [
            "function warehouse:system/on",
        ]
        check("if score #enabled wh_sys matches 1", "system_on")
        lines += ["function warehouse:system/off"]
        check("if score #enabled wh_sys matches 0", "system_off")
        lines += ["function warehouse:system/toggle"]
        check("if score #enabled wh_sys matches 1", "system_toggle_on")
        lines += ["function warehouse:system/toggle"]
        check("if score #enabled wh_sys matches 0", "system_toggle_off")
        lines += [
            'data modify storage warehouse:runtime rename.new set value {text:"CI_RENAMED_STONE"}',
            f"execute as {actor} run function warehouse:boxname/save_31",
        ]
        check('if data storage warehouse:boxnames {c31:{text:"CI_RENAMED_STONE"}}', "rename")
        lines += [f"execute as {actor} run function warehouse:boxname/reset_31"]
        check('if data storage warehouse:boxnames {c31:{text:"石頭方塊"}}', "rename_reset")
        lines += [
            f"scoreboard players set {actor} wh_target 11",
            f"scoreboard players set {actor} wh_unreg_do 1",
            f"execute as {actor} run function warehouse:unregister/do_11",
        ]
        check('if data storage warehouse:chests {c11:{registered:0b,valid:0b}}', "unregister")
        lines += [
            f"scoreboard players set {actor} wh_target 11",
            f"execute as {actor} run function warehouse:register/save_nonzero {{code:11,a_x:9,a_y:80,a_z:1,b_x:9,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
            f"scoreboard players set {actor} wh_rule_item 1",
            f"scoreboard players set {actor} wh_rule_dest 42",
            'data remove storage warehouse:rules overrides."minecraft:diamond"',
            f"execute as {actor} run function warehouse:rule/apply_selected",
        ]
        check('if data storage warehouse:rules {overrides:{"minecraft:diamond":42}}', "rule_apply")
        check('if data storage warehouse:migration {queue:[{item_id:"minecraft:diamond",from:11,to:42}]}', "rule_enqueues_migration")
        lines += [
            "data modify storage warehouse:migration queue set value []",
            f"scoreboard players set {actor} wh_rule_item 1",
            f"execute as {actor} run function warehouse:rule/remove_selected",
        ]
        check('if data storage warehouse:rules {overrides:{"minecraft:diamond":0}}', "rule_remove")
        lines += [
            'data remove storage warehouse:rules overrides."minecraft:diamond"',
            "say WFTA_PHASE_BASIC_DONE",
        ]
        (funcs / "basic.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    
        return len(assertions), assertions

    if phase == "routing":
        # Minimal physical setup for automatic sorting / overflow / safe fallback.
        lines = [
            "function warehouse:system/off",
            "data remove storage warehouse:migration active",
            "data modify storage warehouse:migration queue set value []",
            "data modify storage warehouse:rules overrides set value {}",
            "setblock 1 80 1 minecraft:chest",
            "setblock 1 80 3 minecraft:chest",
            "setblock 3 80 1 minecraft:chest",
            "setblock 3 80 3 minecraft:chest",
            "setblock 5 80 1 minecraft:chest",
            "setblock 5 80 3 minecraft:chest",
            f"execute as {actor} run function warehouse:register/save_00 {{a_x:1,a_y:80,a_z:1,b_x:1,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
            f"scoreboard players set {actor} wh_target 31",
            f"execute as {actor} run function warehouse:register/save_nonzero {{code:31,a_x:3,a_y:80,a_z:1,b_x:3,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
            f"scoreboard players set {actor} wh_target 30",
            f"execute as {actor} run function warehouse:register/save_nonzero {{code:30,a_x:5,a_y:80,a_z:1,b_x:5,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
            "data modify block 1 80 1 Items set value []",
            "data modify block 1 80 3 Items set value []",
            "data modify block 3 80 1 Items set value []",
            "data modify block 3 80 3 Items set value []",
            "data modify block 5 80 1 Items set value []",
            "data modify block 5 80 3 Items set value []",
            "say WFTA_PHASE_ROUTING_SETUP_DONE",
        ]
        (funcs / "routing_setup.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

        lines = [
            'data remove storage warehouse:rules overrides."minecraft:stone"',
            "item replace block 1 80 1 container.0 with minecraft:stone 32",
            "scoreboard players set #cursor wh_sys 0",
            "function warehouse:system/on",
            "say WFTA_PHASE_PREPARE_AUTO_SORT_DONE",
        ]
        (funcs / "prepare_auto_sort.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

        lines, check = phase("auto_sort")
        lines += ["function warehouse:system/off"]
        check("unless items block 1 80 1 container.0 *", "source_empty")
        check("if items block 3 80 1 container.0 minecraft:stone", "dest_item")
        lines += [
            "scoreboard players set #tmp wfta 0",
            "execute store result score #tmp wfta run data get block 3 80 1 Items[{Slot:0b}].count 1",
        ]
        check("if score #tmp wfta matches 32", "dest_count")
        lines.append("say WFTA_PHASE_VERIFY_AUTO_SORT_DONE")
        (funcs / "verify_auto_sort.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

        lines, check = phase("routing")
        lines += [
            "data modify block 1 80 1 Items set value []",
            "data modify block 1 80 3 Items set value []",
            "data modify block 3 80 1 Items set value []",
            "data modify block 3 80 3 Items set value []",
            "data modify block 5 80 1 Items set value []",
            "data modify block 5 80 3 Items set value []",
        ]
        for z in (1, 3):
            for slot in range(27):
                lines.append(f"item replace block 3 80 {z} container.{slot} with minecraft:stone 64")
        lines += [
            "item replace block 1 80 1 container.1 with minecraft:stone 10",
            "scoreboard players set #cursor wh_sys 1",
            "function warehouse:system/on",
            "say WFTA_PHASE_ROUTING_OVERFLOW_STARTED",
        ]
        (funcs / "routing_overflow_start.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

        lines, check = phase("routing_overflow")
        lines += ["function warehouse:system/off"]
        check("unless items block 1 80 1 container.1 *", "source_empty")
        check("if items block 5 80 1 container.0 minecraft:stone", "dest_item")
        lines += [
            "scoreboard players set #tmp wfta 0",
            "execute store result score #tmp wfta run data get block 5 80 1 Items[{Slot:0b}].count 1",
        ]
        check("if score #tmp wfta matches 10", "dest_count")
        for z in (1, 3):
            for slot in range(27):
                lines.append(f"item replace block 5 80 {z} container.{slot} with minecraft:stone 64")
        lines += [
            "item replace block 1 80 1 container.2 with minecraft:stone 5",
            "scoreboard players set #cursor wh_sys 2",
            "function warehouse:system/on",
            "say WFTA_PHASE_ROUTING_SAFE_STARTED",
        ]
        (funcs / "routing_overflow_verify_and_safe_start.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

        lines, check = phase("routing_safe")
        lines += ["function warehouse:system/off"]
        check("if items block 1 80 1 container.2 minecraft:stone", "source_item")
        lines += [
            "scoreboard players set #tmp wfta 0",
            "execute store result score #tmp wfta run data get block 1 80 1 Items[{Slot:2b}].count 1",
        ]
        check("if score #tmp wfta matches 5", "source_count")
        lines.append("say WFTA_PHASE_ROUTING_DONE")
        (funcs / "routing_safe_verify.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

        return len(assertions), assertions

    # Simulate an actual v3.4 world: all pre-v4 markers and persistent user state exist.
    lines = [
        'data modify storage warehouse:meta initialized set value 1b',
        'data modify storage warehouse:meta v03 set value 1b',
        'data modify storage warehouse:meta v04 set value 1b',
        'data modify storage warehouse:meta v06 set value 1b',
        'data modify storage warehouse:meta v07 set value 1b',
        'data modify storage warehouse:meta v08 set value 1b',
        'data modify storage warehouse:meta v09 set value 1b',
        'data modify storage warehouse:meta v10 set value 1b',
        'data modify storage warehouse:meta v11 set value 1b',
        'data modify storage warehouse:meta v13 set value 1b',
        'data modify storage warehouse:meta v100 set value 1b',
        'data modify storage warehouse:meta v12 set value 1b',
        'data modify storage warehouse:meta v14 set value 1b',
        'data modify storage warehouse:meta v21 set value 1b',
        'data modify storage warehouse:meta v22 set value 1b',
        'data modify storage warehouse:meta v30 set value 1b',
        'data modify storage warehouse:meta v34 set value 1b',
        'data remove storage warehouse:meta v40',
        'data remove storage warehouse:meta v42',
        'data remove storage warehouse:meta search_ready',
        'data remove storage warehouse:meta search_rebuilding',
        'data modify storage warehouse:meta legacy_sentinel set value "V34_KEEP"',
        'data modify storage warehouse:chests c11 set value {code:"11",display_code:"11",type:"main",region:1,pos:1,name:"CI_V34_INTERNAL",registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:9,a_y:80,a_z:1,b_x:9,b_y:80,b_z:3,legacy_extra:341}',
        'data modify storage warehouse:boxnames c11 set value {text:"CI_V34_CUSTOM"}',
        'data modify storage warehouse:boxnames c31 set value {text:"CI_V34_STONE"}',
        'data modify storage warehouse:rules overrides set value {"minecraft:stone":42,"minecraft:diamond":0}',
        'data modify storage warehouse:migration queue set value [{item_id:"minecraft:stone",from:31,to:42,legacy:34}]',
        'data modify storage warehouse:migration active set value {item_id:"minecraft:diamond",from:11,to:42,legacy:34}',
        'data modify storage warehouse:names map."minecraft:diamond" set value "CI_V34_DIAMOND_NAME"',
        'data modify storage warehouse:search_index terms."CI_LEGACY_ONLY" set value {count:1,ids:["0"]}',
        "scoreboard players set #enabled wh_sys 0",
        "scoreboard players set #cursor wh_sys 17",
        "scoreboard players set #compact_code wh_tmp 23",
        "scoreboard players set #compact_slot wh_tmp 10",
        f"scoreboard players set {actor} wh_target 37",
        f"scoreboard players set {actor} wh_rule_item 123",
        "setblock 9 80 1 minecraft:chest",
        "setblock 9 80 3 minecraft:chest",
        "item replace block 9 80 1 container.0 with minecraft:diamond 13",
        "say WFTA_PHASE_SEED_V34_DONE",
    ]
    (funcs / "seed_v34.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    lines, check = phase("upgrade_v34")
    check('if data storage warehouse:meta {v34:1b,v40:1b,v42:1b,search_ready:1b,legacy_sentinel:"V34_KEEP"}', "meta")
    check('if data storage warehouse:chests {c11:{name:"CI_V34_INTERNAL",registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:9,a_y:80,a_z:1,b_x:9,b_y:80,b_z:3,legacy_extra:341}}', "chest_record")
    check('if data storage warehouse:boxnames {c11:{text:"CI_V34_CUSTOM"},c31:{text:"CI_V34_STONE"}}', "boxnames")
    check('if data storage warehouse:rules {overrides:{"minecraft:stone":42,"minecraft:diamond":0}}', "rules")
    check('if data storage warehouse:migration {queue:[{item_id:"minecraft:stone",from:31,to:42,legacy:34}],active:{item_id:"minecraft:diamond",from:11,to:42,legacy:34}}', "migration_state")
    check('if data storage warehouse:names {map:{"minecraft:diamond":"CI_V34_DIAMOND_NAME"}}', "names")
    check('unless data storage warehouse:search_index terms."CI_LEGACY_ONLY"', "derived_index_replaced")
    check('if data storage warehouse:search_index terms."- Pigstep"', "new_index_present")
    check("if score #enabled wh_sys matches 0", "enabled")
    check("if score #cursor wh_sys matches 17", "cursor")
    check("if score #compact_code wh_tmp matches 23", "compact_code")
    check("if score #compact_slot wh_tmp matches 10", "compact_slot")
    check(f"if score {actor} wh_target matches 37", "actor_target")
    check(f"if score {actor} wh_rule_item matches 123", "actor_rule_item")
    check("if items block 9 80 1 container.0 minecraft:diamond", "physical_inventory")
    lines += [
        "scoreboard players set #tmp wfta 0",
        "execute store result score #tmp wfta run data get block 9 80 1 Items[{Slot:0b}].count 1",
    ]
    check("if score #tmp wfta matches 13", "physical_count")
    lines.append("say WFTA_PHASE_VERIFY_V34_DONE")
    (funcs / "verify_v34.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Simulate v4.1 -> v4.2 upgrade as a second compatibility path.
    lines = [
        'data modify storage warehouse:meta initialized set value 1b',
        'data modify storage warehouse:meta v03 set value 1b',
        'data modify storage warehouse:meta v04 set value 1b',
        'data modify storage warehouse:meta v06 set value 1b',
        'data modify storage warehouse:meta v07 set value 1b',
        'data modify storage warehouse:meta v08 set value 1b',
        'data modify storage warehouse:meta v09 set value 1b',
        'data modify storage warehouse:meta v10 set value 1b',
        'data modify storage warehouse:meta v11 set value 1b',
        'data modify storage warehouse:meta v13 set value 1b',
        'data modify storage warehouse:meta v100 set value 1b',
        'data modify storage warehouse:meta v12 set value 1b',
        'data modify storage warehouse:meta v14 set value 1b',
        'data modify storage warehouse:meta v21 set value 1b',
        'data modify storage warehouse:meta v22 set value 1b',
        'data modify storage warehouse:meta v30 set value 1b',
        'data modify storage warehouse:meta v34 set value 1b',
        'data modify storage warehouse:meta v40 set value 1b',
        'data remove storage warehouse:meta v42',
        'data remove storage warehouse:meta search_ready',
        'data remove storage warehouse:meta search_rebuilding',
        'data modify storage warehouse:meta legacy_sentinel set value "V41_KEEP"',
        'data modify storage warehouse:chests c11.name set value "CI_V41_INTERNAL"',
        'data modify storage warehouse:chests c11.legacy_extra set value 411',
        'data modify storage warehouse:boxnames c11 set value {text:"CI_V41_CUSTOM"}',
        'data modify storage warehouse:rules overrides set value {"minecraft:stone":31,"minecraft:diamond":42}',
        'data modify storage warehouse:migration queue set value [{item_id:"minecraft:diamond",from:11,to:42,legacy:41}]',
        'data modify storage warehouse:migration active set value {item_id:"minecraft:stone",from:31,to:42,legacy:41}',
        'data modify storage warehouse:names map."minecraft:diamond" set value "CI_V41_DIAMOND_NAME"',
        'data modify storage warehouse:search_index terms."CI_V41_OLD_INDEX" set value {count:1,ids:["0"]}',
        "scoreboard players set #enabled wh_sys 0",
        "scoreboard players set #cursor wh_sys 29",
        "scoreboard players set #compact_code wh_tmp 31",
        "scoreboard players set #compact_slot wh_tmp 22",
        f"scoreboard players set {actor} wh_target 55",
        f"scoreboard players set {actor} wh_rule_item 321",
        "item replace block 9 80 1 container.0 with minecraft:diamond 14",
        "say WFTA_PHASE_SEED_V41_DONE",
    ]
    (funcs / "seed_v41.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    lines, check = phase("upgrade_v41")
    check('if data storage warehouse:meta {v40:1b,v42:1b,search_ready:1b,legacy_sentinel:"V41_KEEP"}', "meta")
    check('if data storage warehouse:chests {c11:{name:"CI_V41_INTERNAL",registered:1b,valid:1b,legacy_extra:411}}', "chest_record")
    check('if data storage warehouse:boxnames {c11:{text:"CI_V41_CUSTOM"}}', "boxname")
    check('if data storage warehouse:rules {overrides:{"minecraft:stone":31,"minecraft:diamond":42}}', "rules")
    check('if data storage warehouse:migration {queue:[{item_id:"minecraft:diamond",from:11,to:42,legacy:41}],active:{item_id:"minecraft:stone",from:31,to:42,legacy:41}}', "migration_state")
    check('if data storage warehouse:names {map:{"minecraft:diamond":"CI_V41_DIAMOND_NAME"}}', "names")
    check('unless data storage warehouse:search_index terms."CI_V41_OLD_INDEX"', "derived_index_replaced")
    check("if score #enabled wh_sys matches 0", "enabled")
    check("if score #cursor wh_sys matches 29", "cursor")
    check("if score #compact_code wh_tmp matches 31", "compact_code")
    check("if score #compact_slot wh_tmp matches 22", "compact_slot")
    check(f"if score {actor} wh_target matches 55", "actor_target")
    check(f"if score {actor} wh_rule_item matches 321", "actor_rule_item")
    lines += [
        "scoreboard players set #tmp wfta 0",
        "execute store result score #tmp wfta run data get block 9 80 1 Items[{Slot:0b}].count 1",
    ]
    check("if score #tmp wfta matches 14", "physical_count")
    lines.append("say WFTA_PHASE_VERIFY_V41_DONE")
    (funcs / "verify_v41.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if phase == "compat":
        return len(assertions), assertions

    # Core management functions.
    lines, check = phase("basic")
    lines += [
        "data remove storage warehouse:migration active",
        "data modify storage warehouse:migration queue set value []",
        "data modify storage warehouse:rules overrides set value {}",
        "scoreboard players set #enabled wh_sys 0",
        "setblock 1 80 1 minecraft:chest",
        "setblock 1 80 3 minecraft:chest",
        "setblock 3 80 1 minecraft:chest",
        "setblock 3 80 3 minecraft:chest",
        "setblock 5 80 1 minecraft:chest",
        "setblock 5 80 3 minecraft:chest",
        "setblock 7 80 1 minecraft:chest",
        "setblock 7 80 3 minecraft:chest",
        "setblock 9 80 1 minecraft:chest",
        "setblock 9 80 3 minecraft:chest",
        "setblock 11 80 1 minecraft:copper_chest",
        f"execute as {actor} run function warehouse:register/save_00 {{a_x:1,a_y:80,a_z:1,b_x:1,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
        f"scoreboard players set {actor} wh_target 31",
        f"execute as {actor} run function warehouse:register/save_nonzero {{code:31,a_x:3,a_y:80,a_z:1,b_x:3,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
        f"scoreboard players set {actor} wh_target 30",
        f"execute as {actor} run function warehouse:register/save_nonzero {{code:30,a_x:5,a_y:80,a_z:1,b_x:5,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
        f"scoreboard players set {actor} wh_target 42",
        f"execute as {actor} run function warehouse:register/save_nonzero {{code:42,a_x:7,a_y:80,a_z:1,b_x:7,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
        f"scoreboard players set {actor} wh_target 11",
        f"execute as {actor} run function warehouse:register/save_nonzero {{code:11,a_x:9,a_y:80,a_z:1,b_x:9,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
    ]
    check('if data storage warehouse:chests {c00:{registered:1b,valid:1b,a_x:1,a_y:80,a_z:1,b_x:1,b_y:80,b_z:3}}', "register_00")
    for code, x in (("31",3),("30",5),("42",7),("11",9)):
        check(f'if data storage warehouse:chests {{c{code}:{{registered:1b,valid:1b,a_x:{x},a_y:80,a_z:1,b_x:{x},b_y:80,b_z:3}}}}', f"register_{code}")
    check("if block 11 80 1 #warehouse:storage_chests", "copper_chest_tag")
    lines += [
        "function warehouse:system/on",
    ]
    check("if score #enabled wh_sys matches 1", "system_on")
    lines += ["function warehouse:system/off"]
    check("if score #enabled wh_sys matches 0", "system_off")
    lines += ["function warehouse:system/toggle"]
    check("if score #enabled wh_sys matches 1", "system_toggle_on")
    lines += ["function warehouse:system/toggle"]
    check("if score #enabled wh_sys matches 0", "system_toggle_off")
    lines += [
        'data modify storage warehouse:runtime rename.new set value {text:"CI_RENAMED_STONE"}',
        f"execute as {actor} run function warehouse:boxname/save_31",
    ]
    check('if data storage warehouse:boxnames {c31:{text:"CI_RENAMED_STONE"}}', "rename")
    lines += [f"execute as {actor} run function warehouse:boxname/reset_31"]
    check('if data storage warehouse:boxnames {c31:{text:"石頭方塊"}}', "rename_reset")
    lines += [
        f"scoreboard players set {actor} wh_target 11",
        f"scoreboard players set {actor} wh_unreg_do 1",
        f"execute as {actor} run function warehouse:unregister/do_11",
    ]
    check('if data storage warehouse:chests {c11:{registered:0b,valid:0b}}', "unregister")
    lines += [
        f"scoreboard players set {actor} wh_target 11",
        f"execute as {actor} run function warehouse:register/save_nonzero {{code:11,a_x:9,a_y:80,a_z:1,b_x:9,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
        f"scoreboard players set {actor} wh_rule_item 1",
        f"scoreboard players set {actor} wh_rule_dest 42",
        'data remove storage warehouse:rules overrides."minecraft:diamond"',
        f"execute as {actor} run function warehouse:rule/apply_selected",
    ]
    check('if data storage warehouse:rules {overrides:{"minecraft:diamond":42}}', "rule_apply")
    check('if data storage warehouse:migration {queue:[{item_id:"minecraft:diamond",from:11,to:42}]}', "rule_enqueues_migration")
    lines += [
        "data modify storage warehouse:migration queue set value []",
        f"scoreboard players set {actor} wh_rule_item 1",
        f"execute as {actor} run function warehouse:rule/remove_selected",
    ]
    check('if data storage warehouse:rules {overrides:{"minecraft:diamond":0}}', "rule_remove")
    lines += [
        'data remove storage warehouse:rules overrides."minecraft:diamond"',
        "say WFTA_PHASE_BASIC_DONE",
    ]
    (funcs / "basic.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Actual tick-driven automatic sorting.
    lines = [
        "data modify block 1 80 1 Items set value []",
        "data modify block 1 80 3 Items set value []",
        "data modify block 3 80 1 Items set value []",
        "data modify block 3 80 3 Items set value []",
        'data remove storage warehouse:rules overrides."minecraft:stone"',
        "item replace block 1 80 1 container.0 with minecraft:stone 32",
        "scoreboard players set #cursor wh_sys 0",
        "function warehouse:system/on",
        "say WFTA_PHASE_PREPARE_AUTO_SORT_DONE",
    ]
    (funcs / "prepare_auto_sort.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    lines, check = phase("auto_sort")
    lines += ["function warehouse:system/off"]
    check("unless items block 1 80 1 container.0 *", "source_empty")
    check("if items block 3 80 1 container.0 minecraft:stone", "dest_item")
    lines += ["scoreboard players set #tmp wfta 0", "execute store result score #tmp wfta run data get block 3 80 1 Items[{Slot:0b}].count 1"]
    check("if score #tmp wfta matches 32", "dest_count")
    lines.append("say WFTA_PHASE_VERIFY_AUTO_SORT_DONE")
    (funcs / "verify_auto_sort.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Override routing, overflow, and safe fallback.
    lines, check = phase("routing")
    lines += [
        "data modify block 1 80 1 Items set value []",
        "data modify block 7 80 1 Items set value []",
        "data modify block 7 80 3 Items set value []",
        'function warehouse:rule/write_override {item_id:"minecraft:stone",dest:42}',
        "item replace block 1 80 1 container.0 with minecraft:stone 7",
        "scoreboard players set #cursor wh_sys 0",
        "function warehouse:sort/tick",
    ]
    check("unless items block 1 80 1 container.0 *", "override_source_empty")
    check("if items block 7 80 1 container.0 minecraft:stone", "override_dest")
    lines += [
        'data remove storage warehouse:rules overrides."minecraft:stone"',
        "data modify block 1 80 1 Items set value []",
        "data modify block 3 80 1 Items set value []",
        "data modify block 3 80 3 Items set value []",
        "data modify block 5 80 1 Items set value []",
        "data modify block 5 80 3 Items set value []",
    ]
    for x in (3,):
        for z in (1,3):
            for slot in range(27):
                lines.append(f"item replace block {x} 80 {z} container.{slot} with minecraft:stone 64")
    lines += [
        "item replace block 1 80 1 container.1 with minecraft:stone 10",
        "scoreboard players set #cursor wh_sys 1",
        "function warehouse:sort/tick",
    ]
    check("unless items block 1 80 1 container.1 *", "overflow_source_empty")
    check("if items block 5 80 1 container.0 minecraft:stone", "overflow_dest")
    lines += ["scoreboard players set #tmp wfta 0", "execute store result score #tmp wfta run data get block 5 80 1 Items[{Slot:0b}].count 1"]
    check("if score #tmp wfta matches 10", "overflow_count")
    for x in (5,):
        for z in (1,3):
            for slot in range(27):
                lines.append(f"item replace block {x} 80 {z} container.{slot} with minecraft:stone 64")
    lines += [
        "item replace block 1 80 1 container.2 with minecraft:stone 5",
        "scoreboard players set #cursor wh_sys 2",
        "function warehouse:sort/tick",
    ]
    check("if items block 1 80 1 container.2 minecraft:stone", "safe_remain_item")
    lines += ["scoreboard players set #tmp wfta 0", "execute store result score #tmp wfta run data get block 1 80 1 Items[{Slot:2b}].count 1"]
    check("if score #tmp wfta matches 5", "safe_remain_count")
    lines.append("say WFTA_PHASE_ROUTING_DONE")
    (funcs / "routing.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Tick-driven background compaction.
    lines = [
        "data modify block 3 80 1 Items set value []",
        "data modify block 3 80 3 Items set value []",
        "item replace block 3 80 1 container.0 with minecraft:stone 10",
        "item replace block 3 80 1 container.1 with minecraft:stone 20",
        "scoreboard players set #compact_code wh_tmp 22",
        "scoreboard players set #compact_slot wh_tmp 1",
        "function warehouse:system/on",
        "say WFTA_PHASE_PREPARE_COMPACT_DONE",
    ]
    (funcs / "prepare_compact.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    lines, check = phase("compact")
    lines += ["function warehouse:system/off", "scoreboard players set #tmp wfta 0", "execute store result score #tmp wfta run data get block 3 80 1 Items[{Slot:0b}].count 1"]
    check("if score #tmp wfta matches 30", "merged_count")
    check("unless items block 3 80 1 container.1 *", "source_cleared")
    lines.append("say WFTA_PHASE_VERIFY_COMPACT_DONE")
    (funcs / "verify_compact.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Viewer and search backends. Seed a fresh known inventory here so this test
    # does not depend on any prior transport/compact phase.
    lines, check = phase("view_search")
    lines += [
        "data modify block 3 80 1 Items set value []",
        "data modify block 3 80 3 Items set value []",
        "item replace block 3 80 1 container.0 with minecraft:stone 30",
        f"execute as {actor} run function warehouse:view/open/31",
        "data get block 3 80 1",
        "data get storage warehouse:runtime viewer",
    ]
    check('if data storage warehouse:runtime {viewer:{current_total:{id:"minecraft:stone",count:30}}}', "viewer_current_total")
    check('if data storage warehouse:runtime {viewer:{render:{l01:"石頭方塊 ×30",count:1}}}', "viewer_render")
    check(f"if score {actor} wh_viewlines matches 1", "viewer_line_count")
    lines += [
        f'execute as {actor} run function warehouse:search/run {{q:"鑽石"}}',
    ]
    check("if data storage warehouse:runtime search.match", "search_match")
    lines += [
        'data remove storage warehouse:rules overrides."minecraft:diamond"',
        f"execute as {actor} run function warehouse:search/item/0",
    ]
    check('if data storage warehouse:runtime {search:{item_id:"minecraft:diamond"}}', "search_item")
    check("if score #search_box wh_search matches 11", "search_default_box")
    lines += [
        'function warehouse:rule/write_override {item_id:"minecraft:diamond",dest:42}',
        f"execute as {actor} run function warehouse:search/item/0",
    ]
    check("if score #search_override wh_search matches 1", "search_override_flag")
    check("if score #search_box wh_search matches 42", "search_override_box")
    lines += [
        'data remove storage warehouse:rules overrides."minecraft:diamond"',
        "say WFTA_PHASE_VIEW_SEARCH_DONE",
    ]
    (funcs / "view_search.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Tick-driven migration of old stock after a rule change.
    lines = [
        "data remove storage warehouse:migration active",
        "data modify storage warehouse:migration queue set value []",
        "data modify block 1 80 1 Items set value []",
        "data modify block 1 80 3 Items set value []",
        "data modify block 3 80 1 Items set value []",
        "data modify block 3 80 3 Items set value []",
        "data modify block 7 80 1 Items set value []",
        "data modify block 7 80 3 Items set value []",
        "item replace block 3 80 1 container.0 with minecraft:stone 12",
        'function warehouse:migration/enqueue {item_id:"minecraft:stone",old_box:31,dest:42}',
        "function warehouse:system/on",
        "say WFTA_PHASE_PREPARE_MIGRATION_DONE",
    ]
    (funcs / "prepare_migration.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    lines, check = phase("migration")
    lines += ["function warehouse:system/off"]
    check("unless items block 3 80 1 container.0 *", "source_empty")
    check("if items block 7 80 1 container.0 minecraft:stone", "dest_item")
    lines += ["scoreboard players set #tmp wfta 0", "execute store result score #tmp wfta run data get block 7 80 1 Items[{Slot:0b}].count 1"]
    check("if score #tmp wfta matches 12", "dest_count")
    check("unless data storage warehouse:migration active", "active_done")
    check("unless data storage warehouse:migration queue[0]", "queue_done")
    lines.append("say WFTA_PHASE_VERIFY_MIGRATION_DONE")
    (funcs / "verify_migration.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Full 61-slot reset regression, including physical item and user metadata preservation.
    lines, check = phase("reset")
    lines += [
        'data modify storage warehouse:boxnames c31 set value {text:"CI_KEEP_AFTER_RESET"}',
        'data modify storage warehouse:rules overrides."minecraft:stone" set value 42',
        "item replace block 9 80 1 container.0 with minecraft:diamond 5",
    ]
    for code in ALL_CODES:
        lines += [
            f"data modify storage warehouse:chests c{code}.registered set value 1b",
            f"data modify storage warehouse:chests c{code}.valid set value 1b",
        ]
    lines += [f"execute as {actor} run function warehouse:admin/reset_registrations"]
    for code in ALL_CODES:
        check(f"if data storage warehouse:chests c{code}{{registered:0b,valid:0b}}", f"c{code}")
    check('if data storage warehouse:boxnames {c31:{text:"CI_KEEP_AFTER_RESET"}}', "boxname_preserved")
    check('if data storage warehouse:rules {overrides:{"minecraft:stone":42}}', "rule_preserved")
    check("if items block 9 80 1 container.0 minecraft:diamond", "physical_item_preserved")
    lines += [
        f"scoreboard players set {actor} wh_target 11",
        f"execute as {actor} run function warehouse:register/save_nonzero {{code:11,a_x:9,a_y:80,a_z:1,b_x:9,b_y:80,b_z:3,dimension:\"minecraft:overworld\"}}",
    ]
    check('if data storage warehouse:chests {c11:{registered:1b,valid:1b}}', "reregister")
    lines.append("say WFTA_PHASE_RESET_DONE")
    (funcs / "reset.mcfunction").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return len(assertions), assertions


def runtime_audit(pack_zip: Path, java: Path, server: Path, phase: str = "full") -> tuple[int, Path]:
    work = Path(tempfile.mkdtemp(prefix="warehouse-full-audit-"))
    world_packs = work / "world/datapacks"
    world_packs.mkdir(parents=True)
    shutil.copy2(pack_zip, world_packs / "warehouse-v4.2.zip")
    expected_count, assertion_labels = make_harness(world_packs / "audit-harness", phase)

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

    output: list[str] = []
    ready = threading.Event()
    proc = subprocess.Popen(
        [str(java), "-Xms256M", "-Xmx1536M", "-jar", str(server), "--nogui"],
        cwd=work,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    def reader():
        assert proc.stdout is not None
        for line in proc.stdout:
            output.append(line)
            if "Done (" in line:
                ready.set()

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()

    def send(command: str):
        assert proc.stdin is not None
        proc.stdin.write(command + "\n")
        proc.stdin.flush()

    def wait_marker(marker: str, timeout: float = 45.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if any(marker in line for line in output):
                return
            if proc.poll() is not None:
                raise AssertionError(f"server exited while waiting for {marker}")
            time.sleep(0.1)
        raise AssertionError(f"timeout waiting for {marker}")

    caught = None
    failure: BaseException | None = None
    try:
        assert ready.wait(90), "server did not become ready"
        send("forceload add 0 0")
        time.sleep(6)

        send("function warehouse_full_test:fresh")
        wait_marker("WFTA_PHASE_FRESH_DONE")

        if phase == "basic":
            send("function warehouse_full_test:basic")
            wait_marker("WFTA_PHASE_BASIC_DONE")
        elif phase == "routing":
            send("function warehouse_full_test:routing_setup")
            wait_marker("WFTA_PHASE_ROUTING_SETUP_DONE")

            send("function warehouse_full_test:prepare_auto_sort")
            wait_marker("WFTA_PHASE_PREPARE_AUTO_SORT_DONE")
            time.sleep(0.8)
            send("function warehouse_full_test:verify_auto_sort")
            wait_marker("WFTA_PHASE_VERIFY_AUTO_SORT_DONE")

            send("function warehouse_full_test:routing_overflow_start")
            wait_marker("WFTA_PHASE_ROUTING_OVERFLOW_STARTED")
            time.sleep(0.8)
            send("function warehouse_full_test:routing_overflow_verify_and_safe_start")
            wait_marker("WFTA_PHASE_ROUTING_SAFE_STARTED")
            time.sleep(0.8)
            send("function warehouse_full_test:routing_safe_verify")
            wait_marker("WFTA_PHASE_ROUTING_DONE")
        else:
            send("function warehouse_full_test:seed_v34")
            wait_marker("WFTA_PHASE_SEED_V34_DONE")
            send("reload")
            time.sleep(8)
            send("forceload add 0 0")
            send("function warehouse_full_test:verify_v34")
            wait_marker("WFTA_PHASE_VERIFY_V34_DONE")

            send("function warehouse_full_test:seed_v41")
            wait_marker("WFTA_PHASE_SEED_V41_DONE")
            send("reload")
            time.sleep(8)
            send("forceload add 0 0")
            send("function warehouse_full_test:verify_v41")
            wait_marker("WFTA_PHASE_VERIFY_V41_DONE")

            if phase == "compat":
                send("say WFTA_PHASE_COMPAT_DONE")
            else:
                send("function warehouse_full_test:basic")
                wait_marker("WFTA_PHASE_BASIC_DONE")

                send("function warehouse_full_test:prepare_auto_sort")
                wait_marker("WFTA_PHASE_PREPARE_AUTO_SORT_DONE")
                time.sleep(0.7)
                send("function warehouse_full_test:verify_auto_sort")
                wait_marker("WFTA_PHASE_VERIFY_AUTO_SORT_DONE")

                send("function warehouse_full_test:routing")
                wait_marker("WFTA_PHASE_ROUTING_DONE")

                send("function warehouse_full_test:prepare_compact")
                wait_marker("WFTA_PHASE_PREPARE_COMPACT_DONE")
                time.sleep(0.8)
                send("function warehouse_full_test:verify_compact")
                wait_marker("WFTA_PHASE_VERIFY_COMPACT_DONE")

                send("function warehouse_full_test:view_search")
                wait_marker("WFTA_PHASE_VIEW_SEARCH_DONE")

                send("function warehouse_full_test:prepare_migration")
                wait_marker("WFTA_PHASE_PREPARE_MIGRATION_DONE")
                time.sleep(3)
                send("function warehouse_full_test:verify_migration")
                wait_marker("WFTA_PHASE_VERIFY_MIGRATION_DONE")

                send("function warehouse_full_test:reset")
                wait_marker("WFTA_PHASE_RESET_DONE")
    except BaseException as exc:
        caught = exc
    finally:
        if proc.poll() is None:
            try:
                send("stop")
                proc.wait(timeout=30)
            except Exception:
                proc.terminate()
        thread.join(timeout=5)
        report = "".join(output)
        console_path = work / "console.log"
        console_path.write_text(report, encoding="utf-8")
        print(f"AUDIT_EVIDENCE {console_path}", flush=True)

    if caught is not None:
        raise caught

    labels_to_check = assertion_labels
    if phase == "compat":
        labels_to_check = [
            label for label in assertion_labels
            if label.startswith(("fresh_", "upgrade_v34_", "upgrade_v41_"))
        ]
    elif phase == "basic":
        labels_to_check = [
            label for label in assertion_labels
            if label.startswith(("fresh_", "basic_"))
        ]
    elif phase == "routing":
        labels_to_check = [
            label for label in assertion_labels
            if label.startswith(("fresh_", "auto_sort_", "routing_overflow_", "routing_safe_"))
        ]
    failures = [label for label in labels_to_check if f"WFTA_PASS_{label}" not in report]
    explicit_fails = [line.strip() for line in output if "WFTA_FAIL_" in line]
    parser_errors = [
        line.strip()
        for line in output
        if any(pattern in line.lower() for pattern in ERROR_PATTERNS)
    ]
    server_errors = [line.strip() for line in output if "/ERROR]" in line]

    assert not failures, f"missing/failed assertions ({len(failures)}): {failures[:30]}"
    assert not explicit_fails, f"explicit assertion failures: {explicit_fails[:30]}"
    assert not parser_errors, f"datapack/runtime parser errors: {parser_errors[:20]}"
    assert not server_errors, f"server ERROR lines: {server_errors[:20]}"

    return len(labels_to_check), work


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-zip", type=Path, required=True)
    ap.add_argument("--java", type=Path, required=True)
    ap.add_argument("--server-jar", type=Path, required=True)
    ap.add_argument("--phase", choices=("compat", "basic", "routing", "full"), default="full")
    args = ap.parse_args()

    stats = static_audit(args.pack_zip.resolve())
    print("STATIC_PASS " + json.dumps(stats, ensure_ascii=False), flush=True)
    count, evidence = runtime_audit(args.pack_zip.resolve(), args.java.resolve(), args.server_jar.resolve(), args.phase)
    print(f"RUNTIME_PASS assertions={count} evidence={evidence}", flush=True)


if __name__ == "__main__":
    main()
