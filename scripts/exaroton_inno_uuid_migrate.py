#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zlib
from dataclasses import dataclass
from pathlib import PurePosixPath

import nbtlib
from nbtlib.tag import Compound, IntArray, List, String

API = "https://api.exaroton.com/v1"
TARGET = "inno.exaroton.me"
STATUS_OFFLINE = 0
SECTOR = 4096
HEADER = SECTOR * 2

PLAYER_MAP = {
    "SunnyChen": (
        "eb6da107-87ee-381c-8df9-c31fbaad0c19",
        "ae8b11b9-09d0-47aa-bf70-76ba60a0e2f5",
    ),
    "penguin0531": (
        "4b653253-aaa4-34b7-b040-6edb74147f1c",
        "1eecf8a9-2c2d-4c16-8736-eebdee687c28",
    ),
    "geena0701": (
        "1d91b447-2c78-323b-8bf1-973edae1911a",
        "fa8e7183-bf37-4d9e-b327-58cd46d6dc11",
    ),
    "Felicitypeng": (
        "81409b70-88c3-33d9-bdac-103b0a5d404b",
        "fa533e52-2ef3-49a2-8b74-7155a3251c9a",
    ),
}
TYPO_NAME = "penguin531"
TYPO_UUID = "5cf4b9f3-ae26-4afc-bc45-e575d125ecf4"


class Error(RuntimeError):
    pass


def addr(v):
    return str(v or "").strip().rstrip(".").lower()


def remote_path(p: str) -> str:
    x = PurePosixPath(p)
    if x.is_absolute() or not x.parts or any(i in ("", ".", "..") for i in x.parts):
        raise Error(f"unsafe remote path: {p!r}")
    return "/".join(urllib.parse.quote(i, safe="") for i in x.parts)


class Client:
    """Production-inno client. It intentionally implements no start/stop/command methods."""

    def __init__(self, token: str, opener=urllib.request.urlopen):
        if not token.strip():
            raise Error("EXAROTON_API_TOKEN is not configured")
        self.token = token.strip()
        self.opener = opener
        self._sid = None

    def req(self, method: str, path: str, *, raw=None, raw_response=False):
        if method not in {"GET", "PUT"}:
            raise Error(f"method blocked by maintenance client: {method}")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "packs-minecraft-inno/1 inno-offline-uuid-maintenance",
        }
        if raw is not None:
            headers["Content-Type"] = "application/octet-stream"
        request = urllib.request.Request(API + path, data=raw, headers=headers, method=method)
        try:
            with self.opener(request, timeout=60) as response:
                data = response.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            raise Error(f"exaroton HTTP {e.code}: {detail or e.reason}") from e
        except urllib.error.URLError as e:
            raise Error(f"cannot reach exaroton API: {e.reason}") from e
        if raw_response:
            return data
        if not data:
            return None
        try:
            result = json.loads(data.decode())
        except Exception as e:
            raise Error("exaroton returned invalid JSON") from e
        if isinstance(result, dict) and result.get("success") is False:
            raise Error(f"exaroton error: {result.get('error') or 'unknown'}")
        return result.get("data") if isinstance(result, dict) and "data" in result else result

    def target(self):
        servers = self.req("GET", "/servers/")
        matches = [s for s in servers if isinstance(s, dict) and addr(s.get("address")) == TARGET]
        if len(matches) != 1:
            raise Error(f"safety lock: expected exactly one {TARGET}, found {len(matches)}")
        sid = matches[0].get("id")
        if not sid:
            raise Error("safety lock: inno has no server id")
        server = self.req("GET", f"/servers/{urllib.parse.quote(str(sid), safe='')}")
        if addr(server.get("address")) != TARGET:
            raise Error("safety lock: production target verification failed")
        self._sid = sid
        return server

    def require_offline(self):
        server = self.target()
        status = int(server.get("status", -1))
        if status != STATUS_OFFLINE:
            raise Error(f"refusing production maintenance: {TARGET} status is {status}, not OFFLINE")
        return server

    def _sidq(self):
        if self._sid is None:
            self.target()
        return urllib.parse.quote(str(self._sid), safe="")

    def read_file_optional(self, path: str):
        try:
            return self.req(
                "GET",
                f"/servers/{self._sidq()}/files/data/{remote_path(path)}/",
                raw_response=True,
            )
        except Error as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def info_optional(self, path: str):
        try:
            return self.req(
                "GET",
                f"/servers/{self._sidq()}/files/info/{remote_path(path)}/",
            )
        except Error as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def write_file(self, path: str, data: bytes):
        self.require_offline()
        self.req(
            "PUT",
            f"/servers/{self._sidq()}/files/data/{remote_path(path)}/",
            raw=data,
        )


