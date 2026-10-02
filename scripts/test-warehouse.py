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
    print("PASS warehouse regression: reset touches exactly registered/valid for all 61 slots")


if __name__ == "__main__":
    main()
