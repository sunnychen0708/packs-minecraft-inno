#!/usr/bin/env python3
"""Static regression checks for the Warehouse datapack."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datapacks/warehouse"

SPECIAL = ["00", "10", "20", "30", "40", "50", "60"]
MAIN = [f"{region}{slot}" for region in range(1, 7) for slot in range(1, 10)]
CODES = SPECIAL + MAIN


def main() -> None:
    meta = json.loads((PACK / "pack.mcmeta").read_text(encoding="utf-8"))
    description = str(meta["pack"]["description"])
    version_match = re.search(r"v(\d+\.\d+(?:\.\d+)?)", description)
    assert version_match, f"pack description has no semantic version: {description}"
    version = version_match.group(1)
    readme = (PACK / "README.md").read_text(encoding="utf-8")
    assert readme.startswith(f"# Warehouse v{version}"), "README version must match pack.mcmeta"

    reset = PACK / "data/warehouse/function/admin/reset_registrations.mcfunction"
    text = reset.read_text(encoding="utf-8")

    assert "data remove storage warehouse:chests" not in text, "must not remove the storage root"

    pattern = re.compile(
        r"^data modify storage warehouse:chests c(\d{2})\.(registered|valid) set value 0b$"
    )
    seen: dict[str, set[str]] = {code: set() for code in CODES}
    unexpected: list[str] = []
    refreshes = 0

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.fullmatch(line)
        if match:
            code, field = match.groups()
            assert code in seen, f"unexpected warehouse slot c{code}"
            assert field not in seen[code], f"duplicate reset for c{code}.{field}"
            seen[code].add(field)
            continue
        if line == "dialog show @s warehouse:admin_reset":
            continue
        # v4.6: releasing the pack's own box-chunk force-loads is part of a reset.
        if line == "function warehouse:chunks/refresh":
            refreshes += 1
            continue
        unexpected.append(line)

    assert not unexpected, f"reset function has unrelated commands: {unexpected}"
    assert refreshes == 1, "reset must release the box-chunk force-loads exactly once"
    missing = {
        code: sorted({"registered", "valid"} - fields)
        for code, fields in seen.items()
        if fields != {"registered", "valid"}
    }
    assert not missing, f"incomplete registration reset: {missing}"
    assert sum(len(fields) for fields in seen.values()) == 122

    v14 = (PACK / "data/warehouse/function/migrate_v14.mcfunction").read_text(encoding="utf-8")
    v40 = (PACK / "data/warehouse/function/migrate_v40.mcfunction").read_text(encoding="utf-8")
    assert "function warehouse:search/index/init_" not in v14
    assert "function warehouse:search/index/init_" not in v40

    tick = (PACK / "data/warehouse/function/search/index/rebuild_tick.mcfunction").read_text(encoding="utf-8")
    calls = re.findall(r"function warehouse:search/index/init_(\d{3})", tick)
    assert calls == [f"{i:03d}" for i in range(72)], "search-index rebuild must dispatch exactly 000..071"
    assert "schedule function warehouse:search/index/rebuild_tick 1t replace" in tick

    run = (PACK / "data/warehouse/function/search/run.mcfunction").read_text(encoding="utf-8")
    assert "warehouse:meta search_ready" in run
    assert "return fail" in run

    setup = (PACK / "data/warehouse/function/setup.mcfunction").read_text(encoding="utf-8")
    warehouse_tick = (PACK / "data/warehouse/function/tick.mcfunction").read_text(encoding="utf-8")
    assert "scoreboard objectives add wh_search_page trigger" not in setup
    assert "scoreboard players enable @a wh_rename" in warehouse_tick

    load = (PACK / "data/warehouse/function/load.mcfunction").read_text(encoding="utf-8")
    assert "execute unless data storage warehouse:meta v42 run function warehouse:migrate_v42" in load
    assert "execute unless data storage warehouse:meta v43 run function warehouse:migrate_v43" in load
    current_marker = "v" + version.replace(".", "")
    assert f"warehouse:meta {current_marker}" in load, "current source version has no migration marker"
    assert f"warehouse:migrate_{current_marker}" in load, "current source version has no migration function"

    api_refresh = (PACK / "data/warehouse/function/api/material_sources/refresh.mcfunction").read_text(encoding="utf-8")
    api_append = (PACK / "data/warehouse/function/api/material_sources/append.mcfunction").read_text(encoding="utf-8")
    api_append_unique = (PACK / "data/warehouse/function/api/material_sources/append_unique.mcfunction").read_text(encoding="utf-8")
    exported_codes = re.findall(r'append \{code:"(\d{2})"\}', api_refresh)
    assert exported_codes == CODES, "material source API must enumerate the canonical 61 Warehouse slots"
    assert "material_source_limit:64" in api_refresh
    assert "matches ..63" in api_refresh
    assert "{registered:1b,valid:1b}" in api_refresh
    assert "material_source_count" in api_refresh
    assert "candidate_source set from storage warehouse:chests c$(code)" in api_append
    assert "append_unique" in api_append
    assert "material_sources append from storage warehouse:api work.candidate_source" in api_append_unique
    assert "a_x:$(b_x)" in api_append_unique and "b_x:$(a_x)" in api_append_unique

    api_count = (PACK / "data/warehouse/function/api/count_item.mcfunction").read_text(encoding="utf-8")
    api_count_source = (PACK / "data/warehouse/function/api/internal/count_source.mcfunction").read_text(encoding="utf-8")
    api_count_loop = (PACK / "data/warehouse/function/api/internal/count_inv_loop.mcfunction").read_text(encoding="utf-8")
    api_count_stack = (PACK / "data/warehouse/function/api/internal/count_stack.mcfunction").read_text(encoding="utf-8")
    api_take = (PACK / "data/warehouse/function/api/take_item.mcfunction").read_text(encoding="utf-8")
    api_take_stack = (PACK / "data/warehouse/function/api/internal/take_stack.mcfunction").read_text(encoding="utf-8")
    api_refund = (PACK / "data/warehouse/function/api/refund_item.mcfunction").read_text(encoding="utf-8")
    api_refund_entry = (PACK / "data/warehouse/function/api/internal/refund_entry.mcfunction").read_text(encoding="utf-8")
    api_refund_finalize = (PACK / "data/warehouse/function/api/internal/refund_finalize.mcfunction").read_text(encoding="utf-8")
    api_pending_tick = (PACK / "data/warehouse/function/api/pending_refunds/tick.mcfunction").read_text(encoding="utf-8")
    assert "function warehouse:api/material_sources/refresh" in api_count
    assert "source_limit:64" in api_count
    assert "forceload query" in api_count_source
    assert "forceload add" in api_count_source
    assert "forceload remove" in api_count_source
    assert "unless loaded" not in api_count_source
    assert 'id:"$(item_id)"' in api_count_stack
    assert "data get storage warehouse:api work.stack.components" in api_count_stack
    assert "result.available" in api_count
    assert "result.stale_sources" in api_count
    assert "function warehouse:api/count_item" in api_take
    assert "insufficient_stock" in api_take
    assert "source_unavailable" in api_take
    assert "data get storage warehouse:api work.stack.components" in api_take_stack
    assert "container.$(api_slot)" in api_take_stack
    assert "warehouse:chests c00" in api_refund
    assert "function warehouse:sort/transport/main" in api_refund_entry
    assert "probe_max_stack" in api_refund_entry
    assert "entry_full" in api_refund_entry
    assert "scoreboard players set #api_plain wh_tmp 1" in api_refund_entry
    assert "warehouse:sort/transport/main_valid" in api_refund_entry
    assert "pending_refunds append" in api_refund_finalize
    assert "result.queued" in api_refund_finalize
    assert "pending_refunds[0]" in api_pending_tick
    assert "work.saved_result" in api_pending_tick

    # v4.5 compact hot path: arithmetic direct dispatch replaces 61-way chest and 54-way slot scans.
    compact_step = (PACK / "data/warehouse/function/compact/step.mcfunction").read_text(encoding="utf-8")
    compact_dispatch = (PACK / "data/warehouse/function/compact/dispatch_code.mcfunction").read_text(encoding="utf-8")
    compact_load = (PACK / "data/warehouse/function/compact/load_code.mcfunction").read_text(encoding="utf-8")
    compact_slot = (PACK / "data/warehouse/function/compact/slot.mcfunction").read_text(encoding="utf-8")
    expected_compact_codes = ["00"] + [f"{n:02d}" for n in range(10, 70)]
    actual_compact_codes = ["00" if code == 0 else f"{code + 9:02d}" for code in range(61)]
    assert actual_compact_codes == expected_compact_codes, "compact arithmetic code mapping must preserve c00,c10..c69"
    expected_slots = [("a", slot) if slot <= 26 else ("b", slot - 27) for slot in range(54)]
    assert expected_slots == [("a", i) for i in range(27)] + [("b", i) for i in range(27)]
    assert compact_step.count("warehouse:compact/load_code") == 1, "only c00 should use the direct special case"
    assert "matches 1..60 run function warehouse:compact/dispatch_code" in compact_step
    assert "scoreboard players add #compact_target wh_tmp 9" in compact_step
    assert "c$(target){registered:1b,valid:1b}" in compact_dispatch
    assert "function warehouse:compact/load_code with storage warehouse:chests c$(target)" in compact_dispatch
    assert "function warehouse:compact/slot_dispatch" not in compact_load
    assert "scoreboard players remove #compact_local wh_tmp 27" in compact_load
    assert "warehouse:runtime compact.slot" in compact_load
    assert compact_load.count("matches ..26") == 3 and compact_load.count("matches 27..") == 4
    assert "container.$(slot)" in compact_slot
    assert "Items[{Slot:$(slot)b}]" in compact_slot
    assert "scoreboard players operation #compact_src wh_tmp = #compact_slot wh_tmp" in compact_slot
    assert "$execute in $(dimension) run data modify storage warehouse:runtime move.stack set from block" in compact_slot
    # Every shared merge reader must use its destination dimension, including
    # main/overflow A/B halves. Compact runs from the overworld tick context.
    merge_readers = list((PACK / "data/warehouse/function/sort/transport").glob("merge_*.mcfunction"))
    dimension_reads = 0
    for path in merge_readers:
        for line in path.read_text(encoding="utf-8").splitlines():
            if "move.candidate set from block" in line:
                dimension = "ov_dimension" if path.name.startswith("merge_o") else "dest_dimension"
                assert line.startswith(f"$execute in $({dimension}) run "), path
                dimension_reads += 1
    assert dimension_reads == 108
    compact_dir = PACK / "data/warehouse/function/compact"
    assert not (compact_dir / "slot_dispatch.mcfunction").exists(), "legacy 54-way slot dispatcher must be removed"
    assert not list(compact_dir.glob("slot_[0-9][0-9].mcfunction")), "legacy per-slot compact handlers must be removed"

    main_dialog = (PACK / "data/warehouse/dialog/main.json").read_text(encoding="utf-8")
    assert f"v{version}" in main_dialog
    assert "建築工具" in main_dialog
    assert "trigger copypaste set 1" in main_dialog

    api_highlight = (PACK / "data/warehouse/function/api/highlight.mcfunction").read_text(encoding="utf-8")
    highlight_slot = (PACK / "data/warehouse/function/api/highlight_slot.mcfunction").read_text(encoding="utf-8")
    highlight_box = (PACK / "data/warehouse/function/api/internal/highlight_box.mcfunction").read_text(encoding="utf-8")
    show_classified = (PACK / "data/warehouse/function/rule/show_classified.mcfunction").read_text(encoding="utf-8")
    assert "warehouse:chests c$(code)" in highlight_slot
    assert highlight_slot.splitlines()[0] == "data remove storage warehouse:api work.highlight"
    assert all(not line.startswith("$") or "$(" in line for line in highlight_slot.splitlines()), "Highlight macro lines must reference a macro variable"
    assert "return run function warehouse:api/highlight_slot with storage warehouse:api request" in api_highlight
    assert "particle minecraft:end_rod" in highlight_box
    assert "force @s" in highlight_box
    assert "Highlight 箱子" in show_classified
    assert "trigger wh_highlight set 1" in show_classified
    select_search = (PACK / "data/warehouse/function/rule/select_search.mcfunction").read_text(encoding="utf-8")
    show_selected = (PACK / "data/warehouse/function/rule/show_selected.mcfunction").read_text(encoding="utf-8")
    highlight_from_rule = (PACK / "data/warehouse/function/highlight/from_rule.mcfunction").read_text(encoding="utf-8")
    assert "scores={wh_search_pick=1..1544}" in warehouse_tick and "warehouse:rule/select_search" in warehouse_tick
    assert "function warehouse:rule/show_selected" in select_search
    assert "function warehouse:rule/show_classified" in show_selected
    assert "scores={wh_highlight=1..}" in warehouse_tick and "warehouse:highlight/from_rule" in warehouse_tick
    assert "wh_rulebox matches 10..69" in highlight_from_rule
    assert "function warehouse:api/highlight" in highlight_from_rule

    # Phase 4 Pick / block resolver.
    api_resolve = (PACK / "data/warehouse/function/api/resolve_block.mcfunction").read_text(encoding="utf-8")
    pick_start = (PACK / "data/warehouse/function/pick/start.mcfunction").read_text(encoding="utf-8")
    pick_raycast = (PACK / "data/warehouse/function/pick/raycast.mcfunction").read_text(encoding="utf-8")
    pick_hit = (PACK / "data/warehouse/function/pick/hit.mcfunction").read_text(encoding="utf-8")
    pick_withdraw = (PACK / "data/warehouse/function/pick/withdraw.mcfunction").read_text(encoding="utf-8")
    pick_take = (PACK / "data/warehouse/function/pick/take.mcfunction").read_text(encoding="utf-8")
    pick_give = (PACK / "data/warehouse/function/pick/give.mcfunction").read_text(encoding="utf-8")
    pick_from_item = (PACK / "data/warehouse/function/pick/from_item.mcfunction").read_text(encoding="utf-8")
    show_unclassified = (PACK / "data/warehouse/function/rule/show_unclassified.mcfunction").read_text(encoding="utf-8")
    assert setup.count("scoreboard objectives add pick trigger") == 1
    assert "warehouse:meta v44" in load and "warehouse:migrate_v44" in load
    assert warehouse_tick.count("scoreboard players enable @a pick") == 1
    assert "scores={pick=1..}" in warehouse_tick and "warehouse:pick/start" in warehouse_tick
    assert "trigger pick" in main_dialog and "Pick 一組" in main_dialog
    assert 'minecraft:enchantments={"minecraft:silk_touch":1}' in api_resolve
    assert "probe_max_stack" in api_resolve and "result.max_stack" in api_resolve
    assert "data remove storage warehouse:pick\n" not in pick_start
    assert "data remove storage warehouse:pick request" in pick_start
    assert "data remove storage warehouse:pick result" in pick_start
    assert "anchored eyes" in pick_start and "warehouse:pick/raycast" in pick_start
    assert "minecraft:water" in pick_raycast and "minecraft:lava" in pick_raycast
    assert "warehouse:api/resolve_block" in pick_hit
    assert "warehouse:api/count_item" in pick_withdraw
    assert "warehouse:api/take_item" in pick_take
    assert "entity @s[type=minecraft:player]" in pick_take
    assert "$give @s $(item_id) $(count)" in pick_give
    assert "probe_max_stack" in pick_from_item and "warehouse:pick/withdraw" in pick_from_item
    assert "warehouse:pick/from_item" in show_classified and "取一組" in show_classified
    assert "warehouse:pick/from_item" in show_unclassified and "取一組" in show_unclassified

    # v4.5: three-column box lists fit a narrow window, and pages about one box go back to
    # the list the box was picked from (wh_back via nav 9), not to the top of the section.
    fn = PACK / "data/warehouse/function"
    for page in list(fn.rglob("*_render.mcfunction")):
        text = page.read_text(encoding="utf-8")
        if '"columns":3' in text:
            assert '"width":150' not in text, f"{page.name}: three-column buttons wider than 120"
    nav = (fn / "ui/nav.mcfunction").read_text(encoding="utf-8")
    assert "wh_nav matches 9 run return run function warehouse:ui/back" in nav
    for n, dlg in ((17, "register/special"), (37, "view/special"), (57, "unregister/special"), (67, "boxname/special")):
        assert f"wh_nav matches {n} run dialog show @s warehouse:{dlg}" in nav
    assert "scoreboard objectives add wh_back dummy" in load
    for f, base in (("ui/select_code", 10), ("view/dispatch", 30), ("unregister/prepare", 50), ("boxname/select", 60)):
        text = (fn / f"{f}.mcfunction").read_text(encoding="utf-8")
        assert f"#bbase wh_tmp {base}" in text and "warehouse:ui/back_from_code" in text, f
    for f in ("ui/show_armed", "register/show_success", "register/show_duplicate_dialog", "unregister/show_done",
              "boxname/show_prepare", "boxname/show_saved", "view/page/empty", "view/page/p1_last", "view/page/p2_next"):
        assert "trigger wh_nav set 9" in (fn / f"{f}.mcfunction").read_text(encoding="utf-8"), f
    assert '"no":{"label":{"text":"取消"}' in (fn / "unregister/confirm_52_render.mcfunction").read_text(encoding="utf-8")
    assert "trigger wh_nav set 9" in (fn / "unregister/confirm_52_render.mcfunction").read_text(encoding="utf-8")
    for f in ("view/error_inaccessible", "view/error_unregistered", "unregister/not_registered"):
        assert "trigger wh_nav set 9" in (PACK / f"data/warehouse/dialog/{f}.json").read_text(encoding="utf-8"), f
    assert "trigger wh_nav set 17" in (PACK / "data/warehouse/dialog/register/armed_00.json").read_text(encoding="utf-8")
    assert "trigger wh_nav set 61" in (PACK / "data/warehouse/dialog/boxname/input_13.json").read_text(encoding="utf-8")
    assert "trigger wh_nav set 67" in (PACK / "data/warehouse/dialog/boxname/input_10.json").read_text(encoding="utf-8")

    # Pages stay centred only if nothing is wider than 390; 入口箱 sits under 區域 1-6;
    # "回主選單" opens the same main page as the G quick action.
    for page in list((PACK / "data/warehouse/dialog").rglob("*.json")) + list(fn.rglob("*.mcfunction")):
        for w in re.findall(r'"width":\s*(\d+)', page.read_text(encoding="utf-8")):
            assert int(w) <= 390, f"{page.name}: width {w} pushes the Dialog off centre"
    for f in ("view/index", "register", "unregister/index", "boxname/index"):
        acts = json.loads((PACK / f"data/warehouse/dialog/{f}.json").read_text(encoding="utf-8"))["actions"]
        assert [a["label"]["text"] for a in acts] == [f"區域 {i}" for i in range(1, 7)] + ["入口箱"], f
    assert "wh_nav matches 1 run dialog show @s warehouse:main" in nav

    # Issue #72: G management page must actually expose the 01–05 bag
    # dialogs; all button actions must map to the right trigger value.
    dialog_dir = PACK / "data/warehouse/dialog"
    manage = json.loads((dialog_dir / "manage.json").read_text(encoding="utf-8"))
    assert any(
        a.get("label", {}).get("text") == "背包箱 (01–05)"
        and a.get("action") == {"type": "show_dialog", "dialog": "warehouse:bag/manage"}
        for a in manage["actions"]
    ), "G box management must expose the bag menu"
    bag_manage = json.loads((dialog_dir / "bag/manage.json").read_text(encoding="utf-8"))
    destinations = [a["action"].get("dialog") for a in bag_manage["actions"]]
    assert destinations == ["warehouse:bag/register", "warehouse:bag/unregister", "warehouse:bag/help"]
    for dialog_name, objective in (("register", "wh_bag_reg"), ("unregister", "wh_bag_unreg")):
        dialog = json.loads((dialog_dir / f"bag/{dialog_name}.json").read_text(encoding="utf-8"))
        assert [a["label"]["text"] for a in dialog["actions"]] == [
            f"{i:02d}-{side}" for i in range(1, 6) for side in ("A", "B")
        ], f"incorrect {dialog_name} choices"
        assert [a["action"]["command"] for a in dialog["actions"]] == [
            f"trigger {objective} set {i}" for i in range(1, 11)
        ], f"incorrect {dialog_name} trigger mappings"
    bag_load = (fn / "bag/load.mcfunction").read_text(encoding="utf-8")
    bag_tick = (fn / "bag/tick.mcfunction").read_text(encoding="utf-8")
    for trigger in ("bag", "sbag", "wh_bag_reg", "wh_bag_unreg"):
        assert f"scoreboard objectives add {trigger} trigger" in bag_load
        assert f"scoreboard players enable @a {trigger}" in bag_tick
    right_click = (fn / "register/on_use.mcfunction").read_text(encoding="utf-8")
    assert "warehouse:bag/register/on_use" in right_click, "physical chest use must invoke bag raycast"
    assert "advancement revoke @s only warehouse:register_chest" in right_click
    bag_raycast = (fn / "bag/register/raycast.mcfunction").read_text(encoding="utf-8")
    assert "#warehouse:storage_chests[type=single]" in bag_raycast
    assert "warehouse:bag/register/hit" in bag_raycast
    assert '"actions": []' not in (dialog_dir / "bag/help.json").read_text(encoding="utf-8")

    print(f"PASS warehouse regression v{version}: reset/search/API/Highlight/Pick are bounded and validated")


if __name__ == "__main__":
    main()