def level_name(raw: bytes) -> str:
    result = "world"
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.strip().startswith("level-name="):
            result = line.split("=", 1)[1].strip() or "world"
            break
    remote_path(result)
    return result


def child_list(info):
    if not isinstance(info, dict):
        return []
    children = info.get("children")
    return children if isinstance(children, list) else []


def walk_dirs(client: Client, root: str, wanted_basename: str):
    info = client.info_optional(root)
    if info is None:
        return []
    found = []
    stack = [(root, info)]
    while stack:
        path, cur = stack.pop()
        if PurePosixPath(path).name == wanted_basename:
            found.append(path)
            continue
        for child in child_list(cur):
            if not isinstance(child, dict) or not child.get("isDirectory"):
                continue
            cpath = str(child.get("path") or "")
            if not cpath:
                name = str(child.get("name") or "")
                if not name:
                    continue
                cpath = f"{path}/{name}"
            cinfo = client.info_optional(cpath)
            if cinfo is not None:
                stack.append((cpath, cinfo))
    return found


def list_region_files(client: Client, world: str):
    dirs = []
    for p in (f"{world}/entities", f"{world}/DIM-1/entities", f"{world}/DIM1/entities"):
        if client.info_optional(p) is not None:
            dirs.append(p)
    custom_root = f"{world}/dimensions"
    if client.info_optional(custom_root) is not None:
        dirs.extend(walk_dirs(client, custom_root, "entities"))
    out = []
    for d in sorted(set(dirs)):
        info = client.info_optional(d)
        for child in child_list(info):
            if not isinstance(child, dict) or child.get("isDirectory"):
                continue
            name = str(child.get("name") or "")
            path = str(child.get("path") or "")
            if not path and name:
                path = f"{d}/{name}"
            if path.endswith(".mca"):
                out.append(path)
    return sorted(set(out))


def uuid_ints(value: str):
    return struct.unpack(">iiii", uuid.UUID(value).bytes)


def normalize_uuid_string(value: str):
    try:
        return str(uuid.UUID(str(value)))
    except Exception:
        return None


def uuid_mappings(pairs):
    """Build NBT UUID mappings from an iterable of (old_uuid, new_uuid) pairs."""
    normalized = [(str(uuid.UUID(old)), str(uuid.UUID(new))) for old, new in pairs]
    return (
        {uuid_ints(old): uuid_ints(new) for old, new in normalized},
        {old: new for old, new in normalized},
    )


INT_MAPPING, STR_MAPPING = uuid_mappings(PLAYER_MAP.values())


def replace_uuid_refs(node, counts, int_mapping=None, str_mapping=None):
    """Recursively replace exact player UUID values in NBT, regardless of key name."""
    int_mapping = INT_MAPPING if int_mapping is None else int_mapping
    str_mapping = STR_MAPPING if str_mapping is None else str_mapping
    changed = False
    if isinstance(node, Compound):
        for key in list(node.keys()):
            value = node[key]
            if isinstance(value, IntArray) and len(value) == 4:
                old_tuple = tuple(int(x) for x in value)
                if old_tuple in int_mapping:
                    node[key] = IntArray(int_mapping[old_tuple])
                    counts["int_array"] += 1
                    changed = True
                    continue
            if isinstance(value, String):
                normalized = normalize_uuid_string(str(value))
                if normalized in str_mapping:
                    node[key] = String(str_mapping[normalized])
                    counts["string"] += 1
                    changed = True
                    continue
            if isinstance(value, (Compound, List)):
                if replace_uuid_refs(value, counts, int_mapping, str_mapping):
                    changed = True
    elif isinstance(node, List):
        for idx, value in enumerate(list(node)):
            if isinstance(value, IntArray) and len(value) == 4:
                old_tuple = tuple(int(x) for x in value)
                if old_tuple in int_mapping:
                    node[idx] = IntArray(int_mapping[old_tuple])
                    counts["int_array"] += 1
                    changed = True
                    continue
            if isinstance(value, String):
                normalized = normalize_uuid_string(str(value))
                if normalized in str_mapping:
                    node[idx] = String(str_mapping[normalized])
                    counts["string"] += 1
                    changed = True
                    continue
            if isinstance(value, (Compound, List)):
                if replace_uuid_refs(value, counts, int_mapping, str_mapping):
                    changed = True
    return changed


