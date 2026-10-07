#!/usr/bin/env python3
"""GitHub Actions control for exaroton test server; writes are hard-locked to innotest."""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from pathlib import Path, PurePosixPath

API = "https://api.exaroton.com/v1"
TARGET = "innotest.exaroton.me"
PACKS = ("utilities", "warehouse", "copy-paste")
BOT_PLAYERS = ("SunnyChen", "penguin0531", "geena0701", "Felicitypeng")
ROOT = Path(__file__).resolve().parents[1]
STATUS = {0:"OFFLINE",1:"ONLINE",2:"STARTING",3:"STOPPING",4:"RESTARTING",5:"SAVING",6:"LOADING",7:"CRASHED",8:"PENDING",9:"TRANSFERRING",10:"PREPARING"}

class Error(RuntimeError): pass

def addr(v): return str(v or "").strip().rstrip(".").lower()

def remote_path(p: str) -> str:
    x = PurePosixPath(p)
    if x.is_absolute() or not x.parts or any(i in ("", ".", "..") for i in x.parts):
        raise Error(f"unsafe remote path: {p!r}")
    return "/".join(urllib.parse.quote(i, safe="") for i in x.parts)

class APIClient:
    def __init__(self, token: str, opener=urllib.request.urlopen):
        if not token.strip(): raise Error("EXAROTON_API_TOKEN is not configured")
        self.token, self.opener = token.strip(), opener

    def req(self, method, path, *, obj=None, raw=None, raw_response=False):
        headers = {"Authorization": f"Bearer {self.token}", "User-Agent": "packs-minecraft-inno/1"}
        body = raw
        if obj is not None:
            body = json.dumps(obj, separators=(",", ":")).encode()
            headers["Content-Type"] = "application/json"
        elif raw is not None:
            headers["Content-Type"] = "application/octet-stream"
        request = urllib.request.Request(API + path, data=body, headers=headers, method=method)
        try:
            with self.opener(request, timeout=30) as response:
                data = response.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            raise Error(f"exaroton HTTP {e.code}: {detail or e.reason}") from e
        except urllib.error.URLError as e:
            raise Error(f"cannot reach exaroton API: {e.reason}") from e
        if raw_response: return data
        try: result = json.loads(data.decode())
        except Exception as e: raise Error("exaroton returned invalid JSON") from e
        if isinstance(result, dict) and result.get("success") is False:
            raise Error(f"exaroton error: {result.get('error') or 'unknown'}")
        return result.get("data") if isinstance(result, dict) and "data" in result else result

    def get(self, sid):
        data = self.req("GET", f"/servers/{urllib.parse.quote(str(sid), safe='')}")
        if not isinstance(data, dict): raise Error("unexpected server response")
        return data

    def target(self):
        servers = self.req("GET", "/servers/")
        matches = [s for s in servers if isinstance(s, dict) and addr(s.get("address")) == TARGET]
        if len(matches) != 1: raise Error(f"safety lock: expected exactly one {TARGET}, found {len(matches)}")
        sid = matches[0].get("id")
        if not sid: raise Error("safety lock: innotest has no server id")
        return self.verify(sid)

    def verify(self, sid):
        server = self.get(sid)
        if addr(server.get("address")) != TARGET:
            raise Error(f"safety lock refused mutation/read target: {addr(server.get('address')) or '<missing>'}")
        return server

    def action(self, name):
        server = self.target(); server = self.verify(server["id"])
        sid = urllib.parse.quote(str(server["id"]), safe="")
        self.req("GET", f"/servers/{sid}/{name}/")

    def command(self, command):
        if not command.strip(): raise Error("command must not be empty")
        server = self.target(); server = self.verify(server["id"])
        sid = urllib.parse.quote(str(server["id"]), safe="")
        self.req("POST", f"/servers/{sid}/command/", obj={"command": command.strip()})

    def log(self):
        server = self.target(); sid = urllib.parse.quote(str(server["id"]), safe="")
        data = self.req("GET", f"/servers/{sid}/logs/")
        return str((data or {}).get("content") or "")

    def read_file(self, path):
        server = self.target(); sid = urllib.parse.quote(str(server["id"]), safe="")
        return self.req("GET", f"/servers/{sid}/files/data/{remote_path(path)}/", raw_response=True)

    def read_file_optional(self, path):
        try:
            return self.read_file(path)
        except Error as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def read_binary_file_optional(self, path):
        """Read binary world files through exaroton's non-directory data endpoint."""
        server = self.target()
        sid = urllib.parse.quote(str(server["id"]), safe="")
        try:
            return self.req(
                "GET",
                f"/servers/{sid}/files/data/{remote_path(str(path).lstrip('/'))}",
                raw_response=True,
            )
        except Error as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def write_file(self, path, content):
        server = self.target(); server = self.verify(server["id"])
        sid = urllib.parse.quote(str(server["id"]), safe="")
        self.req("PUT", f"/servers/{sid}/files/data/{remote_path(path)}/", raw=content)

    def delete_file(self, path):
        server = self.target(); server = self.verify(server["id"])
        sid = urllib.parse.quote(str(server["id"]), safe="")
        self.req("DELETE", f"/servers/{sid}/files/data/{remote_path(path)}/")

    def file_info(self, path):
        server = self.target()
        sid = urllib.parse.quote(str(server["id"]), safe="")
        return self.req("GET", f"/servers/{sid}/files/info/{remote_path(path)}/")

    def info_optional(self, path):
        try:
            return self.file_info(str(path).lstrip("/"))
        except Error as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def get_config(self, path):
        server = self.target()
        sid = urllib.parse.quote(str(server["id"]), safe="")
        return self.req("GET", f"/servers/{sid}/files/config/{remote_path(path)}/")

    def update_config(self, path, values):
        server = self.target(); server = self.verify(server["id"])
        sid = urllib.parse.quote(str(server["id"]), safe="")
        return self.req("POST", f"/servers/{sid}/files/config/{remote_path(path)}/", obj=values)


INNO_READONLY_TARGET = "inno.exaroton.me"

