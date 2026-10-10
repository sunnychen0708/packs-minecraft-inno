#!/usr/bin/env python3
"""GET-only probe of exaroton region bytes after UUID migration."""
from __future__ import annotations

import hashlib
import json
import os

import exaroton_inno_uuid_migrate as migration
from inno_animal_owner_audit import scan_region

MANIFEST = "uuid-migration-1791312983.json"


def run():
    client = migration.Client(os.environ.get("EXAROTON_API_TOKEN", ""))
    server = client.target()
    mr = client.read_file_optional(MANIFEST)
    if not mr:
        raise migration.Error(f"missing {MANIFEST}")
    manifest = json.loads(mr.decode("utf-8"))
    entries = [x for x in manifest["writes"] if str(x.get("path", "")).endswith(".mca")]
    report = []
    for item in entries:
        p = str(item["path"])
        b = client.read_file_optional(p)
        info = client.info_optional(p)
        expected = item.get("new_sha256")
        diagnosis = {}
        if b:
            try:
                padded = b + bytes((-len(b)) % migration.SECTOR)
                for chunk in migration.parse_region(padded).values():
                    loc = int.from_bytes(b[chunk.index * 4:chunk.index * 4 + 4], "big")
                    offset = (loc >> 8) * migration.SECTOR
                    if offset + 5 + len(chunk.payload) > len(b):
                        raise migration.Error(f"chunk {chunk.index} goes beyond true file length")
                pets = scan_region(padded, p)
                owners = {}
                notable = []
                online = {player[1] for player in migration.PLAYER_MAP.values()}
                old = {player[0] for player in migration.PLAYER_MAP.values()}
                for pet in pets:
                    status = (
                        "no-owner" if not pet["owner"] else
                        "known-online" if pet["owner"] in online else
                        "known-old-offline" if pet["owner"] in old else "other-owner"
                    )
                    key = pet["animal"] + ":" + status
                    owners[key] = owners.get(key, 0) + 1
                    if status in {"known-old-offline", "other-owner"}:
                        notable.append({**pet, "owner_status": status})
                diagnosis = {
                    "species_by_owner_status": owners,
                    "unexpected_owner_pets": notable[:50],
                    "unexpected_owner_pets_truncated": len(notable) > 50,
                }
            except Exception as exc:
                diagnosis = {"read_only_parse_error": str(exc)}
        report.append({
            "read_only_pet_diagnosis": diagnosis,
            "path": p,
            "api_file_size": (info or {}).get("size"),
            "download_size": len(b) if b is not None else None,
            "size_mod_sector": len(b) % 4096 if b else None,
            "sha256_equals_2026_10_06_manifest": (
                hashlib.sha256(b).hexdigest() == expected if b is not None else None
            ),
            "first_16_bytes_hex": b[:16].hex() if b else None,
        })
    print(json.dumps({
        "operation": "read-only-region-integrity-probe",
        "server": {"address": server.get("address"), "status": server.get("status")},
        "manifest": MANIFEST,
        "modified_regions": report,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
