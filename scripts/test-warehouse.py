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

    api_refresh = (PACK / "data/warehouse/function/api/material_sources/refresh.mcfunction").read_text(encoding="utf-8")
    api_append = (PACK / "data/warehouse/function/api/material_sources/append.mcfunction").read_text(encoding="utf-8")
    exported_codes = re.findall(r'append \\{code:"(\\d{2})"\\}', api_refresh)
    assert exported_codes == CODES, "material source API must enumerate the canonical 61 Warehouse slots"
    assert "material_source_limit:64" in api_refresh
    assert "matches ..63" in api_refresh
    assert "{registered:1b,valid:1b}" in api_refresh
    assert "material_source_count" in api_refresh
    assert "material_sources append from storage warehouse:chests c$(code)" in api_append

    api_count = (PACK / "data/warehouse/function/api/count_item.mcfunction").read_text(encoding="utf-8")
    api_count_source = (PACK / "data/warehouse/function/api/internal/count_source.mcfunction").read_text(encoding="utf-8")
    api_count_loop = (PACK / "data/warehouse/function/api/internal/count_inv_loop.mcfunction").read_text(encoding="utf-8")
    assert "function warehouse:api/material_sources/refresh" in api_count
    assert "source_limit:64" in api_count
    assert "forceload query" in api_count_source
    assert "forceload add" in api_count_source
    assert "forceload remove" in api_count_source
    assert 'id:"$(item_id)"' in api_count_loop
    assert "result.available" in api_count
    assert "result.stale_sources" in api_count

    print("PASS warehouse regression: reset is scoped; search-index rebuild is bounded; shared material count API is present")


if __name__ == "__main__":
    main()