class InnoReadOnlyClient:
    """GET-only exaroton client hard-locked to the production inno server."""
    def __init__(self, token: str, opener=urllib.request.urlopen):
        if not token.strip():
            raise Error("EXAROTON_API_TOKEN is not configured")
        self.token, self.opener = token.strip(), opener

    def get_json(self, path):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "packs-minecraft-inno/1 inno-readonly",
        }
        request = urllib.request.Request(API + path, headers=headers, method="GET")
        try:
            with self.opener(request, timeout=30) as response:
                data = response.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            raise Error(f"exaroton HTTP {e.code}: {detail or e.reason}") from e
        except urllib.error.URLError as e:
            raise Error(f"cannot reach exaroton API: {e.reason}") from e
        try:
            result = json.loads(data.decode())
        except Exception as e:
            raise Error("exaroton returned invalid JSON") from e
        if isinstance(result, dict) and result.get("success") is False:
            raise Error(f"exaroton error: {result.get('error') or 'unknown'}")
        return result.get("data") if isinstance(result, dict) and "data" in result else result

    def get_raw(self, path):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "packs-minecraft-inno/1 inno-readonly",
        }
        request = urllib.request.Request(API + path, headers=headers, method="GET")
        try:
            with self.opener(request, timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            raise Error(f"exaroton HTTP {e.code}: {detail or e.reason}") from e
        except urllib.error.URLError as e:
            raise Error(f"cannot reach exaroton API: {e.reason}") from e

    def target(self):
        servers = self.get_json("/servers/")
        matches = [
            server for server in servers
            if isinstance(server, dict)
            and addr(server.get("address")) == INNO_READONLY_TARGET
        ]
        if len(matches) != 1:
            raise Error(
                f"read-only safety lock: expected exactly one "
                f"{INNO_READONLY_TARGET}, found {len(matches)}"
            )
        sid = matches[0].get("id")
        if not sid:
            raise Error("read-only safety lock: inno has no server id")
        server = self.get_json(f"/servers/{urllib.parse.quote(str(sid), safe='')}")
        if addr(server.get("address")) != INNO_READONLY_TARGET:
            raise Error("read-only safety lock: target verification failed")
        return server

    def read_file_optional(self, sid, path):
        sid_q = urllib.parse.quote(str(sid), safe="")
        try:
            return self.get_raw(
                f"/servers/{sid_q}/files/data/{remote_path(path)}/"
            )
        except Error as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def read_binary_file_optional(self, sid, path):
        """Binary-safe read (no trailing slash), like APIClient.read_binary_file_optional."""
        sid_q = urllib.parse.quote(str(sid), safe="")
        try:
            return self.get_raw(
                f"/servers/{sid_q}/files/data/{remote_path(str(path).lstrip('/'))}"
            )
        except Error as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def file_info_optional(self, sid, path):
        sid_q = urllib.parse.quote(str(sid), safe="")
        try:
            return self.get_json(
                f"/servers/{sid_q}/files/info/{remote_path(path)}/"
            )
        except Error as e:
            if "HTTP 404" in str(e):
                return None
            raise


def _json_file(client, sid, path):
    raw = client.read_file_optional(sid, path)
    if raw is None:
        return []
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise Error(f"{path} is not valid JSON") from e
    return value


def _uuid_files(info, suffix):
    children = (info or {}).get("children") or []
    out = []
    for child in children:
        if not isinstance(child, dict):
            continue
        name = str(child.get("name") or "")
        if not name.endswith(suffix):
            continue
        candidate = name[:-len(suffix)]
        try:
            parsed = str(uuid.UUID(candidate))
        except ValueError:
            continue
        out.append(parsed)
    return sorted(set(out))


def inno_identity_status(token):
    """Read identity-related files from inno without starting or mutating it."""
    client = InnoReadOnlyClient(token)
    server = client.target()
    sid = server["id"]

    properties = client.read_file_optional(sid, "server.properties")
    if properties is None:
        raise Error("inno server.properties not found")
    world = level_name(properties)

    whitelist = _json_file(client, sid, "whitelist.json")
    usercache = _json_file(client, sid, "usercache.json")
    ops = _json_file(client, sid, "ops.json")

    playerdata = _uuid_files(
        client.file_info_optional(sid, f"{world}/players/data"), ".dat"
    )
    advancements = _uuid_files(
        client.file_info_optional(sid, f"{world}/players/advancements"), ".json"
    )
    stats = _uuid_files(
        client.file_info_optional(sid, f"{world}/players/stats"), ".json"
    )

    known = {}
    for source, entries in (
        ("whitelist", whitelist),
        ("usercache", usercache),
        ("ops", ops),
    ):
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            raw_uuid = str(entry.get("uuid") or "")
            try:
                key = str(uuid.UUID(raw_uuid))
            except ValueError:
                continue
            item = known.setdefault(key, {"names": [], "sources": []})
            name = str(entry.get("name") or "")
            if name and name not in item["names"]:
                item["names"].append(name)
            if source not in item["sources"]:
                item["sources"].append(source)

    all_world_uuids = sorted(set(playerdata) | set(advancements) | set(stats))
    unexplained = [
        {"uuid": u, **known.get(u, {"names": [], "sources": []})}
        for u in all_world_uuids
        if u not in known
    ]

    code = int(server.get("status", -1))
    return {
        "server": {
            "name": server.get("name"),
            "address": server.get("address"),
            "status": code,
            "status_name": STATUS.get(code, "UNKNOWN"),
        },
        "world": world,
        "whitelist": whitelist,
        "usercache": usercache,
        "ops": ops,
        "world_uuid_files": {
            "playerdata": playerdata,
            "advancements": advancements,
            "stats": stats,
            "union": all_world_uuids,
        },
        "world_uuids_not_present_in_whitelist_usercache_ops": unexplained,
    }


def inno_world_layout_status(token):
    """Inspect only directory metadata needed to locate 26.3 player identity files."""
    client = InnoReadOnlyClient(token)
    server = client.target()
    sid = server["id"]
    properties = client.read_file_optional(sid, "server.properties")
    if properties is None:
        raise Error("inno server.properties not found")
    world = level_name(properties)
    candidates = [
        world,
        f"{world}/players",
        f"{world}/players/data",
        f"{world}/players/advancements",
        f"{world}/players/stats",
        f"{world}/dimensions",
        f"{world}/dimensions/minecraft",
        f"{world}/dimensions/minecraft/overworld",
        f"{world}/dimensions/minecraft/overworld/playerdata",
        f"{world}/dimensions/minecraft/overworld/advancements",
        f"{world}/dimensions/minecraft/overworld/stats",
    ]
    result = {"world": world, "paths": {}}
    for path in candidates:
        info = client.file_info_optional(sid, path)
        if info is None:
            result["paths"][path] = None
            continue
        children = []
        for child in (info.get("children") or []):
            if not isinstance(child, dict):
                continue
            children.append({
                "name": child.get("name"),
                "path": child.get("path"),
                "isDirectory": child.get("isDirectory"),
                "size": child.get("size"),
            })
        result["paths"][path] = {
            "path": info.get("path"),
            "name": info.get("name"),
            "isDirectory": info.get("isDirectory"),
            "children": children,
        }
    return result


WAREHOUSE_BOX_FIELDS = ("dimension", "a_x", "a_y", "a_z", "b_x", "b_y", "b_z")


def command_storage_contents(raw):
    """Parse a 26.3 data/<namespace>/command_storage.dat into its storage contents."""
    import gzip
    import nbtlib

    data = gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw
    root = nbtlib.File.parse(io.BytesIO(data))
    if "data" not in root and "" in root:
        root = root[""]
    return root["data"]["contents"]


def _tag_type(value):
    return type(value).__name__


def warehouse_registration_report(contents):
    """Summarize warehouse:chests without dumping the stored values."""
    chests = contents.get("chests") or {}
    boxes, incomplete = {}, []
    for code in sorted(key for key in chests if key[:1] == "c" and key[1:].isdigit()):
        box = chests[code]
        registered = int(box.get("registered", 0)) == 1
        missing = [field for field in WAREHOUSE_BOX_FIELDS if field not in box]
        types = sorted({_tag_type(box[field]) for field in WAREHOUSE_BOX_FIELDS[1:] if field in box})
        boxes[code] = {
            "registered": registered,
            "valid": int(box.get("valid", 0)) == 1,
            "missing": missing,
            "coordinate_types": types,
            "dimension": str(box["dimension"]) if "dimension" in box else None,
        }
        if registered and missing:
            incomplete.append(code)
    meta = contents.get("meta") or {}
    forceload = contents.get("forceload") or {}
    return {
        "box_entries": len(boxes),
        "registered": sum(1 for box in boxes.values() if box["registered"]),
        "registered_missing_fields": incomplete,
        "registered_non_int_coordinates": [
            code for code, box in boxes.items()
            if box["registered"] and any(t != "Int" for t in box["coordinate_types"])
        ],
        "dimensions": sorted({box["dimension"] for box in boxes.values() if box["registered"] and box["dimension"]}),
        "meta_flags": sorted(str(key) for key in meta),
        "forceload_records": len(forceload.get("chunks") or []),
        "boxes": {code: box for code, box in boxes.items() if box["registered"] and (box["missing"] or box["coordinate_types"] != ["Int"])},
    }


def utilities_waypoint_report(contents):
    """Count saved Utilities locations and flag any whose x/y/z is not an Int tag."""
    locations, odd = 0, []

    def walk(value, path):
        nonlocal locations
        if not hasattr(value, "items"):
            return
        if all(axis in value for axis in ("x", "y", "z")):
            locations += 1
            types = {axis: _tag_type(value[axis]) for axis in ("x", "y", "z")}
            if any(t != "Int" for t in types.values()):
                odd.append({"path": path, "types": types})
            return
        for key, child in value.items():
            walk(child, f"{path}.{key}" if path else str(key))

    for storage in ("players", "shared"):
        walk(contents.get(storage) or {}, storage)
    meta = contents.get("meta") or {}
    return {"version": str(meta["version"]) if "version" in meta else None, "locations": locations, "non_int_locations": odd}


def inno_storage_status(token):
    """Read-only: summarize production Warehouse registrations and Utilities waypoint coordinate types."""
    client = InnoReadOnlyClient(token)
    server = client.target()
    sid = server["id"]
    properties = client.read_file_optional(sid, "server.properties")
    if properties is None:
        raise Error("inno server.properties not found")
    world = level_name(properties)
    result = {"world": world, "server_status": STATUS.get(int(server.get("status", -1)), "UNKNOWN")}
    packs = client.file_info_optional(sid, f"{world}/datapacks") or {}
    result["datapacks"] = sorted(str(child.get("name")) for child in (packs.get("children") or []) if isinstance(child, dict))
    for name, report in (("warehouse", warehouse_registration_report), ("sunny_nav", utilities_waypoint_report)):
        path = f"{world}/data/{name}/command_storage.dat"
        raw = client.read_binary_file_optional(sid, path)
        result[name] = {"path": path, "missing": True} if raw is None else {"path": path, **report(command_storage_contents(raw))}
    return result


def pack_zip(name):
    if name not in PACKS: raise Error(f"unsupported datapack: {name}")
    base = ROOT / "datapacks" / name
    if not (base / "pack.mcmeta").is_file(): raise Error(f"missing datapack: {name}")
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(base.rglob("*")):
            if p.is_symlink(): raise Error(f"symlink refused: {p}")
            if p.is_file(): z.write(p, p.relative_to(base).as_posix())
    return out.getvalue()

def level_name(raw):
    result = "world"
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.strip().startswith("level-name="):
            result = line.split("=", 1)[1].strip() or "world"; break
    remote_path(result)
    return result

def deploy(client, which):
    names = PACKS if which == "all" else (which,)
    if any(n not in PACKS for n in names): raise Error(f"unsupported datapack: {which}")
    world = level_name(client.read_file("server.properties"))
    for name in names:
        payload = pack_zip(name)
        dst = f"{world}/datapacks/{name}.zip"
        client.write_file(dst, payload)
        print(f"deployed {name} -> {dst} ({len(payload)} bytes)")
    current = client.target()
    if int(current.get("status", -1)) == 1:
        client.command("reload"); print("server online: reload issued")
    else:
        print("server offline/not-online: not started, no reload issued")

def zip_tree(base):
    if not base.is_dir():
        raise Error(f"missing directory to zip: {base}")
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(base.rglob("*")):
            if p.is_symlink():
                raise Error(f"symlink refused: {p}")
            if p.is_file():
                z.write(p, p.relative_to(base).as_posix())
    return out.getvalue()

def player_count(server):
    players = server.get("players")
    if isinstance(players, int):
        return players
    if isinstance(players, list):
        return len(players)
    if isinstance(players, dict):
        for key in ("count", "online", "current"):
            value = players.get(key)
            if isinstance(value, int):
                return value
        listing = players.get("list")
        if isinstance(listing, list):
            return len(listing)
    return -1

def wait_players(client, minimum=3, timeout=180):
    deadline = time.time() + timeout
    last = -1
    while time.time() < deadline:
        server = client.target()
        if int(server.get("status", -1)) != 1:
            time.sleep(2)
            continue
        last = player_count(server)
        if last >= minimum:
            return server
        time.sleep(2)
    raise Error(f"timeout waiting for at least {minimum} players; last count={last}")

def run_copy_paste_multiplayer_test(client):
    current = client.target()
    if int(current.get("status", -1)) != 1:
        raise Error("innotest must be ONLINE before live multiplayer testing")

    # Mark the whole deployment/test session before any reload so parser/load
    # errors from this attempt cannot be hidden by a later PASS line.
    session_marker = f"MCCMP_SESSION_{int(time.time() * 1000)}"
    client.command(f"say {session_marker} START")
    time.sleep(1)

    # Deploy the exact datapacks from the checked-out main commit first.
    deploy(client, "all")
    time.sleep(5)

    import subprocess
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "build-copy-paste-multiplayer-test.py")])
    harness = ROOT / "dist" / "mcc-multiplayer-test"
    payload = zip_tree(harness)
    world = level_name(client.read_file("server.properties"))
    remote_harness = f"{world}/datapacks/mcc-multiplayer-test.zip"
    client.write_file(remote_harness, payload)
    print(f"deployed live multiplayer harness -> {remote_harness} ({len(payload)} bytes)")
    client.command("reload")
    time.sleep(6)

    # Preflight only the current session. Historical errors earlier in the
    # persistent exaroton log are irrelevant, but any new server ERROR after
    # this session marker makes the live regression invalid.
    preflight_log = client.log()
    session_at = preflight_log.rfind(f"{session_marker} START")
    if session_at < 0:
        raise Error("live multiplayer preflight marker not found in server log")
    preflight_segment = preflight_log[session_at:]
    preflight_errors = [
        line for line in preflight_segment.splitlines()
        if "/ERROR]:" in line
    ]
    if preflight_errors:
        try:
            client.delete_file(remote_harness)
        finally:
            try:
                client.command("reload")
            except Error:
                pass
        preview = "\n".join(preflight_errors[:12])
        raise Error(
            "live multiplayer preflight found current-session server errors:\n"
            + preview
        )

    server = wait_players(client, 3, 180)
    print(f"live multiplayer test starting with player count={player_count(server)}")

    # Reserve SunnyChen for supervision / real-client control. Use two of the
    # three non-SunnyChen test players while the third remains connected.
    # Mark this run in the server log so stale results from previous attempts
    # can never be mistaken for the current test.
    run_marker = f"MCCMP_RUN_{int(time.time() * 1000)}"
    client.command(f"say {run_marker} START")
    time.sleep(1)

    commands = [
        "tag @a remove mcc_mp_a",
        "tag @a remove mcc_mp_b",
        "execute as @a[name=penguin0531,limit=1] run function mcc_mp_test:join_a",
        "execute as @a[name=geena0701,limit=1] run function mcc_mp_test:join_b",
        "execute as @a[name=penguin0531,limit=1] run function mcc_mp_test:start",
    ]
    for command in commands:
        client.command(command)
        time.sleep(1)

    # The exaroton test server can fall behind under the full datapack load.
    # Wait for the scheduled regression chain itself to finish instead of
    # assuming a fixed wall-clock duration.
    deadline = time.time() + 180
    result = ""
    segment = ""
    log = ""
    while time.time() < deadline:
        log = client.log()
        marker = log.rfind(f"{run_marker} START")
        if marker >= 0:
            segment = log[marker:]
            result_lines = [
                line for line in segment.splitlines()
                if "MCCMP_RESULT " in line
            ]
            if result_lines:
                result = result_lines[-1]
                break
        time.sleep(3)

    # Clean the temporary harness and its reserved test state only after the
    # current run has produced a result (or timed out).
    cleanup = [
        "tick rate 20",
        "function mcc_mp_test:cleanup",
    ]
    for command in cleanup:
        try:
            client.command(command)
        except Error:
            pass
    try:
        client.delete_file(remote_harness)
    finally:
        try:
            client.command("reload")
        except Error:
            pass

    current_checks = "\n".join(
        line for line in segment.splitlines()
        if "MCCMP_CHECK " in line or "MCCMP_DIAG " in line or "MCCMP_DIFF " in line or "MCCMP_RESULT " in line
    )
    if current_checks:
        print(current_checks)

    current_errors = [
        line for line in segment.splitlines()
        if "/ERROR]:" in line
    ]
    if current_errors:
        preview = "\n".join(current_errors[:12])
        raise Error(
            "live multiplayer test produced current-run server errors even "
            "though a result line was present:\n" + preview
        )

    if "MCCMP_RESULT PASS" in result:
        print("COPY_PASTE_MULTIPLAYER_LIVE_TEST=PASS")
        return

    raise Error(
        f"live multiplayer test did not pass; "
        f"current-run result={result or '<missing>'}"
    )

