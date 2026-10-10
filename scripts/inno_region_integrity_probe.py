#!/usr/bin/env python3
"""GET-only probe of exaroton region bytes after UUID migration."""
from __future__ import annotations

import hashlib
import json
import os

import exaroton_inno_uuid_migrate as migration

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
        report.append({
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