@dataclass
class Chunk:
    index: int
    timestamp: bytes
    compression_byte: int
    payload: bytes
    changed: bool = False


def decode_chunk(compression_byte: int, payload: bytes):
    if compression_byte & 0x80:
        raise Error("external region chunks are not supported; refusing to modify")
    scheme = compression_byte & 0x7F
    if scheme == 1:
        return gzip.decompress(payload)
    if scheme == 2:
        return zlib.decompress(payload)
    if scheme == 3:
        return payload
    raise Error(f"unsupported region compression scheme {scheme}; refusing to modify")


def encode_chunk(compression_byte: int, raw: bytes):
    scheme = compression_byte & 0x7F
    if scheme == 1:
        return gzip.compress(raw)
    if scheme == 2:
        return zlib.compress(raw)
    if scheme == 3:
        return raw
    raise Error(f"unsupported region compression scheme {scheme}; refusing to modify")


def parse_region(data: bytes):
    if len(data) < HEADER or len(data) % SECTOR != 0:
        raise Error(f"invalid region length {len(data)}")
    chunks = {}
    for i in range(1024):
        loc = int.from_bytes(data[i * 4:i * 4 + 4], "big")
        offset = loc >> 8
        sectors = loc & 0xFF
        if offset == 0 and sectors == 0:
            continue
        if offset < 2 or sectors < 1:
            raise Error(f"invalid region location entry at chunk {i}")
        pos = offset * SECTOR
        if pos + 5 > len(data):
            raise Error(f"truncated chunk header at index {i}")
        length = int.from_bytes(data[pos:pos + 4], "big")
        if length < 1 or length > sectors * SECTOR - 4:
            raise Error(f"invalid chunk length at index {i}")
        compression_byte = data[pos + 4]
        payload = data[pos + 5:pos + 4 + length]
        ts = data[SECTOR + i * 4:SECTOR + i * 4 + 4]
        chunks[i] = Chunk(i, ts, compression_byte, payload)
    return chunks


def build_region(chunks):
    locations = bytearray(SECTOR)
    timestamps = bytearray(SECTOR)
    body = bytearray()
    next_sector = 2
    for i in range(1024):
        chunk = chunks.get(i)
        if chunk is None:
            continue
        record = len(chunk.payload) + 1
        blob = record.to_bytes(4, "big") + bytes([chunk.compression_byte]) + chunk.payload
        sectors = (len(blob) + SECTOR - 1) // SECTOR
        if sectors > 255:
            raise Error(f"chunk {i} exceeds region sector-count limit after rewrite")
        locations[i * 4:i * 4 + 4] = ((next_sector << 8) | sectors).to_bytes(4, "big")
        timestamps[i * 4:i * 4 + 4] = chunk.timestamp
        body.extend(blob)
        body.extend(b"\x00" * (sectors * SECTOR - len(blob)))
        next_sector += sectors
    return bytes(locations + timestamps + body)