def run_blueprint_matcher_live_test(client):
    """Issue #49: every exact 26.3 block state through the Blueprint matcher on innotest."""
    current = client.target()
    if int(current.get("status", -1)) != 1:
        raise Error("innotest must be ONLINE before Blueprint matcher live testing")

    session_marker = f"MCCBP_SESSION_{int(time.time() * 1000)}"
    client.command(f"say {session_marker} START")
    time.sleep(1)

    # Deploy the exact Copy/Paste source from the checked-out commit.
    deploy(client, "copy-paste")
    time.sleep(5)

    import subprocess
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "build-blueprint-matcher-live-test.py")])
    payload = zip_tree(ROOT / "dist" / "mcc-bp-matcher-live-test")
    world = level_name(client.read_file("server.properties"))
    remote_harness = f"{world}/datapacks/mcc-bp-matcher-live-test.zip"
    client.write_file(remote_harness, payload)
    print(f"deployed Blueprint matcher harness -> {remote_harness} ({len(payload)} bytes)")
    client.command("reload")
    time.sleep(6)

    result = ""
    segment = ""
    try:
        log = client.log()
        session_at = log.rfind(f"{session_marker} START")
        if session_at < 0:
            raise Error("Blueprint matcher preflight marker not found in server log")
        preflight_errors = [line for line in log[session_at:].splitlines() if "/ERROR]:" in line]
        if preflight_errors:
            raise Error("Blueprint matcher preflight found current-session server errors:\n"
                        + "\n".join(preflight_errors[:12]))

        run_marker = f"MCCBP_RUN_{int(time.time() * 1000)}"
        client.command(f"say {run_marker} START")
        time.sleep(1)
        client.command("function mcc_bp_live:start")
        # Read-only progress probes; never cancel the pending first batch here.
        time.sleep(10)
        for command in ("tick query",
                        "scoreboard players get #states mccbp",
                        "data get storage mcc_bp_live:t want"):
            client.command(command)
            time.sleep(1)

        deadline = time.time() + 300
        while time.time() < deadline:
            log = client.log()
            marker = log.rfind(f"{run_marker} START")
            if marker >= 0:
                segment = log[marker:]
                hits = [line for line in segment.splitlines() if "MCCBP_RESULT " in line]
                if hits:
                    result = hits[-1]
                    break
            time.sleep(3)
    finally:
        for command in ("scoreboard objectives remove mccbp",
                        "data remove storage mcc_bp_live:t want",
                        "execute in minecraft:overworld run setblock -440 250 120 minecraft:air strict",
                        "execute in minecraft:overworld run forceload remove -440 120"):
            try:
                client.command(command)
            except Error:
                pass
        try:
            client.delete_file(remote_harness)
        finally:
            try:
                client.command("reload")
            except Error:
                pass

    report = "\n".join(line for line in segment.splitlines() if "MCCBP_" in line)
    if report:
        print(report)
    errors = [line for line in segment.splitlines() if "/ERROR]:" in line]
    if errors:
        raise Error("Blueprint matcher live test produced current-run server errors:\n"
                    + "\n".join(errors[:12]))
    if "MCCBP_RESULT PASS" in result:
        print("BLUEPRINT_MATCHER_LIVE_TEST=PASS")
        return
    raise Error(f"Blueprint matcher live test did not pass; current-run result={result or '<missing>'}")

