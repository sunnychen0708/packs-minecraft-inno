#!/usr/bin/env python3
"""GitHub Actions control for exaroton test server; writes are hard-locked to innotest."""
from __future__ import annotations

import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

API = "https://api.exaroton.com/v1"
TARGET = "innotest.exaroton.me"
PACKS = ("utilities", "warehouse", "copy-paste")
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

    def write_file(self, path, content):
        server = self.target(); server = self.verify(server["id"])
        sid = urllib.parse.quote(str(server["id"]), safe="")
        self.req("PUT", f"/servers/{sid}/files/data/{remote_path(path)}/", raw=content)

    def update_config(self, path, values):
        server = self.target(); server = self.verify(server["id"])
        sid = urllib.parse.quote(str(server["id"]), safe="")
        return self.req("POST", f"/servers/{sid}/files/config/{remote_path(path)}/", obj=values)

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
    elif op == "set-online-mode-false": set_offline_mode(client)
    else: raise Error(f"unsupported operation: {op}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: exaroton_innotest.py REQUEST.json", file=sys.stderr); raise SystemExit(2)
    try: run(sys.argv[1])
    except Error as e: print(f"ERROR: {e}", file=sys.stderr); raise SystemExit(2)