def transform_region(data: bytes, int_mapping=None, str_mapping=None):
    chunks = parse_region(data)
    total_counts = {"int_array": 0, "string": 0}
    changed_chunks = 0
    for chunk in chunks.values():
        raw = decode_chunk(chunk.compression_byte, chunk.payload)
        try:
            nbt = nbtlib.File.parse(io.BytesIO(raw))
        except Exception as e:
            raise Error(f"NBT parse failed in region chunk {chunk.index}: {e}") from e
        counts = {"int_array": 0, "string": 0}
        changed = replace_uuid_refs(nbt, counts, int_mapping, str_mapping)
        if not changed:
            continue
        out = io.BytesIO()
        nbt.write(out)
        chunk.payload = encode_chunk(chunk.compression_byte, out.getvalue())
        chunk.changed = True
        changed_chunks += 1
        total_counts["int_array"] += counts["int_array"]
        total_counts["string"] += counts["string"]
    if not changed_chunks:
        return data, {"changed_chunks": 0, **total_counts}
    return build_region(chunks), {"changed_chunks": changed_chunks, **total_counts}


def transform_player_nbt(data: bytes, int_mapping=None, str_mapping=None):
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data), mode="rb") as gz:
            raw = gz.read()
    except OSError:
        raw = data
    nbt = nbtlib.File.parse(io.BytesIO(raw))
    counts = {"int_array": 0, "string": 0}
    if not replace_uuid_refs(nbt, counts, int_mapping, str_mapping):
        return data, {"changed": False, **counts}
    out = io.BytesIO()
    nbt.write(out)
    raw_out = out.getvalue()
    if data[:2] == b"\x1f\x8b":
        raw_out = gzip.compress(raw_out)
    return raw_out, {"changed": True, **counts}


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _stats_doc(raw: bytes | None):
    if raw is None:
        return None
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise Error("stats JSON must be an object")
    return value


def _counter_value(doc, category, key):
    if not isinstance(doc, dict):
        return 0
    stats = doc.get("stats")
    if not isinstance(stats, dict):
        return 0
    entries = stats.get(category)
    if not isinstance(entries, dict):
        return 0
    value = entries.get(key)
    return value if _number(value) else 0


def _all_counter_keys(*docs):
    result = set()
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        stats = doc.get("stats")
        if not isinstance(stats, dict):
            continue
        for category, entries in stats.items():
            if not isinstance(entries, dict):
                continue
            for key, value in entries.items():
                if _number(value):
                    result.add((category, key))
    return sorted(result)


def _write_counter(doc, category, key, value):
    stats = doc.setdefault("stats", {})
    if not isinstance(stats, dict):
        raise Error("stats JSON field 'stats' must be an object")
    entries = stats.setdefault(category, {})
    if not isinstance(entries, dict):
        raise Error(f"stats category {category!r} must be an object")
    entries[key] = value


def merge_stats(old_raw: bytes | None, new_raw: bytes | None):
    """Merge disjoint offline/online play history by summing numeric counters."""
    if old_raw is None:
        return new_raw, False
    if new_raw is None:
        return old_raw, True
    old = _stats_doc(old_raw)
    new = _stats_doc(new_raw)
    changed = False
    for category, key in _all_counter_keys(old):
        old_value = _counter_value(old, category, key)
        current = _counter_value(new, category, key)
        merged = current + old_value
        if current != merged:
            _write_counter(new, category, key, merged)
            changed = True
    if not changed:
        return new_raw, False
    return (json.dumps(new, ensure_ascii=False, separators=(",", ":")) + "\n").encode(), True


def merge_stats_after_legacy_max(
    old_raw: bytes,
    pre_max_online_raw: bytes,
    current_online_raw: bytes,
):
    """Correct a previous max-per-counter merge without losing later online progress.

    Previous code produced max(offline, online). The first migration backup contains
    the original online counters. Any growth above that legacy max is post-migration
    play and is preserved while rebuilding the desired offline + online total.
    """
    old = _stats_doc(old_raw)
    baseline = _stats_doc(pre_max_online_raw)
    current = _stats_doc(current_online_raw)
    changed = False
    for category, key in _all_counter_keys(old, baseline, current):
        old_value = _counter_value(old, category, key)
        baseline_value = _counter_value(baseline, category, key)
        current_value = _counter_value(current, category, key)
        legacy_max = max(old_value, baseline_value)
        later_progress = max(current_value - legacy_max, 0)
        merged = old_value + baseline_value + later_progress
        if current_value != merged:
            _write_counter(current, category, key, merged)
            changed = True
    if not changed:
        return current_online_raw, False
    return (json.dumps(current, ensure_ascii=False, separators=(",", ":")) + "\n").encode(), True


