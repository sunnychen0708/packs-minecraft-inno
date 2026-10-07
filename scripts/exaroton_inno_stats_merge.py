#!/usr/bin/env python3
"""Stats-only correction for production offline/online UUID migration."""
from __future__ import annotations

import json
import os
import sys
import time
import uuid

import exaroton_inno_uuid_migrate as migration


def plan_or_apply(mode: str):
    if mode not in {"dry-run", "apply"}:
        raise migration.Error("mode must be dry-run or apply")

    client = migration.Client(os.environ.get("EXAROTON_API_TOKEN", ""))
    server = client.require_offline()
    props = client.read_file_optional("server.properties")
    if props is None:
        raise migration.Error("server.properties not found")
    world = migration.level_name(props)

    whitelist = migration.json_list(
        client.read_file_optional("whitelist.json"), "whitelist.json"
    )
    by_name = {
        str(entry.get("name") or "").lower(): str(entry.get("uuid") or "")
        for entry in whitelist
        if isinstance(entry, dict)
    }
    for name, (_, online_uuid) in migration.PLAYER_MAP.items():
        if migration.normalize_uuid_string(by_name.get(name.lower(), "")) != str(
            uuid.UUID(online_uuid)
        ):
            raise migration.Error(f"whitelist safety check failed for {name}")

    stats_root = f"{world}/players/stats"
    state_raw = client.read_file_optional(migration.STATS_SUM_STATE)
    state = migration._stats_sum_state(state_raw)
    state_players = state["players"]
    state_updates = {}
    changes = []
    players = {}

    for name, (offline_uuid, online_uuid) in migration.PLAYER_MAP.items():
        offline_path = f"{stats_root}/{offline_uuid}.json"
        online_path = f"{stats_root}/{online_uuid}.json"
        offline_raw = client.read_file_optional(offline_path)
        online_raw = client.read_file_optional(online_path)
        state_entry = state_players.get(name)
        legacy_backup = None

        if offline_raw is None:
            merged, changed = online_raw, False
            strategy = "no-offline-source"
        elif isinstance(state_entry, dict):
            recorded = str(state_entry.get("offline_stats_sha256") or "")
            actual = migration.sha256(offline_raw)
            if recorded != actual:
                raise migration.Error(
                    f"offline stats changed after summed migration for {name}; "
                    "refusing to add the historical source twice"
                )
            if online_raw is None:
                raise migration.Error(
                    f"online stats missing for {name} after summed migration state was recorded"
                )
            merged, changed = online_raw, False
            strategy = "already-summed"
        else:
            baseline = None
            if online_raw is not None:
                legacy_backup, baseline = migration.find_pre_migration_stats_backup(
                    client, stats_root, online_uuid
                )
            if online_raw is not None and baseline is not None:
                merged, changed = migration.merge_stats_after_legacy_max(
                    offline_raw, baseline, online_raw
                )
                strategy = "sum-corrected-from-legacy-max"
            else:
                merged, changed = migration.merge_stats(offline_raw, online_raw)
                strategy = "sum-per-counter"

            if merged is not None:
                state_updates[name] = {
                    "offline_stats_sha256": migration.sha256(offline_raw),
                    "target_online_uuid": str(uuid.UUID(online_uuid)),
                    "strategy": "sum-per-counter",
                }

        if merged is not None and changed:
            changes.append(
                (
                    online_path,
                    online_raw,
                    merged,
                    {
                        "player": name,
                        "strategy": strategy,
                        "legacy_pre_max_backup": legacy_backup,
                    },
                )
            )

        players[name] = {
            "offline_stats": offline_raw is not None,
            "online_stats": online_raw is not None,
            "strategy": strategy,
            "legacy_pre_max_stats_backup": legacy_backup,
            "will_write": bool(merged is not None and changed),
        }

    summary = {
        "mode": mode,
        "scope": "stats-only",
        "server": {"address": server.get("address"), "status": server.get("status")},
        "world": world,
        "strategy": "sum-per-counter",
        "stats_files_to_change": len(changes),
        "stats_sum_state_updates": sorted(state_updates),
        "players": players,
        "changes": [{"path": item[0], **item[3]} for item in changes],
    }

    if mode == "dry-run":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    client.require_offline()
    stamp = int(time.time())
    manifest = []
    for path, old, new, _ in changes:
        migration.backup_and_write(client, path, old, new, stamp, manifest)

    if state_updates:
        next_state = json.loads(json.dumps(state))
        next_players = next_state["players"]
        for name, entry in state_updates.items():
            next_players[name] = {**entry, "applied_at_unix": stamp}
        state_bytes = (
            json.dumps(next_state, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        migration.backup_and_write(
            client,
            migration.STATS_SUM_STATE,
            state_raw,
            state_bytes,
            stamp,
            manifest,
        )

    manifest_obj = {
        "created_at_unix": stamp,
        "scope": "stats-only",
        "stats_merge_strategy": "sum-per-counter",
        "stats_sum_state": migration.STATS_SUM_STATE,
        "writes": manifest,
    }
    manifest_path = f"uuid-stats-migration-{stamp}.json"
    client.write_file(
        manifest_path,
        (json.dumps(manifest_obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )

    summary["applied"] = True
    summary["backup_stamp"] = stamp
    summary["manifest"] = manifest_path
    summary["files_written"] = len(manifest)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: exaroton_inno_stats_merge.py dry-run|apply")
    try:
        plan_or_apply(sys.argv[1])
    except migration.Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
