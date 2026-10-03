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
        unexpected.append(line)

    assert not unexpected, f"reset function has unrelated commands: {unexpected}"
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
    assert "loot replace entity" in api_resolve and "minecraft:silk_touch" in api_resolve
    assert "probe_max_stack" in api_resolve and "result.max_stack" in api_resolve
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

    print(f"PASS warehouse regression v{version}: reset/search/API/Highlight/Pick are bounded and validated")


if __name__ == "__main__":
    main()