def merge_advancements(old_raw: bytes | None, new_raw: bytes | None):
    if old_raw is None:
        return new_raw, False
    if new_raw is None:
        return old_raw, True
    old = json.loads(old_raw.decode("utf-8"))
    new = json.loads(new_raw.decode("utf-8"))
    if not isinstance(old, dict) or not isinstance(new, dict):
        return new_raw, False
    changed = False
    for advancement, old_value in old.items():
        if advancement == "DataVersion":
            continue
        if advancement not in new:
            new[advancement] = old_value
            changed = True
            continue
        new_value = new.get(advancement)
        if not isinstance(old_value, dict) or not isinstance(new_value, dict):
            continue
        old_criteria = old_value.get("criteria")
        new_criteria = new_value.setdefault("criteria", {})
        if isinstance(old_criteria, dict) and isinstance(new_criteria, dict):
            for criterion, when in old_criteria.items():
                if criterion not in new_criteria:
                    new_criteria[criterion] = when
                    changed = True
        if old_value.get("done") and not new_value.get("done"):
            new_value["done"] = True
            changed = True
    if not changed:
        return new_raw, False
    return (json.dumps(new, ensure_ascii=False, separators=(",", ":")) + "\n").encode(), True


def json_list(raw, name):
    if raw is None:
        return []
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise Error(f"invalid {name}") from e
    if not isinstance(value, list):
        raise Error(f"{name} must be a JSON list")
    return value


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def backup_and_write(client: Client, path: str, old: bytes | None, new: bytes, stamp: int, manifest):
    if old == new:
        return
    if old is not None:
        backup = f"{path}.pre-online-uuid-migration-{stamp}.bak"
        client.write_file(backup, old)
    client.write_file(path, new)
    manifest.append({
        "path": path,
        "old_sha256": sha256(old) if old is not None else None,
        "new_sha256": sha256(new),
        "backup_created": old is not None,
    })


STATS_SUM_STATE = "uuid-migration-stats-sum-state.json"


def _stats_sum_state(raw):
    if raw is None:
        return {"version": 1, "strategy": "sum-per-counter", "players": {}}
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise Error(f"invalid {STATS_SUM_STATE}") from e
    if not isinstance(value, dict) or value.get("version") != 1:
        raise Error(f"unsupported {STATS_SUM_STATE} format")
    players = value.get("players")
    if not isinstance(players, dict):
        raise Error(f"{STATS_SUM_STATE} players must be an object")
    return value


def find_pre_migration_stats_backup(client: Client, stats_root: str, online_uuid: str):
    """Return the earliest backup of online stats made by the legacy max merger."""
    info = client.info_optional(stats_root)
    if info is None:
        return None, None
    prefix = f"{online_uuid}.json.pre-online-uuid-migration-"
    suffix = ".bak"
    candidates = []
    for child in child_list(info):
        if not isinstance(child, dict) or child.get("isDirectory"):
            continue
        name = str(child.get("name") or "")
        if not (name.startswith(prefix) and name.endswith(suffix)):
            continue
        stamp_text = name[len(prefix):-len(suffix)]
        try:
            stamp = int(stamp_text)
        except ValueError:
            continue
        path = (str(child.get("path") or "") or f"{stats_root}/{name}").lstrip("/")
        candidates.append((stamp, path))
    if not candidates:
        return None, None
    _, path = min(candidates)
    return path, client.read_file_optional(path)