LIVE_SUITES = {
    "utilities": ("build-utilities-live-test.py", "utilities-live-test"),
    "warehouse": ("build-warehouse-live-test.py", "warehouse-live-test"),
}

def wait_named_players(client, names, timeout=180):
    deadline = time.time() + timeout
    missing = list(names)
    while time.time() < deadline:
        server = client.target()
        players = server.get("players") or {}
        listing = players.get("list") if isinstance(players, dict) else players
        online = set(listing or [])
        missing = [n for n in names if n not in online]
        if int(server.get("status", -1)) == 1 and not missing:
            # A restarted bot session drops the old clients first: require the
            # players to still be there 10 s later before starting.
            time.sleep(10)
            again = client.target().get("players") or {}
            again = set((again.get("list") if isinstance(again, dict) else again) or [])
            if all(n in again for n in names):
                return server
        time.sleep(2)
    raise Error(f"timeout waiting for test players; missing={missing}")

def run_live_suite(client, suite):
    """Deploy the checked-out packs, run one innotest live suite and clean it up.

    The suite datapack is built by scripts/<builder>; it reports
    <PREFIX>_CHECK / <PREFIX>_DIFF lines and one <PREFIX>_RESULT line, and its
    <ns>:cleanup function restores everything the suite touched.
    """
    if suite not in LIVE_SUITES:
        raise Error(f"unknown live suite {suite!r}; known: {sorted(LIVE_SUITES)}")
    current = client.target()
    if int(current.get("status", -1)) != 1:
        raise Error("innotest must be ONLINE before a live suite")
    builder, out_name = LIVE_SUITES[suite]

    import subprocess
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / builder)])
    out = ROOT / "dist" / out_name
    meta = json.loads((out / "suite.json").read_text(encoding="utf-8"))
    ns, prefix, names = meta["ns"], meta["prefix"], list(meta["players"].values())
    timeout = int(meta.get("timeout_s", 600))
    start_function = str(meta.get("start_function") or f"{ns}:start")
    cleanup_function = str(meta.get("cleanup_function") or f"{ns}:cleanup")

    session_marker = f"{prefix}_SESSION_{int(time.time() * 1000)}"
    client.command(f"say {session_marker} START")
    time.sleep(1)
    deploy(client, "all")
    time.sleep(5)
    payload = zip_tree(out)
    world = level_name(client.read_file("server.properties"))
    remote = f"{world}/datapacks/{out_name}.zip"
    client.write_file(remote, payload)
    print(f"deployed {suite} live suite -> {remote} ({len(payload)} bytes)")
    client.command("reload")
    time.sleep(6)

    def remove_harness():
        try:
            client.delete_file(remote)
        finally:
            try:
                client.command("reload")
            except Error:
                pass

    log = client.log()
    at = log.rfind(f"{session_marker} START")
    if at < 0:
        raise Error("live suite preflight marker not found in server log")
    errors = [line for line in log[at:].splitlines() if "/ERROR]:" in line]
    if errors:
        remove_harness()
        raise Error("live suite preflight found current-session server errors:\n" + "\n".join(errors[:12]))

    wait_named_players(client, names, 240)
    run_marker = f"{prefix}_RUN_{int(time.time() * 1000)}"
    client.command(f"say {run_marker} START")
    time.sleep(1)
    client.command(f"function {start_function}")

    deadline = time.time() + timeout
    result = segment = ""
    printed = 0
    speed_done = 0
    while time.time() < deadline:
        log = client.log()
        marker = log.rfind(f"{run_marker} START")
        if marker >= 0:
            segment = log[marker:]
            # The suite asks for tick-rate changes (functions cannot run /tick).
            for line in segment.splitlines():
                parts = line.split(f"{prefix}_SPEED ", 1)
                if len(parts) == 2:
                    seq_rate = parts[1].split()
                    seq, rate = int(seq_rate[0]), int(seq_rate[1])
                    if seq > speed_done and 1 <= rate <= 10000:
                        client.command(f"tick rate {rate}")
                        client.command(f"scoreboard players set #speed htest {seq}")
                        print(f"tick rate {rate} (request {seq})")
                        speed_done = seq
            lines = [l for l in segment.splitlines() if f"{prefix}_CHECK " in l or f"{prefix}_DIFF " in l]
            for line in lines[printed:]:
                print(line)
            printed = len(lines)
            results = [l for l in segment.splitlines() if f"{prefix}_RESULT " in l]
            if results:
                result = results[-1]
                break
        time.sleep(2)

    try:
        client.command("tick rate 20")
        client.command(f"function {cleanup_function}")
        time.sleep(3)
    except Error:
        pass
    final_log = client.log()
    marker = final_log.rfind(f"{run_marker} START")
    if marker >= 0:
        segment = final_log[marker:]
    restore_lines = [l for l in segment.splitlines() if f"{prefix}_RESTORE" in l or f"{prefix}_CLEANUP" in l]
    for line in restore_lines:
        print(line)
    remove_harness()

    errors = [line for line in segment.splitlines() if "/ERROR]:" in line]
    if errors:
        raise Error(f"{suite} live suite produced current-run server errors:\n" + "\n".join(errors[:12]))
    if f"{prefix}_RESULT PASS" in result:
        print(f"{suite.upper()}_LIVE_SUITE=PASS")
        return
    raise Error(f"{suite} live suite did not pass; result={result or '<missing: timeout>'}")

