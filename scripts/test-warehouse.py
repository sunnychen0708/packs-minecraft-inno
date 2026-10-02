#!/usr/bin/env python3
"""Static regression checks for the Warehouse datapack."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datapacks/warehouse"

SPECIAL = ["00", "10", "20", "30", "40", "50", "60"]
MAIN = [f"{region}{slot}" for region in range(1, 7) for slot in range(1, 10)]
CODES = SPECIAL + MAIN


def main() -> None:
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

    load = (PACK / "data/warehouse/function/load.mcfunction").read_text(encoding="utf-8")
    assert "execute unless data storage warehouse:meta v42 run function warehouse:migrate_v42" in load
    assert "execute unless data storage warehouse:meta v43 run function warehouse:migrate_v43" in load

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
    assert "v4.2" in main_dialog
    assert "建築工具" in main_dialog
    assert "trigger copypaste set 1" in main_dialog

    api_highlight = (PACK / "data/warehouse/function/api/highlight.mcfunction").read_text(encoding="utf-8")
    highlight_box = (PACK / "data/warehouse/function/api/internal/highlight_box.mcfunction").read_text(encoding="utf-8")
    show_classified = (PACK / "data/warehouse/function/rule/show_classified.mcfunction").read_text(encoding="utf-8")
    assert "warehouse:chests c$(code)" in (PACK / "data/warehouse/function/api/highlight_slot.mcfunction").read_text(encoding="utf-8")
    assert "particle minecraft:end_rod" in highlight_box
    assert "force @s" in highlight_box
    assert "Highlight 箱子" in show_classified
    assert "trigger wh_highlight set 1" in show_classified

    print("PASS warehouse regression: reset/search/API/Highlight are bounded and validated")


if __name__ == "__main__":
    main()
