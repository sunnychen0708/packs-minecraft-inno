#!/usr/bin/env python3
"""GET-only audit of cat and wolf Owner UUIDs on production inno."""
from __future__ import annotations

import io
import json
import os
import struct
import uuid
from collections import Counter

import nbtlib
from nbtlib.tag import IntArray, String

import exaroton_inno_uuid_migrate as migration


def decode_owner(value):
    if isinstance(value, IntArray) and len(value) == 4:
        return str(uuid.UUID(bytes=struct.pack(">iiii", *(int(v) for v in value))))
    if isinstance(value, String):
        return migration.normalize_uuid_string(str(value))
    return None


def scan_region(raw, path):
    rows = []
    for chunk in migration.parse_region(raw).values():
        root = nbtlib.File.parse(io.BytesIO(migration.decode_chunk(
            chunk.compression_byte, chunk.payload
        )))
        entities = root.get("Entities")
        if entities is None:
            raise migration.Error(f"Entities list missing in {path} chunk {chunk.index}")
        for entity in entities:
            if not isinstance(entity, nbtlib.tag.Compound):
                continue
            animal = str(entity.get("id", ""))
            if animal not in {"minecraft:wolf", "minecraft:cat"}:
                continue
            key = "Owner" if "Owner" in entity else (
                "OwnerUUID" if "OwnerUUID" in entity else None
            )
            pos = entity.get("Pos")
            rows.append({
                "animal": animal.removeprefix("minecraft:"),
                "owner": decode_owner(entity[key]) if key else None,
                "owner_tag": key,
                "owner_tag_type": type(entity[key]).__name__ if key else None,
                "position": [round(float(n), 1) for n in pos]
                if pos is not None and len(pos) == 3 else None,
                "region": path,
            })
    return rows


def audit_animal_owners(client=None):
    client = client or migration.Client(os.environ.get("EXAROTON_API_TOKEN", ""))
    # Intentionally no require_offline: GET-only, and no server power changes.
    server = client.target()
    props = client.read_file_optional("server.properties")
    if props is None:
        raise migration.Error("server.properties is missing")
    world = migration.level_name(props)
    region_paths = migration.list_region_files(client, world)
    label_by_uuid = {}
    for name, (old, new) in migration.PLAYER_MAP.items():
        label_by_uuid[str(uuid.UUID(old))] = f"{name}:offline"
        label_by_uuid[str(uuid.UUID(new))] = f"{name}:online"

    counts = Counter()
    owner_counts = Counter()
    examples = []
    unreadable = []
    read_regions = 0
    for path in region_paths:
        raw = client.read_file_optional(path)
        if not raw:
            # Never count an unavailable region as verified clean.
            unreadable.append(path)
            continue
        read_regions += 1
        for entry in scan_region(raw, path):
            owner = entry["owner"]
            player = label_by_uuid.get(owner)
            if entry["owner_tag"] is None:
                status = "wild-or-no-owner"
            elif owner is None:
                status = "unreadable-owner"
            elif player is None:
                status = "unknown-owner"
            elif player.endswith(":offline"):
                status = "old-offline-owner"
            else:
                status = "online-owner"
            counts[(entry["animal"], status)] += 1
            owner_counts[(entry["animal"], player or owner or status)] += 1
            if status not in {"online-owner", "wild-or-no-owner"} and len(examples) < 300:
                examples.append({**entry, "status": status, "player": player})

    report = {
        "operation": "read-only-animal-owner-audit",
        "server": {"address": server.get("address"), "status": server.get("status")},
        "world": world,
        "regions_listed": len(region_paths),
        "regions_read": read_regions,
        "unverified_regions": unreadable,
        "species_owner_status_counts": [
            {"species": species, "status": status, "count": count}
            for (species, status), count in sorted(counts.items())
        ],
        "species_owner_uuid_counts": [
            {"species": species, "owner": owner, "count": count}
            for (species, owner), count in sorted(owner_counts.items())
        ],
        "mismatched_owner_examples": examples,
        "examples_capped_at": 300,
        "warning": "When inno is online, loaded entities may differ from saved region files. Unverified regions cannot be treated as clean.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    audit_animal_owners()