def wait_status(client, wanted, timeout=180):
    deadline = time.time() + timeout
    while time.time() < deadline:
        server = client.target()
        if int(server.get("status", -1)) == wanted:
            return server
        time.sleep(3)
    raise Error(f"timeout waiting for status {STATUS.get(wanted, wanted)}")

def set_offline_mode(client):
    current = client.target()
    status = int(current.get("status", -1))
    restart_after = status != 0
    if status != 0:
        if status != 1:
            raise Error(f"refusing config change while server is {STATUS.get(status, status)}; retry when stable")
        client.action("stop")
        print("stopping innotest before changing online-mode")
        wait_status(client, 0)

    client.update_config("server.properties", {"online-mode": False})
    print("online-mode=false written to innotest server.properties")

    if restart_after:
        client.action("start")
        print("innotest start requested after config change")
    else:
        print("innotest was already offline; left it offline")

def offline_uuid(name):
    digest = bytearray(hashlib.md5(("OfflinePlayer:" + name).encode("utf-8")).digest())
    digest[6] = (digest[6] & 0x0F) | 0x30
    digest[8] = (digest[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(digest)))

def rewrite_innotest_entity_uuid_refs(client, world, uuid_pairs, stamp):
    """Rewrite production online UUID references in innotest entity region files."""
    try:
        import exaroton_inno_uuid_migrate as migration
        int_mapping, str_mapping = migration.uuid_mappings(uuid_pairs)
        region_files = migration.list_region_files(client, world)
    except Exception as e:
        raise Error(f"cannot prepare innotest entity UUID rewrite: {e}") from e

    changes = []
    total_refs = 0
    for path in region_files:
        path = str(path).lstrip("/")
        raw = client.read_binary_file_optional(path)
        if raw is None:
            continue
        if raw == b"":
            info = client.info_optional(path)
            size = int((info or {}).get("size") or 0)
            if size == 0:
                continue
            raise Error(
                f"binary region download returned 0 bytes for {path} "
                f"but exaroton reports size={size}"
            )
        try:
            transformed, stats = migration.transform_region(
                raw,
                int_mapping=int_mapping,
                str_mapping=str_mapping,
            )
        except Exception as e:
            raise Error(f"cannot rewrite entity UUIDs in {path}: {e}") from e
        if transformed == raw:
            continue

        backup = f"{path}.pre-inno-online-copy-{stamp}.backup"
        client.write_file(backup, raw)
        client.write_file(path, transformed)

        verified = client.read_binary_file_optional(path)
        if verified is None:
            raise Error(f"rewritten entity region disappeared during verification: {path}")
        if hashlib.sha256(verified).digest() != hashlib.sha256(transformed).digest():
            raise Error(f"verification failed after rewriting entity region {path}")
        try:
            verify_again, remaining = migration.transform_region(
                verified,
                int_mapping=int_mapping,
                str_mapping=str_mapping,
            )
        except Exception as e:
            raise Error(f"cannot verify entity UUID rewrite in {path}: {e}") from e
        remaining_refs = int(remaining.get("int_array", 0)) + int(remaining.get("string", 0))
        if verify_again != verified or remaining_refs:
            raise Error(
                f"entity UUID rewrite verification found {remaining_refs} remaining refs in {path}"
            )

        count = int(stats.get("int_array", 0)) + int(stats.get("string", 0))
        total_refs += count
        changes.append({
            "path": path,
            "backup": backup,
            "changed_chunks": int(stats.get("changed_chunks", 0)),
            "uuid_references_rewritten": count,
        })

    return {
        "region_files_scanned": len(region_files),
        "region_files_changed": len(changes),
        "uuid_references_rewritten": total_refs,
        "changes": changes,
    }


