#!/usr/bin/env python3
"""Focused regression tests for UUID/entity/stat migration helpers."""
from __future__ import annotations

import gzip
import io
import json
import zlib

import nbtlib
from nbtlib.tag import IntArray, String

import exaroton_inno_uuid_migrate as migration
import exaroton_innotest as innotest


def raw_json(value):
    return (json.dumps(value, separators=(",", ":")) + "\n").encode("utf-8")


def counter(raw, category, key):
    value = json.loads(raw.decode("utf-8"))
    return value["stats"][category][key]


def nbt_bytes(old_uuid):
    root = nbtlib.File({
        "Owner": IntArray(migration.uuid_ints(old_uuid)),
        "OwnerString": String(old_uuid),
    })
    out = io.BytesIO()
    root.write(out)
    return out.getvalue()


def synthetic_region(old_uuid):
    payload = zlib.compress(nbt_bytes(old_uuid))
    chunk = migration.Chunk(
        index=0,
        timestamp=b"\x00\x00\x00\x01",
        compression_byte=2,
        payload=payload,
    )
    return migration.build_region({0: chunk})


def test_sum_stats():
    old = raw_json({
        "DataVersion": 1,
        "stats": {
            "minecraft:mined": {
                "minecraft:stone": 1000,
                "minecraft:diamond_ore": 2,
            }
        },
    })
    new = raw_json({
        "DataVersion": 2,
        "stats": {
            "minecraft:mined": {
                "minecraft:stone": 700,
                "minecraft:diamond_ore": 3,
                "minecraft:dirt": 9,
            }
        },
    })
    merged, changed = migration.merge_stats(old, new)
    assert changed
    assert counter(merged, "minecraft:mined", "minecraft:stone") == 1700
    assert counter(merged, "minecraft:mined", "minecraft:diamond_ore") == 5
    assert counter(merged, "minecraft:mined", "minecraft:dirt") == 9


def test_correct_legacy_max_without_losing_later_progress():
    old = raw_json({
        "stats": {
            "minecraft:mined": {
                "minecraft:stone": 1000,
                "minecraft:diamond_ore": 2,
            }
        }
    })
    pre_max_online = raw_json({
        "stats": {
            "minecraft:mined": {
                "minecraft:stone": 700,
                "minecraft:diamond_ore": 5,
            }
        }
    })
    # Legacy max result was stone=1000, diamond=5. The player then gained
    # another +50 stone and +3 diamond online before this corrective migration.
    current = raw_json({
        "stats": {
            "minecraft:mined": {
                "minecraft:stone": 1050,
                "minecraft:diamond_ore": 8,
            }
        }
    })
    merged, changed = migration.merge_stats_after_legacy_max(
        old, pre_max_online, current
    )
    assert changed
    assert counter(merged, "minecraft:mined", "minecraft:stone") == 1750
    assert counter(merged, "minecraft:mined", "minecraft:diamond_ore") == 10


def test_directional_region_uuid_rewrite():
    online = "ae8b11b9-09d0-47aa-bf70-76ba60a0e2f5"
    offline = innotest.offline_uuid("SunnyChen")
    int_map, str_map = migration.uuid_mappings([(online, offline)])
    region = synthetic_region(online)

    transformed, stats = migration.transform_region(
        region, int_mapping=int_map, str_mapping=str_map
    )
    assert transformed != region
    assert stats["changed_chunks"] == 1
    assert stats["int_array"] == 1
    assert stats["string"] == 1

    unchanged, remaining = migration.transform_region(
        transformed, int_mapping=int_map, str_mapping=str_map
    )
    assert unchanged == transformed
    assert remaining["changed_chunks"] == 0
    assert remaining["int_array"] == 0
    assert remaining["string"] == 0


def test_directional_player_nbt_uuid_rewrite():
    online = "1eecf8a9-2c2d-4c16-8736-eebdee687c28"
    offline = innotest.offline_uuid("penguin0531")
    int_map, str_map = migration.uuid_mappings([(online, offline)])
    original = gzip.compress(nbt_bytes(online))

    transformed, meta = migration.transform_player_nbt(
        original, int_mapping=int_map, str_mapping=str_map
    )
    assert transformed != original
    assert meta["int_array"] == 1
    assert meta["string"] == 1

    unchanged, remaining = migration.transform_player_nbt(
        transformed, int_mapping=int_map, str_mapping=str_map
    )
    assert unchanged == transformed
    assert not remaining["changed"]