def plan_or_apply(mode: str):
    if mode not in {"dry-run", "apply"}:
        raise Error("mode must be dry-run or apply")
    client = Client(os.environ.get("EXAROTON_API_TOKEN", ""))
    server = client.require_offline()
    props = client.read_file_optional("server.properties")
    if props is None:
        raise Error("server.properties not found")
    world = level_name(props)

    whitelist = json_list(client.read_file_optional("whitelist.json"), "whitelist.json")
    by_name = {str(e.get("name") or "").lower(): str(e.get("uuid") or "") for e in whitelist if isinstance(e, dict)}
    for name, (_, online_uuid) in PLAYER_MAP.items():
        if normalize_uuid_string(by_name.get(name.lower(), "")) != str(uuid.UUID(online_uuid)):
            raise Error(f"whitelist safety check failed for {name}")

    region_files = list_region_files(client, world)
    region_changes = []
    for path in region_files:
        raw = client.read_file_optional(path)
        if raw is None:
            continue
        transformed, stats = transform_region(raw)
        if transformed != raw:
            region_changes.append((path, raw, transformed, stats))

    # Minecraft 26.3 moved player identity data under world/players/.
    # Old offline .dat_old files are preserved as history only; never overwrite
    # a current online .dat with them, because that could roll back inventory,
    # position, XP, ender-chest data, etc.
    player_data_root = f"{world}/players/data"
    advancements_root = f"{world}/players/advancements"
    stats_root = f"{world}/players/stats"
    stats_state_raw = client.read_file_optional(STATS_SUM_STATE)
    stats_state = _stats_sum_state(stats_state_raw)
    stats_state_players = stats_state["players"]
    stats_state_updates = {}

    player_changes = []
    identity_summary = {}
    for name, (old_uuid, new_uuid) in PLAYER_MAP.items():
        old_player = client.read_file_optional(f"{player_data_root}/{old_uuid}.dat")
        old_player_backup = client.read_file_optional(f"{player_data_root}/{old_uuid}.dat_old")
        new_player = client.read_file_optional(f"{player_data_root}/{new_uuid}.dat")

        if new_player is None and old_player is not None:
            candidate, meta = transform_player_nbt(old_player)
            player_changes.append((
                f"{player_data_root}/{new_uuid}.dat",
                None,
                candidate,
                {"source": "offline-current", **meta},
            ))
        elif new_player is not None:
            # Only rewrite exact stale offline UUID references inside the
            # canonical online player file. Do not import old inventory/state.
            candidate, meta = transform_player_nbt(new_player)
            if candidate != new_player:
                player_changes.append((
                    f"{player_data_root}/{new_uuid}.dat",
                    new_player,
                    candidate,
                    {"source": "online-current", **meta},
                ))

        old_adv = client.read_file_optional(f"{advancements_root}/{old_uuid}.json")
        new_adv = client.read_file_optional(f"{advancements_root}/{new_uuid}.json")
        merged_adv, adv_changed = merge_advancements(old_adv, new_adv)
        if merged_adv is not None and adv_changed:
            player_changes.append((
                f"{advancements_root}/{new_uuid}.json",
                new_adv,
                merged_adv,
                {"merged": True},
            ))

        old_stats = client.read_file_optional(f"{stats_root}/{old_uuid}.json")
        new_stats = client.read_file_optional(f"{stats_root}/{new_uuid}.json")
        stats_strategy = "none"
        legacy_stats_backup = None
        state_entry = stats_state_players.get(name)
        if old_stats is not None and isinstance(state_entry, dict):
            recorded_source = str(state_entry.get("offline_stats_sha256") or "")
            current_source = sha256(old_stats)
            if recorded_source != current_source:
                raise Error(
                    f"offline stats changed after summed migration for {name}; "
                    "refusing to add the historical source twice"
                )
            if new_stats is None:
                raise Error(
                    f"online stats missing for {name} after summed migration state was recorded"
                )
            merged_stats, stats_changed = new_stats, False
            stats_strategy = "already-summed"
        else:
            if old_stats is not None and new_stats is not None:
                legacy_stats_backup, baseline_stats = find_pre_migration_stats_backup(
                    client, stats_root, new_uuid
                )
            else:
                baseline_stats = None
            if old_stats is not None and new_stats is not None and baseline_stats is not None:
                merged_stats, stats_changed = merge_stats_after_legacy_max(
                    old_stats, baseline_stats, new_stats
                )
                stats_strategy = "sum-corrected-from-legacy-max"
            else:
                merged_stats, stats_changed = merge_stats(old_stats, new_stats)
                stats_strategy = "sum-per-counter" if old_stats is not None else "none"
            if old_stats is not None and merged_stats is not None:
                stats_state_updates[name] = {
                    "offline_stats_sha256": sha256(old_stats),
                    "target_online_uuid": str(uuid.UUID(new_uuid)),
                    "strategy": "sum-per-counter",
                }

        if merged_stats is not None and stats_changed:
            player_changes.append((
                f"{stats_root}/{new_uuid}.json",
                new_stats,
                merged_stats,
                {
                    "merged": True,
                    "strategy": stats_strategy,
                    "legacy_pre_max_backup": legacy_stats_backup,
                },
            ))

        identity_summary[name] = {
            "offline_playerdata_current": old_player is not None,
            "offline_playerdata_backup": old_player_backup is not None,
            "online_playerdata": new_player is not None,
            "offline_advancements": old_adv is not None,
            "online_advancements": new_adv is not None,
            "offline_stats": old_stats is not None,
            "online_stats": new_stats is not None,
            "stats_strategy": stats_strategy,
            "legacy_pre_max_stats_backup": legacy_stats_backup,
            "canonical_playerdata": (
                "online"
                if new_player is not None
                else ("offline-current-copied" if old_player is not None else "missing")
            ),
            "offline_dat_old_action": "preserved-not-merged",
        }

    usercache_raw = client.read_file_optional("usercache.json")
    usercache = json_list(usercache_raw, "usercache.json")
    filtered_cache = [
        e for e in usercache
        if not (
            isinstance(e, dict)
            and (
                str(e.get("name") or "").lower() == TYPO_NAME.lower()
                or normalize_uuid_string(str(e.get("uuid") or "")) == str(uuid.UUID(TYPO_UUID))
            )
        )
    ]
    cache_removed = len(usercache) - len(filtered_cache)
    cache_new = (json.dumps(filtered_cache, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    summary = {
        "mode": mode,
        "server": {"address": server.get("address"), "status": server.get("status")},
        "world": world,
        "entity_region_files_scanned": len(region_files),
        "entity_region_files_to_change": len(region_changes),
        "entity_uuid_references_to_change": sum(x[3]["int_array"] + x[3]["string"] for x in region_changes),
        "player_related_files_to_change": len(player_changes),
        "stats_merge_strategy": "sum-per-counter",
        "stats_sum_state_updates": sorted(stats_state_updates),
        "penguin531_usercache_entries_to_remove": cache_removed,
        "players": identity_summary,
        "region_changes": [{"path": x[0], **x[3]} for x in region_changes],
        "player_changes": [{"path": x[0], **x[3]} for x in player_changes],
    }

    if mode == "dry-run":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    client.require_offline()
    stamp = int(time.time())
    manifest = []

    for path, old, new, _ in region_changes:
        backup_and_write(client, path, old, new, stamp, manifest)

    for path, old, new, _ in player_changes:
        backup_and_write(client, path, old, new, stamp, manifest)

    if cache_removed:
        backup_and_write(client, "usercache.json", usercache_raw, cache_new, stamp, manifest)

    if stats_state_updates:
        next_state = json.loads(json.dumps(stats_state))
        next_players = next_state["players"]
        for name, entry in stats_state_updates.items():
            next_players[name] = {**entry, "applied_at_unix": stamp}
        state_bytes = (
            json.dumps(next_state, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        backup_and_write(
            client, STATS_SUM_STATE, stats_state_raw, state_bytes, stamp, manifest
        )

    manifest_obj = {
        "created_at_unix": stamp,
        "mapping": {name: {"offline": old, "online": new} for name, (old, new) in PLAYER_MAP.items()},
        "stats_merge_strategy": "sum-per-counter",
        "stats_sum_state": STATS_SUM_STATE,
        "penguin531_removed_from_usercache": cache_removed,
        "writes": manifest,
    }
    manifest_path = f"uuid-migration-{stamp}.json"
    client.write_file(manifest_path, (json.dumps(manifest_obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    summary["applied"] = True
    summary["backup_stamp"] = stamp
    summary["manifest"] = manifest_path
    summary["files_written"] = len(manifest)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: exaroton_inno_uuid_migrate.py dry-run|apply")
    try:
        plan_or_apply(sys.argv[1])
    except Error as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