def migrate_bot_identities(client):
    current = client.target()
    status = int(current.get("status", -1))
    if status not in (0, 1):
        raise Error(f"refusing identity migration while server is {STATUS.get(status, status)}")

    options = client.get_config("server.properties")
    online_mode = next((item.get("value") for item in options if isinstance(item, dict) and item.get("key") == "online-mode"), None)
    if online_mode is not False:
        raise Error("identity migration requires online-mode=false")

    restart_after = status == 1
    if restart_after:
        client.action("stop")
        print("stopping innotest for offline UUID migration")
        wait_status(client, 0)

    wl_raw = client.read_file("whitelist.json")
    wl = json.loads(wl_raw.decode("utf-8"))
    got_names = [str(e.get("name") or "") for e in wl if isinstance(e, dict)]
    if len(wl) != 4 or {n.lower() for n in got_names} != {n.lower() for n in BOT_PLAYERS}:
        raise Error(f"safety lock: whitelist must contain exactly {', '.join(BOT_PLAYERS)}")

    cache_raw = client.read_file_optional("usercache.json")
    cache = json.loads(cache_raw.decode("utf-8")) if cache_raw else []
    ops_raw = client.read_file_optional("ops.json")
    ops = json.loads(ops_raw.decode("utf-8")) if ops_raw else []
    world = level_name(client.read_file("server.properties"))

    stamp = int(time.time())
    client.write_file(f"whitelist.pre-offline-migration-{stamp}.json", wl_raw)
    if ops_raw is not None:
        client.write_file(f"ops.pre-offline-migration-{stamp}.json", ops_raw)

    summary = {}
    for entry in wl:
        name = str(entry.get("name") or "")
        target_uuid = offline_uuid(name)
        original_uuid = str(entry.get("uuid") or "")
        candidates = []
        for candidate in [original_uuid] + [
            str(e.get("uuid") or "") for e in cache
            if isinstance(e, dict) and str(e.get("name") or "").lower() == name.lower()
        ]:
            if candidate and candidate != target_uuid and candidate not in candidates:
                candidates.append(candidate)

        copied = []
        specs = [
            ("players/data", ".dat"),
            ("players/data", ".dat_old"),
            ("players/advancements", ".json"),
            ("players/stats", ".json"),
        ]
        for folder, suffix in specs:
            dest_path = f"{world}/{folder}/{target_uuid}{suffix}"
            source_data = None
            source_uuid = None
            for candidate in candidates:
                data = client.read_file_optional(f"{world}/{folder}/{candidate}{suffix}")
                if data is not None:
                    source_data = data
                    source_uuid = candidate
                    break
            if source_data is None:
                continue
            existing = client.read_file_optional(dest_path)
            if existing is not None and existing != source_data:
                client.write_file(dest_path + f".pre-migration-{stamp}.backup", existing)
            client.write_file(dest_path, source_data)
            copied.append({"kind": folder + suffix, "from": source_uuid})

        entry["uuid"] = target_uuid
        summary[name] = {"offline_uuid": target_uuid, "copied": copied}

    for op in ops:
        if not isinstance(op, dict):
            continue
        name = str(op.get("name") or "")
        match = next((n for n in BOT_PLAYERS if n.lower() == name.lower()), None)
        if match:
            op["uuid"] = offline_uuid(match)

    client.write_file("whitelist.json", (json.dumps(wl, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    if ops_raw is not None:
        client.write_file("ops.json", (json.dumps(ops, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    print("offline UUID migration complete:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if restart_after:
        client.action("start")
        print("starting innotest after identity migration")
        wait_status(client, 1)
        print("innotest is ONLINE")
    else:
        print("innotest was offline before migration; left offline")


def migrate_inno_online_to_innotest_offline(client, token):
    """Copy the four production online-mode identities into innotest offline UUIDs.

    Source is strictly GET-only inno.exaroton.me. Destination writes are strictly
    hard-locked by APIClient to innotest.exaroton.me.
    """
    source = InnoReadOnlyClient(token)
    source_server = source.target()
    source_status = int(source_server.get("status", -1))
    if source_status != 0:
        raise Error(
            f"safety lock: production inno must remain OFFLINE for migration; "
            f"current status is {STATUS.get(source_status, source_status)}"
        )
    source_sid = source_server["id"]

    source_props = source.read_file_optional(source_sid, "server.properties")
    if source_props is None:
        raise Error("production inno server.properties not found")
    source_world = level_name(source_props)

    source_whitelist = _json_file(source, source_sid, "whitelist.json")
    if not isinstance(source_whitelist, list):
        raise Error("production inno whitelist.json is not a list")

    source_by_name = {}
    for entry in source_whitelist:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name") or "")
        raw_uuid = str(entry.get("uuid") or "")
        if not name or not raw_uuid:
            continue
        try:
            parsed = str(uuid.UUID(raw_uuid))
        except ValueError:
            continue
        source_by_name[name.lower()] = {"name": name, "uuid": parsed}

    missing_names = [name for name in BOT_PLAYERS if name.lower() not in source_by_name]
    if missing_names:
        raise Error(
            "production inno whitelist is missing required players: "
            + ", ".join(missing_names)
        )

    target_server = client.target()
    target_status = int(target_server.get("status", -1))
    if target_status not in (0, 1):
        raise Error(
            f"refusing innotest migration while server is "
            f"{STATUS.get(target_status, target_status)}"
        )

    options = client.get_config("server.properties")
    online_mode = next(
        (
            item.get("value")
            for item in options
            if isinstance(item, dict) and item.get("key") == "online-mode"
        ),
        None,
    )
    if online_mode is not False:
        raise Error("innotest migration requires online-mode=false")

    restart_after = target_status == 1
    if restart_after:
        client.action("stop")
        print("stopping innotest before copying production online UUID data")
        wait_status(client, 0)

    target_world = level_name(client.read_file("server.properties"))
    stamp = int(time.time())
    try:
        import exaroton_inno_uuid_migrate as migration
        uuid_pairs = [
            (source_by_name[name.lower()]["uuid"], offline_uuid(name))
            for name in BOT_PLAYERS
        ]
        int_mapping, str_mapping = migration.uuid_mappings(uuid_pairs)
    except Exception as e:
        raise Error(f"cannot prepare online-to-offline UUID mapping: {e}") from e

    whitelist_raw = client.read_file("whitelist.json")
    whitelist = json.loads(whitelist_raw.decode("utf-8"))
    if not isinstance(whitelist, list):
        raise Error("innotest whitelist.json is not a list")

    whitelist_names = {
        str(e.get("name") or "").lower()
        for e in whitelist
        if isinstance(e, dict)
    }
    required_names = {name.lower() for name in BOT_PLAYERS}
    if whitelist_names != required_names or len(whitelist) != 4:
        raise Error(
            "safety lock: innotest whitelist must contain exactly "
            + ", ".join(BOT_PLAYERS)
        )

    ops_raw = client.read_file_optional("ops.json")
    ops = json.loads(ops_raw.decode("utf-8")) if ops_raw else []

    entity_rewrite = rewrite_innotest_entity_uuid_refs(
        client, target_world, uuid_pairs, stamp
    )

    client.write_file(
        f"whitelist.pre-inno-online-copy-{stamp}.json",
        whitelist_raw,
    )
    if ops_raw is not None:
        client.write_file(
            f"ops.pre-inno-online-copy-{stamp}.json",
            ops_raw,
        )

    result = {}
    # Minecraft Java 26.3 stores per-player files below world/players/*.
    specs = [
        ("players/data", ".dat"),
        ("players/data", ".dat_old"),
        ("players/advancements", ".json"),
        ("players/stats", ".json"),
    ]

    for name in BOT_PLAYERS:
        source_uuid = source_by_name[name.lower()]["uuid"]
        target_uuid = offline_uuid(name)
        copied = []
        missing = []

        for folder, suffix in specs:
            source_path = f"{source_world}/{folder}/{source_uuid}{suffix}"
            target_path = f"{target_world}/{folder}/{target_uuid}{suffix}"
            source_data = source.read_file_optional(source_sid, source_path)

            if source_data is None:
                missing.append(f"{folder}{suffix}")
                continue

            payload = source_data
            nbt_uuid_rewrites = 0
            if folder == "players/data":
                try:
                    payload, nbt_meta = migration.transform_player_nbt(
                        source_data,
                        int_mapping=int_mapping,
                        str_mapping=str_mapping,
                    )
                except Exception as e:
                    raise Error(f"cannot rewrite UUID references in {source_path}: {e}") from e
                nbt_uuid_rewrites = int(nbt_meta.get("int_array", 0)) + int(nbt_meta.get("string", 0))

            existing = client.read_file_optional(target_path)
            if existing is not None and existing != payload:
                client.write_file(
                    target_path + f".pre-inno-online-copy-{stamp}.backup",
                    existing,
                )

            client.write_file(target_path, payload)
            verified = client.read_file(target_path)
            if hashlib.sha256(verified).digest() != hashlib.sha256(payload).digest():
                raise Error(f"verification failed after writing {target_path}")

            copied.append(
                {
                    "kind": f"{folder}{suffix}",
                    "source_online_uuid": source_uuid,
                    "target_offline_uuid": target_uuid,
                    "bytes": len(payload),
                    "internal_uuid_references_rewritten": nbt_uuid_rewrites,
                }
            )

        for entry in whitelist:
            if (
                isinstance(entry, dict)
                and str(entry.get("name") or "").lower() == name.lower()
            ):
                entry["uuid"] = target_uuid

        for entry in ops:
            if (
                isinstance(entry, dict)
                and str(entry.get("name") or "").lower() == name.lower()
            ):
                entry["uuid"] = target_uuid

        result[name] = {
            "source_online_uuid": source_uuid,
            "target_offline_uuid": target_uuid,
            "copied": copied,
            "missing_source_files": missing,
        }

    client.write_file(
        "whitelist.json",
        (json.dumps(whitelist, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )
    if ops_raw is not None:
        client.write_file(
            "ops.json",
            (json.dumps(ops, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )

    print("copied production inno online UUID data into innotest offline UUIDs:")
    print(json.dumps({
        "players": result,
        "entity_uuid_rewrite": entity_rewrite,
    }, ensure_ascii=False, indent=2))

    if restart_after:
        client.action("start")
        print("starting innotest after production-data copy")
        wait_status(client, 1)
        print("innotest is ONLINE")
    else:
        print("innotest was offline before migration; left offline")


def run_warehouse_compact_live_test(client):
    """Run a focused live regression for compact arithmetic direct dispatch."""
    current = client.target()
    if int(current.get("status", -1)) != 1:
        raise Error("innotest must be ONLINE before Warehouse compact live testing")

    marker = f"WH_COMPACT_LIVE_{int(time.time() * 1000)}"
    ax, ay, az = -430, 250, 120
    bx, by, bz = -428, 250, 120
    force_from = "-430 120"
    force_to = "-428 120"

    setup = [
        f"say {marker} START",
        "scoreboard players operation #whc_old_enabled wh_sys = #enabled wh_sys",
        "scoreboard players operation #whc_old_code wh_tmp = #compact_code wh_tmp",
        "scoreboard players operation #whc_old_slot wh_tmp = #compact_slot wh_tmp",
        "scoreboard players set #enabled wh_sys 0",
        "execute store success score #whc_had wh_tmp run data get storage warehouse:chests c69",
        "data remove storage warehouse:runtime compact_live_backup",
        "data modify storage warehouse:runtime compact_live_backup set from storage warehouse:chests c69",
        f"forceload add {force_from} {force_to}",
        f"setblock {ax} {ay} {az} minecraft:chest",
        f"setblock {bx} {by} {bz} minecraft:chest",
        (
            "data modify storage warehouse:chests c69 set value "
            f'{{registered:1b,valid:1b,dimension:"minecraft:overworld",'
            f"a_x:{ax},a_y:{ay},a_z:{az},b_x:{bx},b_y:{by},b_z:{bz}}}"
        ),
        f'data modify block {ax} {ay} {az} Items set value ['
        '{Slot:0b,id:"minecraft:diamond",count:10},'
        '{Slot:5b,id:"minecraft:diamond",count:10}]',
        f'data modify block {bx} {by} {bz} Items set value ['
        '{Slot:3b,id:"minecraft:diamond",count:7}]',
        "scoreboard players set #compact_code wh_tmp 60",
        "scoreboard players set #compact_slot wh_tmp 0",
    ]

    try:
        for command in setup:
            client.command(command)
            time.sleep(0.15)

        # First call must direct-dispatch code 60 to c69 and process A slot 0.
        client.command("function warehouse:compact/step")
        client.command(
            f"execute if score #compact_active wh_tmp matches 1 "
            f"if score #compact_code wh_tmp matches 60 "
            f"if score #compact_slot wh_tmp matches 1 "
            f"run say {marker} CODE_PASS"
        )

        # Advance through A slot 5; the second 10-stack should merge into slot 0.
        for _ in range(5):
            client.command("function warehouse:compact/step")
        client.command(
            f'execute if data block {ax} {ay} {az} '
            'Items[{Slot:0b,id:"minecraft:diamond",count:20}] '
            f'unless data block {ax} {ay} {az} Items[{{Slot:5b,id:"minecraft:diamond"}}] '
            f'run say {marker} A_PASS'
        )

        # Advance from global slot 6 through global slot 30 (B local slot 3).
        for _ in range(25):
            client.command("function warehouse:compact/step")
        client.command(
            f'execute if data block {ax} {ay} {az} '
            'Items[{Slot:0b,id:"minecraft:diamond",count:27}] '
            f'unless data block {bx} {by} {bz} Items[{{Slot:3b,id:"minecraft:diamond"}}] '
            f'run say {marker} B_PASS'
        )

        # Finish the cycle and verify cursor wrap semantics.
        for _ in range(23):
            client.command("function warehouse:compact/step")
        client.command(
            f"execute if score #compact_code wh_tmp matches 0 "
            f"if score #compact_slot wh_tmp matches 0 "
            f"run say {marker} WRAP_PASS"
        )
        time.sleep(2)

        log = client.log()
        start_at = log.rfind(f"{marker} START")
        if start_at < 0:
            raise Error("Warehouse compact live marker not found in server log")
        segment = log[start_at:]
        current_errors = [
            line for line in segment.splitlines()
            if (
                "/ERROR]:" in line
                or "Unknown or incomplete command" in line
                or "Unknown function" in line
                or "<--[HERE]" in line
            )
        ]
        if current_errors:
            raise Error(
                "Warehouse compact live test produced server/command errors:\n"
                + "\n".join(current_errors[:12])
            )

        required = ("CODE_PASS", "A_PASS", "B_PASS", "WRAP_PASS")
        missing = [name for name in required if f"{marker} {name}" not in segment]
        if missing:
            # Persist diagnostics into the server log before cleanup.
            diagnostic_commands = [
                f"data get block {ax} {ay} {az} Items",
                f"data get block {bx} {by} {bz} Items",
                "scoreboard players get #compact_active wh_tmp",
                "scoreboard players get #compact_code wh_tmp",
                "scoreboard players get #compact_slot wh_tmp",
                "data get storage warehouse:runtime compact",
            ]
            for command in diagnostic_commands:
                try:
                    client.command(command)
                except Error:
                    pass
            time.sleep(1)
            debug = client.log()
            debug_start = debug.rfind(f"{marker} START")
            raise Error(
                "Warehouse compact live test missing checkpoints "
                + ", ".join(missing)
                + "; current session tail:\n"
                + "\n".join(debug[debug_start:].splitlines()[-60:])
            )

        print("WAREHOUSE_COMPACT_LIVE_TEST=PASS")
        print("  code 60 -> c69 direct dispatch: PASS")
        print("  A global/local slot mapping and merge: PASS")
        print("  B global 30 -> local slot 3 mapping and merge: PASS")
        print("  54-slot cursor wrap to code 0 / slot 0: PASS")
    finally:
        cleanup = [
            f"setblock {ax} {ay} {az} minecraft:air",
            f"setblock {bx} {by} {bz} minecraft:air",
            f"forceload remove {force_from} {force_to}",
            (
                "execute if score #whc_had wh_tmp matches 1 "
                "run data modify storage warehouse:chests c69 "
                "set from storage warehouse:runtime compact_live_backup"
            ),
            (
                "execute unless score #whc_had wh_tmp matches 1 "
                "run data remove storage warehouse:chests c69"
            ),
            "data remove storage warehouse:runtime compact_live_backup",
            "scoreboard players operation #compact_code wh_tmp = #whc_old_code wh_tmp",
            "scoreboard players operation #compact_slot wh_tmp = #whc_old_slot wh_tmp",
            "scoreboard players operation #enabled wh_sys = #whc_old_enabled wh_sys",
            "scoreboard players reset #whc_had wh_tmp",
            "scoreboard players reset #whc_old_code wh_tmp",
            "scoreboard players reset #whc_old_slot wh_tmp",
            "scoreboard players reset #whc_old_enabled wh_sys",
        ]
        for command in cleanup:
            try:
                client.command(command)
            except Error:
                pass


def run_utilities_bfs_live_test(client):
    """Run a focused live regression for the foliage shell-order optimization."""
    current = client.target()
    if int(current.get("status", -1)) != 1:
        raise Error("innotest must be ONLINE before utilities BFS live testing")

    marker = f"UTIL_BFS_LIVE_{int(time.time() * 1000)}"
    area = "-375 243 90 -345 276 105"
    force_from = "-375 90"
    force_to = "-345 105"
    scores = ("#bfs_near", "#bfs_far", "#bfs_xout", "#bfs_yout", "#bfs_none")

    commands = [
        f"say {marker} START",
        f"forceload add {force_from} {force_to}",
        f"fill {area} minecraft:air",
        "setblock -350 260 100 minecraft:oak_leaves[persistent=true]",
        "execute positioned -350 260 100 store result score #bfs_near su_tmp run function survival_utils:tree/check_foliage",
        "execute positioned -355 244 95 store result score #bfs_far su_tmp run function survival_utils:tree/check_foliage",
        "execute positioned -356 244 95 store result score #bfs_xout su_tmp run function survival_utils:tree/check_foliage",
        "execute positioned -355 243 95 store result score #bfs_yout su_tmp run function survival_utils:tree/check_foliage",
        "execute positioned -370 244 95 store result score #bfs_none su_tmp run function survival_utils:tree/check_foliage",
        (
            "execute if score #bfs_near su_tmp matches 1 "
            "if score #bfs_far su_tmp matches 1 "
            "if score #bfs_xout su_tmp matches 0 "
            "if score #bfs_yout su_tmp matches 0 "
            "if score #bfs_none su_tmp matches 0 "
            f"run say {marker} PASS"
        ),
    ]

    try:
        for command in commands:
            client.command(command)
            time.sleep(0.75)
        time.sleep(2)

        log = client.log()
        start = log.rfind(f"{marker} START")
        if start < 0:
            raise Error("utilities BFS live marker not found in server log")
        segment = log[start:]
        current_errors = [
            line for line in segment.splitlines()
            if (
                "/ERROR]:" in line
                or "Unknown or incomplete command" in line
                or "Unknown function" in line
                or "<--[HERE]" in line
            )
        ]
        if current_errors:
            raise Error(
                "utilities BFS live test produced server/command errors:\n"
                + "\n".join(current_errors[:12])
            )
        if f"{marker} PASS" not in segment:
            for score in scores:
                try:
                    client.command(f"scoreboard players get {score} su_tmp")
                except Error:
                    pass
            time.sleep(1)
            debug = client.log()
            debug_start = debug.rfind(f"{marker} START")
            raise Error(
                "utilities BFS live test did not pass; current session tail:\n"
                + "\n".join(debug[debug_start:].splitlines()[-40:])
            )

        print("UTILITIES_BFS_LIVE_TEST=PASS")
        print("  shell0 hit -> 1")
        print("  far legal boundary (+5,+16,+5) -> 1")
        print("  x outside (+6,+16,+5) -> 0")
        print("  y outside (+5,+17,+5) -> 0")
        print("  unrelated origin -> 0")
    finally:
        cleanup = [
            f"fill {area} minecraft:air",
            f"forceload remove {force_from} {force_to}",
            *[f"scoreboard players reset {score} su_tmp" for score in scores],
            "scoreboard players set #leaf su_tmp 0",
        ]
        for command in cleanup:
            try:
                client.command(command)
            except Error:
                pass

def run(path):
    try: r = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e: raise Error(f"invalid request file: {path}") from e
    if not isinstance(r, dict): raise Error("request must be a JSON object")
    unknown = set(r) - {"request_id", "operation", "command", "pack"}
    if unknown: raise Error(f"unsupported request fields: {', '.join(sorted(unknown))}")
    op = str(r.get("operation") or "").strip()
    print(f"request {r.get('request_id')}: {op}")
    if op == "noop": return
    client = APIClient(os.environ.get("EXAROTON_API_TOKEN", ""))
    if op == "status":
        s = client.target(); code = int(s.get("status", -1))
        print(json.dumps({"id":s.get("id"),"name":s.get("name"),"address":s.get("address"),"status":code,"status_name":STATUS.get(code,"UNKNOWN"),"players":s.get("players"),"software":s.get("software")}, ensure_ascii=False, indent=2))
    elif op == "log": print(client.log())
    elif op in {"start", "stop", "restart"}: client.action(op); print(f"{op} requested for {TARGET}")
    elif op == "command": client.command(str(r.get("command") or "")); print(f"command sent to {TARGET}")
    elif op == "deploy-datapack": deploy(client, str(r.get("pack") or ""))
    elif op == "run-copy-paste-multiplayer-test": run_copy_paste_multiplayer_test(client)
    elif op == "run-blueprint-matcher-live-test": run_blueprint_matcher_live_test(client)
    elif op == "run-warehouse-compact-live-test": run_warehouse_compact_live_test(client)
    elif op == "run-live-suite": run_live_suite(client, str(r.get("pack") or ""))
    elif op == "run-utilities-bfs-live-test": run_utilities_bfs_live_test(client)
    elif op == "set-online-mode-false": set_offline_mode(client)
    elif op == "online-mode-status":
        options = client.get_config("server.properties")
        online = next((item.get("value") for item in options if isinstance(item, dict) and item.get("key") == "online-mode"), None)
        server = client.target()
        code = int(server.get("status", -1))
        print(json.dumps({"online-mode": online, "server_status": STATUS.get(code, "UNKNOWN")}, ensure_ascii=False))
    elif op == "whitelist-status":
        entries = json.loads(client.read_file("whitelist.json").decode("utf-8"))
        print(json.dumps([{"name":e.get("name"),"uuid":e.get("uuid")} for e in entries], ensure_ascii=False, indent=2))
    elif op == "identity-status":
        wl = json.loads(client.read_file("whitelist.json").decode("utf-8"))
        names = {str(e.get("name") or "").lower() for e in wl}
        try:
            cache = json.loads(client.read_file("usercache.json").decode("utf-8"))
        except Error:
            cache = []
        try:
            ops = json.loads(client.read_file("ops.json").decode("utf-8"))
        except Error:
            ops = []
        result = {
            "whitelist": wl,
            "usercache_matches": [e for e in cache if str(e.get("name") or "").lower() in names],
            "ops_matches": [e for e in ops if str(e.get("name") or "").lower() in names],
            "world": level_name(client.read_file("server.properties")),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif op == "migrate-offline-bot-identities":
        migrate_bot_identities(client)
    elif op == "migrate-inno-online-to-innotest-offline":
        migrate_inno_online_to_innotest_offline(
            client,
            os.environ.get("EXAROTON_API_TOKEN", ""),
        )
    elif op == "bot-log-status":
        lines = client.log().splitlines()
        keys = [n.lower() for n in BOT_PLAYERS] + ["disconnect", "lost connection", "kicked", "uuid"]
        selected = [line for line in lines[-800:] if any(k in line.lower() for k in keys)]
        print("\n".join(selected[-200:]))
    elif op == "inno-identity-status":
        print(json.dumps(inno_identity_status(os.environ.get("EXAROTON_API_TOKEN", "")), ensure_ascii=False, indent=2))
    elif op == "inno-storage-status":
        print(json.dumps(inno_storage_status(os.environ.get("EXAROTON_API_TOKEN", "")), ensure_ascii=False, indent=2))
    elif op == "inno-world-layout-status":
        print(json.dumps(inno_world_layout_status(os.environ.get("EXAROTON_API_TOKEN", "")), ensure_ascii=False, indent=2))
    elif op in {"inno-uuid-migrate-dry-run", "inno-uuid-migrate-apply"}:
        import subprocess
        import site
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "nbtlib==1.12.1"])
        site.addsitedir(site.getusersitepackages())
        import exaroton_inno_uuid_migrate as migration
        original_remote_path = migration.remote_path
        migration.remote_path = lambda p: original_remote_path(str(p).lstrip("/"))

        def _read_file_optional(self, path):
            try:
                data = self.req(
                    "GET",
                    f"/servers/{self._sidq()}/files/data/{migration.remote_path(path)}",
                    raw_response=True,
                )
                if data == b"" and str(path).endswith(".mca"):
                    info = self.info_optional(path)
                    size = int((info or {}).get("size") or 0)
                    if size == 0:
                        print(f"skipping empty region file: {path}")
                        return None
                    raise migration.Error(
                        f"binary region download returned 0 bytes for {path} "
                        f"but exaroton reports size={size}"
                    )
                return data
            except migration.Error as e:
                if "HTTP 404" in str(e):
                    return None
                raise

        def _write_file(self, path, data):
            self.require_offline()
            self.req(
                "PUT",
                f"/servers/{self._sidq()}/files/data/{migration.remote_path(path)}/",
                raw=data,
            )

        migration.Client.read_file_optional = _read_file_optional
        migration.Client.write_file = _write_file
        migration.plan_or_apply("dry-run" if op.endswith("dry-run") else "apply")
    elif op == "inno-uuid-migrate-verify":
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "nbtlib==1.12.1"])
        import exaroton_inno_uuid_migrate as migration
        original_remote_path = migration.remote_path
        migration.remote_path = lambda p: original_remote_path(str(p).lstrip("/"))
        verifier = migration.Client(os.environ.get("EXAROTON_API_TOKEN", ""))
        server = verifier.require_offline()
        manifest_name = str(r.get("command") or "").strip()
        if not manifest_name.startswith("uuid-migration-") or not manifest_name.endswith(".json"):
            raise Error("verification requires uuid-migration-*.json manifest name")
        manifest_raw = verifier.read_file_optional(manifest_name)
        if manifest_raw is None:
            raise Error(f"migration manifest not found: {manifest_name}")
        manifest = json.loads(manifest_raw.decode("utf-8"))
        writes = manifest.get("writes") if isinstance(manifest, dict) else None
        if not isinstance(writes, list):
            raise Error("migration manifest has no writes list")
        checked = []
        for item in writes:
            if not isinstance(item, dict):
                raise Error("invalid migration manifest write entry")
            path = str(item.get("path") or "")
            expected = str(item.get("new_sha256") or "")
            current = verifier.read_file_optional(path)
            if current is None:
                raise Error(f"verification missing written file: {path}")
            actual = hashlib.sha256(current).hexdigest()
            if expected and actual != expected:
                raise Error(f"verification checksum mismatch: {path}")
            old_refs = 0
            if path.endswith(".mca"):
                transformed, stats = migration.transform_region(current)
                old_refs = int(stats.get("int_array", 0)) + int(stats.get("string", 0))
                if transformed != current or old_refs:
                    raise Error(f"verification found remaining offline UUID refs in {path}: {old_refs}")
            checked.append({"path": path, "sha256_ok": True, "remaining_old_uuid_refs": old_refs})
        cache = json.loads(verifier.read_file_optional("usercache.json").decode("utf-8"))
        typo_left = [
            e for e in cache
            if isinstance(e, dict) and (
                str(e.get("name") or "").lower() == migration.TYPO_NAME.lower()
                or migration.normalize_uuid_string(str(e.get("uuid") or "")) == str(uuid.UUID(migration.TYPO_UUID))
            )
        ]
        if typo_left:
            raise Error("verification found penguin531 still present in usercache.json")
        print(json.dumps({
            "server_status": int(server.get("status", -1)),
            "server_status_name": STATUS.get(int(server.get("status", -1)), "UNKNOWN"),
            "manifest": manifest_name,
            "files_verified": len(checked),
            "penguin531_entries": 0,
            "checked": checked,
        }, ensure_ascii=False, indent=2))
    else: raise Error(f"unsupported operation: {op}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: exaroton_innotest.py REQUEST.json", file=sys.stderr); raise SystemExit(2)
    try: run(sys.argv[1])
    except Error as e: print(f"ERROR: {e}", file=sys.stderr); raise SystemExit(2)