class FakeInnotestClient:
    def __init__(self, region, include_empty=False):
        self.files = {"world/entities/r.0.0.mca": region}
        self.include_empty = include_empty
        if include_empty:
            self.files["world/entities/r.0.1.mca"] = b""
        self.writes = []

    def info_optional(self, path):
        if path == "world/entities":
            children = [
                {
                    "name": "r.0.0.mca",
                    "path": "world/entities/r.0.0.mca",
                    "isDirectory": False,
                }
            ]
            if self.include_empty:
                children.append({
                    "name": "r.0.1.mca",
                    "path": "world/entities/r.0.1.mca",
                    "isDirectory": False,
                })
            return {"children": children}
        if path in self.files:
            return {"size": len(self.files[path])}
        return None

    def read_file_optional(self, path):
        return self.files.get(path)

    def read_binary_file_optional(self, path):
        return self.files.get(path)

    def read_file(self, path):
        return self.files[path]

    def write_file(self, path, data):
        self.files[path] = data
        self.writes.append(path)


def test_innotest_entity_rewrite_backs_up_and_is_idempotent():
    online = "fa8e7183-bf37-4d9e-b327-58cd46d6dc11"
    offline = innotest.offline_uuid("geena0701")
    region = synthetic_region(online)
    client = FakeInnotestClient(region)

    result = innotest.rewrite_innotest_entity_uuid_refs(
        client, "world", [(online, offline)], 12345
    )
    assert result["region_files_scanned"] == 1
    assert result["region_files_changed"] == 1
    assert result["uuid_references_rewritten"] == 2
    assert "world/entities/r.0.0.mca.pre-inno-online-copy-12345.backup" in client.files

    second = innotest.rewrite_innotest_entity_uuid_refs(
        client, "world", [(online, offline)], 12346
    )
    assert second["region_files_changed"] == 0
    assert second["uuid_references_rewritten"] == 0


def test_innotest_empty_region_is_skipped_safely():
    online = "fa533e52-2ef3-49a2-8b74-7155a3251c9a"
    offline = innotest.offline_uuid("Felicitypeng")
    client = FakeInnotestClient(synthetic_region(online), include_empty=True)

    result = innotest.rewrite_innotest_entity_uuid_refs(
        client, "world", [(online, offline)], 54321
    )
    assert result["region_files_scanned"] == 2
    assert result["region_files_changed"] == 1
    assert result["uuid_references_rewritten"] == 2


def storage_dat(contents):
    root = nbtlib.File({"data": nbtlib.Compound({"contents": nbtlib.Compound(contents)}), "DataVersion": nbtlib.Int(5023)})
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb") as handle:
        root.write(handle)
    return out.getvalue()


def test_inno_storage_reports():
    from nbtlib.tag import Byte, Compound, Double, Int

    box = {"registered": Byte(1), "valid": Byte(1), "dimension": String("minecraft:overworld"),
           **{f"{h}_{a}": Int(1) for h in "ab" for a in "xyz"}}
    legacy = {"registered": Byte(1), "valid": Byte(1), "a_x": Int(1), "a_y": Int(2), "a_z": Int(3)}
    raw = storage_dat({
        "chests": Compound({"c00": Compound(box), "c10": Compound(legacy), "c11": Compound({"registered": Byte(0)})}),
        "meta": Compound({"v46": Byte(1)}),
    })
    report = innotest.warehouse_registration_report(innotest.command_storage_contents(raw))
    assert report["registered"] == 2
    assert report["registered_missing_fields"] == ["c10"]
    assert report["boxes"]["c10"]["missing"] == ["dimension", "b_x", "b_y", "b_z"]
    assert report["meta_flags"] == ["v46"]

    point = lambda x: Compound({"x": x, "y": Int(64), "z": Int(-3), "set": Byte(1)})
    raw = storage_dat({
        "players": Compound({"p1": Compound({"back": point(Int(5)), "custom": Compound({"s1": point(Double(5.5))})})}),
        "shared": Compound({"s1": point(Int(1))}),
    })
    report = innotest.utilities_waypoint_report(innotest.command_storage_contents(raw))
    assert report["locations"] == 3
    assert report["non_int_locations"] == [{"path": "players.p1.custom.s1", "types": {"x": "Double", "y": "Int", "z": "Int"}}]


def main():
    tests = [
        test_sum_stats,
        test_correct_legacy_max_without_losing_later_progress,
        test_directional_region_uuid_rewrite,
        test_directional_player_nbt_uuid_rewrite,
        test_innotest_entity_rewrite_backs_up_and_is_idempotent,
        test_innotest_empty_region_is_skipped_safely,
        test_inno_storage_reports,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS exaroton migration regressions: {len(tests)} tests")


if __name__ == "__main__":
    main()
