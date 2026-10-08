#!/usr/bin/env python3
"""Publish the read-only inno cat/wolf advancement report to one Discord webhook message.

Reads a JSON report created by inno-animal-progress.yml.  This module never
sends commands to Minecraft/exaroton or changes the world.  The webhook URL is
read from a GitHub Actions secret, never from repository files.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPOSITORY = "sunnychen0708/packs-minecraft-inno"
STATE_PATH = "ops/discord-animal-message.json"
PLAYERS = ("SunnyChen", "penguin0531", "geena0701", "Felicitypeng")

CATS = {
    "tabby": "虎斑", "black": "黑貓", "red": "橘貓", "siamese": "暹羅貓",
    "british_shorthair": "英國短毛貓", "calico": "三花貓",
    "persian": "波斯貓", "ragdoll": "布偶貓", "white": "白貓",
    "jellie": "Jellie", "all_black": "全黑貓",
}
WOLVES = {
    "ashen": "灰狼", "black": "黑狼", "chestnut": "栗色狼",
    "pale": "蒼白狼", "rusty": "鏽色狼", "snowy": "雪狼",
    "spotted": "斑點狼", "striped": "條紋狼", "woods": "林地狼",
}


class PublishError(RuntimeError):
    pass


def validate_webhook_url(value: str) -> tuple[str, str]:
    """Return sanitized canonical URL and non-secret webhook ID."""
    parts = urllib.parse.urlsplit(value.strip())
    path = re.fullmatch(
        r"/api(?:/v\d+)?/webhooks/(\d+)/([A-Za-z0-9._-]+)",
        parts.path,
    )
    if (
        parts.scheme != "https"
        or parts.hostname not in ("discord.com", "discordapp.com")
        or parts.port not in (None, 443)
        or parts.username is not None
        or parts.password is not None
        or parts.query or parts.fragment
        or not path
    ):
        raise PublishError("DISCORD_WEBHOOK_URL must be an HTTPS Discord webhook URL")
    return "https://discord.com/api/webhooks/" + path.group(1) + "/" + path.group(2), path.group(1)


def validate_report(report: dict) -> None:
    if not isinstance(report, dict) or report.get("server") != "inno.exaroton.me":
        raise PublishError("Report is not from the production inno server")
    if report.get("read_only") is not True:
        raise PublishError("Refusing to publish a report not marked read-only")
    if not isinstance(report.get("players"), dict) or set(report["players"]) != set(PLAYERS):
        raise PublishError("Expected exactly the four approved player reports")
    for name in PLAYERS:
        player = report["players"][name]
        if not isinstance(player, dict):
            raise PublishError("Malformed report for " + name)
        for key, names in (("cats", CATS), ("wolves", WOLVES)):
            progress = player.get(key)
            if not isinstance(progress, dict) or not isinstance(progress.get("collected"), list):
                raise PublishError("Missing progress for " + name + "/" + key)
            if not isinstance(progress.get("missing"), list):
                raise PublishError("Missing variant list for " + name + "/" + key)
            collected, missing = progress["collected"], progress["missing"]
            if (
                len(collected) != len(set(collected))
                or len(missing) != len(set(missing))
                or set(collected) | set(missing) != set(names)
                or set(collected) & set(missing)
                or progress.get("total") != len(names)
                or progress.get("count") != len(collected)
                or progress.get("unknown_criteria")
            ):
                raise PublishError("Inconsistent or unknown criteria for " + name + "/" + key)


def progress_line(kind: str, data: dict, dictionary: dict[str, str]) -> str:
    missing = "、".join(dictionary[item] for item in data["missing"]) or "無 ✅"
    icon = "🐱" if kind == "cats" else "🐺"
    label = "貓" if kind == "cats" else "狼"
    return f"{icon} **{label} {data['count']}/{data['total']}**｜缺少：{missing}"


def discord_payload(report: dict, *, now: datetime | None = None) -> dict:
    validate_report(report)
    now = now or datetime.now(timezone.utc)
    players = report["players"]
    cat_union = set().union(*(players[p]["cats"]["collected"] for p in PLAYERS))
    wolf_union = set().union(*(players[p]["wolves"]["collected"] for p in PLAYERS))
    fields = []
    for name in PLAYERS:
        entry = players[name]
        fields.append({
            "name": name,
            "value": (
                progress_line("cats", entry["cats"], CATS) + "\n"
                + progress_line("wolves", entry["wolves"], WOLVES)
            ),
            "inline": False,
        })
    remaining_cats = "、".join(CATS[item] for item in CATS if item not in cat_union) or "無 ✅"
    remaining_wolves = "、".join(WOLVES[item] for item in WOLVES if item not in wolf_union) or "無 ✅"
    fields.append({
        "name": "全服合計",
        "value": (
            f"🐱 貓 **{len(cat_union)}/11**｜全服未收集：{remaining_cats}\n"
            f"🐺 狼 **{len(wolf_union)}/9**｜全服未收集：{remaining_wolves}"
        ),
        "inline": False,
    })
    status = "OFFLINE" if report.get("server_status_code") == 0 else "ONLINE／其他"
    payload = {
        "allowed_mentions": {"parse": []},
        "embeds": [{
            "title": "🐱 貓與狼收集圖鑑 🐺",
            "description": (
                "四位玩家的**曾馴服花色進度**，不是目前存活寵物數。\n"
                f"資料來源：inno 存檔｜讀取時伺服器狀態：{status}"
            ),
            "color": 0x5865F2,
            "fields": fields,
            "footer": {"text": "手動更新 • 唯讀存檔 • 已馴服的種類不因寵物死亡而消失"},
            "timestamp": now.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }],
    }
    if sum(len(field["name"]) + len(field["value"]) for field in fields) > 5600:
        raise PublishError("Discord embed is too long")
    return payload


def send_json(method: str, url: str, payload: dict | None = None, *, token: str | None = None,
              allow_missing: bool = False) -> dict | None:
    """HTTPS JSON request; sanitize errors so webhook token is never printed."""
    headers = {
        "User-Agent": "inno-animal-collection/1.0",
        "Accept": "application/json",
    }
    if token:
        headers.update({
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        if allow_missing and exc.code == 404:
            return None
        raise PublishError(f"{'GitHub' if token else 'Discord'} {method} returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError):
        raise PublishError(f"{'GitHub' if token else 'Discord'} {method} connection failed") from None
    if not body:
        return {}
    try:
        return json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise PublishError(f"{'GitHub' if token else 'Discord'} returned invalid JSON") from None


def state_url(repo: str) -> str:
    if repo != REPOSITORY:
        raise PublishError("Refusing to write state outside the approved repository")
    return f"https://api.github.com/repos/{repo}/contents/{STATE_PATH}"


def get_state(repo: str, token: str) -> tuple[dict, str | None]:
    obj = send_json("GET", state_url(repo), token=token, allow_missing=True)
    if obj is None:
        return {}, None
    try:
        raw = base64.b64decode(obj["content"], validate=False)
        state = json.loads(raw)
        if not isinstance(state, dict):
            raise ValueError("not a JSON object")
        return state, str(obj["sha"])
    except (ValueError, KeyError, TypeError):
        raise PublishError("Invalid Discord progress state in repository") from None


def save_state(repo: str, token: str, state: dict, sha: str | None) -> None:
    contents = json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    request_body = {
        "message": "Record Discord animal progress dashboard message ID",
        "content": base64.b64encode(contents.encode("utf-8")).decode("ascii"),
        "branch": "main",
    }
    if sha:
        request_body["sha"] = sha
    send_json("PUT", state_url(repo), request_body, token=token)


def publish(report: dict, webhook: str, repo: str, github_token: str) -> tuple[str, str]:
    url, webhook_id = validate_webhook_url(webhook)
    if not github_token.strip():
        raise PublishError("GITHUB_TOKEN is required to persist the Discord message ID")
    payload = discord_payload(report)
    state, sha = get_state(repo, github_token)
    old_id = str(state.get("message_id") or "")
    if state.get("webhook_id") == webhook_id and re.fullmatch(r"\d{10,25}", old_id):
        edited = send_json(
            "PATCH", url + "/messages/" + old_id, payload, allow_missing=True,
        )
        if edited is not None:
            return "updated", old_id
        # Webhook message was deleted. Create a new one and repair stored state.
    created = send_json("POST", url + "?wait=true", payload)
    new_id = str((created or {}).get("id", ""))
    if not re.fullmatch(r"\d{10,25}", new_id):
        raise PublishError("Discord did not return a valid message ID")
    save_state(repo, github_token, {"webhook_id": webhook_id, "message_id": new_id}, sha)
    return "created", new_id


def main() -> None:
    # No secret means no Discord request. Never log the secret URL.
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not webhook:
        raise PublishError(
            "Missing DISCORD_WEBHOOK_URL. Set it in Settings > Secrets and variables > Actions."
        )
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise PublishError("Run this workflow on main only")
    report_path = Path("inno-animal-progress.json")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    mode, message_id = publish(
        report, webhook,
        os.environ.get("GITHUB_REPOSITORY", ""),
        os.environ.get("GITHUB_TOKEN", ""),
    )
    print(f"Discord animal progress message {mode}: ID={message_id}")
    print("No Minecraft server commands or file writes were performed.")


if __name__ == "__main__":
    try:
        main()
    except (PublishError, ValueError, OSError, json.JSONDecodeError) as exc:
        # Avoid Python tracebacks that could contain a webhook URL from urllib.
        print("ERROR: " + str(exc), file=sys.stderr)
        sys.exit(1)
