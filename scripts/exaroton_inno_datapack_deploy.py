#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

API = "https://api.exaroton.com/v1"
TARGET = "inno.exaroton.me"
STATUS_OFFLINE = 0

DESIRED = {
    "utilities": "utilities-v3.8.zip",
    "warehouse": "warehouse-v4.7.zip",
    "copy-paste": "copy-paste-v1.8.zip",
}

LEGACY_PATTERNS = {
    "utilities": re.compile(r"^(?:utilities(?:-v\d+\.\d+)?|survival[_-]?utilities(?:-v\d+\.\d+)?)\.zip$", re.I),
    "warehouse": re.compile(r"^(?:warehouse(?:-v\d+\.\d+)?|Minecraft_Warehouse_26\.3_v\d+\.\d+)\.zip$", re.I),
    "copy-paste": re.compile(r"^(?:copy-paste(?:-v\d+\.\d+)?|copy_paste(?:-v\d+\.\d+)?)\.zip$", re.I),
}


class Error(RuntimeError):
    pass


def addr(value):
    return str(value or "").strip().rstrip(".").lower()


def remote_path(path: str) -> str:
    p = PurePosixPath(path)
    if p.is_absolute() or not p.parts or any(part in ("", ".", "..") for part in p.parts):
        raise Error(f"unsafe remote path: {path!r}")
    return "/".join(urllib.parse.quote(part, safe="") for part in p.parts)


class Client:
    """Production datapack client: no server lifecycle or console-command methods exist."""

    def __init__(self, token: str, opener=urllib.request.urlopen):
        token = token.strip()
        if not token:
            raise Error("EXAROTON_API_TOKEN is not configured")
        self.token = token
        self.opener = opener
        self._sid = None

    def req(self, method: str, path: str, *, raw=None, raw_response=False):
        if method not in {"GET", "PUT", "DELETE"}:
            raise Error(f"blocked HTTP method for production datapack deploy: {method}")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "packs-minecraft-inno/1 production-datapack-deploy",
        }
        if raw is not None:
            headers["Content-Type"] = "application/octet-stream"
        request = urllib.request.Request(API + path, data=raw, headers=headers, method=method)
        try:
            with self.opener(request, timeout=60) as response:
                data = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            raise Error(f"exaroton HTTP {exc.code}: {detail or exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise Error(f"cannot reach exaroton API: {exc.reason}") from exc
        if raw_response:
            return data
        if not data:
            return None
        try:
            result = json.loads(data.decode())
        except Exception as exc:
            raise Error("exaroton returned invalid JSON") from exc
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
            raise Error("safety lock: production inno has no server id")
        server = self.req("GET", f"/servers/{urllib.parse.quote(str(sid), safe='')}")
        if addr(server.get("address")) != TARGET:
            raise Error("safety lock: production target verification failed")
        self._sid = sid
        return server

    def require_offline(self):
        server = self.target()
        status = int(server.get("status", -1))
        if status != STATUS_OFFLINE:
            raise Error(f"refusing datapack mutation: {TARGET} status is {status}, not OFFLINE")
        return server

    def _sidq(self):
        if self._sid is None:
            self.target()
        return urllib.parse.quote(str(self._sid), safe="")

    def read_file(self, path: str) -> bytes:
        return self.req(
            "GET",
            f"/servers/{self._sidq()}/files/data/{remote_path(path)}/",
            raw_response=True,
        )

    def file_info(self, path: str):
        return self.req("GET", f"/servers/{self._sidq()}/files/info/{remote_path(path)}/")

    def write_file(self, path: str, data: bytes):
        self.require_offline()
        self.req("PUT", f"/servers/{self._sidq()}/files/data/{remote_path(path)}/", raw=data)

    def delete_file(self, path: str):
        self.require_offline()
        self.req("DELETE", f"/servers/{self._sidq()}/files/data/{remote_path(path)}/")


def level_name(raw: bytes) -> str:
    world = "world"
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.strip().startswith("level-name="):
            world = line.split("=", 1)[1].strip() or "world"
            break
    remote_path(world)
    return world


def child_names(info) -> list[str]:
    if not isinstance(info, dict):
        return []
    out = []
    for child in info.get("children") or []:
        if isinstance(child, dict):
            name = str(child.get("name") or "")
            if name:
                out.append(name)
    return sorted(out)


def recognized_pack(name: str):
    for pack, pattern in LEGACY_PATTERNS.items():
        if pattern.fullmatch(name):
            return pack
    return None


def main():
    root = Path(os.environ.get("INNO_DATAPACK_DIR", "dist/inno-deploy"))
    payloads = {}
    for pack, filename in DESIRED.items():
        path = root / filename
        if not path.is_file():
            raise Error(f"missing release asset: {path}")
        data = path.read_bytes()
        if len(data) < 100:
            raise Error(f"release asset is unexpectedly small: {path}")
        payloads[pack] = data

    client = Client(os.environ.get("EXAROTON_API_TOKEN", ""))
    server = client.require_offline()
    properties = client.read_file("server.properties")
    world = level_name(properties)
    datapacks_dir = f"{world}/datapacks"

    before = child_names(client.file_info(datapacks_dir))
    print(json.dumps({
        "target": server.get("address"),
        "status": int(server.get("status", -1)),
        "world": world,
        "before": before,
        "desired": list(DESIRED.values()),
    }, ensure_ascii=False, indent=2))

    # Upload every desired release first. If an upload fails, legacy files remain,
    # and the server is still offline, so we do not leave production without a pack.
    for pack, filename in DESIRED.items():
        dst = f"{datapacks_dir}/{filename}"
        client.write_file(dst, payloads[pack])
        print(f"uploaded {pack} -> {dst} ({len(payloads[pack])} bytes)")

    # Remove only old ZIPs that are positively recognized as one of our three packs.
    for name in before:
        pack = recognized_pack(name)
        if not pack:
            continue
        if name == DESIRED[pack]:
            continue
        client.delete_file(f"{datapacks_dir}/{name}")
        print(f"removed old {pack} datapack -> {name}")

    client.require_offline()
    after = child_names(client.file_info(datapacks_dir))
    missing = [name for name in DESIRED.values() if name not in after]
    stale = [
        name for name in after
        if (pack := recognized_pack(name)) and name != DESIRED[pack]
    ]
    if missing or stale:
        raise Error(f"post-deploy verification failed: missing={missing}, stale={stale}")

    print(json.dumps({
        "status": "PASS",
        "server": TARGET,
        "server_remains_offline": True,
        "world": world,
        "after": after,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
