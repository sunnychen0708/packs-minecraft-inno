#!/usr/bin/env python3
"""Generic Minecraft Java datapack validation.

Examples:
  python3 scripts/validate-datapack.py copy-paste
  python3 scripts/validate-datapack.py warehouse
  python3 scripts/validate-datapack.py copy-paste --java /path/to/java --server-jar /path/to/server.jar --accept-eula

Static validation is always performed. The optional server smoke test boots an
isolated vanilla server and checks datapack loading/reload logs. Pack-specific
behavior should live in scripts/test-<pack>.py.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
import threading
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATAPACKS = ROOT / "datapacks"

NAMESPACE_RE = re.compile(r"^[a-z0-9_.-]+$")
PATH_RE = re.compile(r"^[a-z0-9_./-]+$")
FUNCTION_TOKEN_RE = re.compile(r"\bfunction\s+([^\s{]+)")
SCHEDULE_TOKEN_RE = re.compile(r"\bschedule\s+function\s+([^\s{]+)")
TRIGGER_ADD_RE = re.compile(r"\bscoreboard\s+objectives\s+add\s+([A-Za-z0-9_.+\-]+)\s+trigger\b")
MACRO_ARG_RE = re.compile(r"\$\(([A-Za-z0-9_.\-]+)\)")

ERROR_PATTERNS = (
    "failed to load function",
    "failed to parse",
    "couldn't parse command",
    "unknown function",
    "failed to load datapacks",
    "errors in currently selected datapacks",
    "couldn't load tag",
    "invalid macro",
    "whilst instantiating",
    "missing argument",
)


class ValidationError(Exception):
    pass


def normalize_format(value):
    if isinstance(value, int):
        return (value, 0)
    if isinstance(value, list) and 1 <= len(value) <= 2 and all(isinstance(x, int) for x in value):
        return (value[0], value[1] if len(value) == 2 else 0)
    raise ValidationError(f"Unsupported pack format value: {value!r}")


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ValidationError(f"Invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc


def function_id(path: Path, data_root: Path) -> str:
    rel = path.relative_to(data_root)
    namespace = rel.parts[0]
    if len(rel.parts) < 3 or rel.parts[1] != "function":
        raise ValidationError(f"Unexpected function path: {path.relative_to(ROOT)}")
    function_path = "/".join(rel.parts[2:]).removesuffix(".mcfunction")
    return f"{namespace}:{function_path}"


def tag_id(path: Path, data_root: Path) -> str:
    rel = path.relative_to(data_root)
    namespace = rel.parts[0]
    tag_path = "/".join(rel.parts[3:]).removesuffix(".json")
    return f"{namespace}:{tag_path}"


def check_pack_metadata(pack: Path):
    meta_path = pack / "pack.mcmeta"
    if not meta_path.is_file():
        raise ValidationError(f"Missing {meta_path.relative_to(ROOT)}")
    meta = read_json(meta_path)
    pack_obj = meta.get("pack")
    if not isinstance(pack_obj, dict):
        raise ValidationError("pack.mcmeta is missing the 'pack' object")
    if "description" not in pack_obj:
        raise ValidationError("pack.mcmeta is missing pack.description")

    if "min_format" in pack_obj or "max_format" in pack_obj:
        if "min_format" not in pack_obj or "max_format" not in pack_obj:
            raise ValidationError("pack.mcmeta must provide both min_format and max_format")
        minimum = normalize_format(pack_obj["min_format"])
        maximum = normalize_format(pack_obj["max_format"])
        if minimum > maximum:
            raise ValidationError(f"min_format {minimum} is greater than max_format {maximum}")
        return minimum, maximum

    if "pack_format" in pack_obj:
        value = normalize_format(pack_obj["pack_format"])
        return value, value

    raise ValidationError("pack.mcmeta has no min_format/max_format or pack_format")


def collect_functions(data_root: Path):
    functions = {}
    for path in data_root.glob("*/function/**/*.mcfunction"):
        fid = function_id(path, data_root)
        namespace, fpath = fid.split(":", 1)
        if not NAMESPACE_RE.fullmatch(namespace) or not PATH_RE.fullmatch(fpath):
            raise ValidationError(f"Invalid function id {fid}")
        if fid in functions:
            raise ValidationError(f"Duplicate function id {fid}")
        functions[fid] = path
    return functions


def collect_function_tags(data_root: Path):
    tags = {}
    for path in data_root.glob("*/tags/function/**/*.json"):
        tid = tag_id(path, data_root)
        tags[tid] = path
    return tags


def resolve_tag_values(data_root: Path, functions: dict[str, Path], tags: dict[str, Path]):
    for tid, path in tags.items():
        obj = read_json(path)
        values = obj.get("values")
        if not isinstance(values, list):
            raise ValidationError(f"Function tag {tid} is missing a values array")
        for entry in values:
            if isinstance(entry, str):
                value = entry
            elif isinstance(entry, dict) and isinstance(entry.get("id"), str):
                value = entry["id"]
            else:
                raise ValidationError(f"Invalid entry in function tag {tid}: {entry!r}")

            if value.startswith("#"):
                target = value[1:]
                if target not in tags:
                    raise ValidationError(f"Function tag {tid} references missing tag #{target}")
            elif value not in functions:
                raise ValidationError(f"Function tag {tid} references missing function {value}")


def static_function_tokens(line: str):
    """Return literal function ids, skipping tags and macro-generated paths."""
    tokens = list(FUNCTION_TOKEN_RE.findall(line)) + list(SCHEDULE_TOKEN_RE.findall(line))
    for token in tokens:
        token = token.rstrip(",")
        if token.startswith("#") or "$(" in token:
            continue
        if ":" in token:
            yield token


def repo_function_exists(fid: str) -> bool:
    """Allow intentional cross-pack calls when the target function exists elsewhere in this repo."""
    namespace, fpath = fid.split(":", 1)
    rel = Path("data") / namespace / "function" / (fpath + ".mcfunction")
    return any((pack / rel).is_file() for pack in DATAPACKS.iterdir() if pack.is_dir())


def check_function_references(functions: dict[str, Path]):
    missing = []
    direct_macro_calls = []
    empty_macro_lines = []
    macro_functions = {}

    for fid, path in functions.items():
        text = path.read_text(encoding="utf-8")
        placeholders = set()
        for line_no, line in enumerate(text.splitlines(), 1):
            if line.startswith("$"):
                args = MACRO_ARG_RE.findall(line)
                if not args:
                    empty_macro_lines.append((fid, line_no))
                placeholders.update(args)
        if placeholders:
            macro_functions[fid] = placeholders

    for source_id, path in functions.items():
        text = path.read_text(encoding="utf-8")
        refs = set()
        for line in text.splitlines():
            refs.update(static_function_tokens(line))
        for ref in sorted(refs):
            if ref not in functions and not repo_function_exists(ref):
                missing.append((source_id, ref))

        for line_no, line in enumerate(text.splitlines(), 1):
            for ref in static_function_tokens(line):
                if ref in macro_functions:
                    tail = line.split(f"function {ref}", 1)[1].strip()
                    if not (tail.startswith("with ") or tail.startswith("{")):
                        direct_macro_calls.append((source_id, line_no, ref))

    if missing:
        details = ", ".join(f"{src} -> {ref}" for src, ref in missing[:20])
        raise ValidationError(f"Missing function references: {details}")

    if direct_macro_calls:
        details = ", ".join(f"{src}:{line} -> {ref}" for src, line, ref in direct_macro_calls[:20])
        raise ValidationError(f"Macro functions called without arguments: {details}")

    if empty_macro_lines:
        details = ", ".join(f"{src}:{line}" for src, line in empty_macro_lines[:20])
        raise ValidationError(f"Macro lines without variables: {details}")

    return macro_functions


def check_triggers(functions: dict[str, Path]):
    texts = {fid: path.read_text(encoding="utf-8") for fid, path in functions.items()}
    all_text = "\n".join(texts.values())
    triggers = sorted(set(TRIGGER_ADD_RE.findall(all_text)))
    warnings = []

    for objective in triggers:
        enable_re = re.compile(rf"\bscoreboard\s+players\s+enable\s+\S+\s+{re.escape(objective)}\b")
        set_zero_re = re.compile(rf"\bscoreboard\s+players\s+set\s+\S+\s+{re.escape(objective)}\s+0\b")
        reset_re = re.compile(rf"\bscoreboard\s+players\s+reset\s+\S+(?:\s+{re.escape(objective)})?\b")
        if not enable_re.search(all_text):
            warnings.append(f"trigger {objective!r} is never obviously enabled; enforce user-facing trigger lifecycle in the pack-specific test")
        if not (set_zero_re.search(all_text) or reset_re.search(all_text)):
            warnings.append(f"trigger {objective!r} has no obvious reset-to-zero/reset command; enforce this in the pack-specific test if required")

    return triggers, warnings


def check_all_json(pack: Path):
    count = 0
    for path in pack.rglob("*.json"):
        read_json(path)
        count += 1
    return count


def check_archive(pack: Path):
    with tempfile.TemporaryDirectory(prefix="datapack-validate-") as tmp:
        archive_path = Path(tmp) / f"{pack.name}.zip"
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(pack.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(pack).as_posix())

        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            if "pack.mcmeta" not in names:
                raise ValidationError("Built ZIP does not contain pack.mcmeta at archive root")
            if not any(name.startswith("data/") for name in names):
                raise ValidationError("Built ZIP does not contain data/ at archive root")
            bad = archive.testzip()
            if bad:
                raise ValidationError(f"ZIP CRC check failed for {bad}")
            top = {name.split("/", 1)[0] for name in names}
            if pack.name in top:
                raise ValidationError("ZIP contains an extra parent pack directory")

        return len(names)


def static_validation(pack: Path):
    if not pack.is_dir():
        raise ValidationError(f"Datapack not found: {pack}")

    data_root = pack / "data"
    if not data_root.is_dir():
        raise ValidationError(f"Missing data/ directory in {pack.name}")

    minimum, maximum = check_pack_metadata(pack)
    json_count = check_all_json(pack)
    functions = collect_functions(data_root)
    if not functions:
        raise ValidationError(f"No functions found in {pack.name}")
    tags = collect_function_tags(data_root)
    resolve_tag_values(data_root, functions, tags)
    macro_functions = check_function_references(functions)
    triggers, warnings = check_triggers(functions)
    zip_entries = check_archive(pack)

    print(
        f"PASS static {pack.name}: format {minimum[0]}.{minimum[1]}..{maximum[0]}.{maximum[1]}, "
        f"{json_count} JSON, {len(functions)} functions, {len(tags)} function tags, "
        f"{len(macro_functions)} macro functions, {len(triggers)} triggers, {zip_entries} ZIP entries",
        flush=True,
    )
    for warning in warnings:
        print(f"WARN {pack.name}: {warning}", flush=True)

    return {
        "minimum": minimum,
        "maximum": maximum,
        "functions": functions,
        "macros": macro_functions,
        "triggers": triggers,
    }


def server_smoke(pack: Path, java: Path, server_jar: Path):
    evidence_root = ROOT / "dist" / "validation"
    evidence_root.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    evidence = evidence_root / f"{pack.name}-{stamp}"
    evidence.mkdir()

    world_datapacks = evidence / "world" / "datapacks"
    world_datapacks.mkdir(parents=True)
    archive_path = world_datapacks / f"{pack.name}.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(pack.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(pack).as_posix())

    (evidence / "eula.txt").write_text("eula=true\n", encoding="utf-8")
    (evidence / "server.properties").write_text(
        "\n".join(
            [
                "server-ip=127.0.0.1",
                "server-port=0",
                "online-mode=false",
                "white-list=true",
                "view-distance=2",
                "simulation-distance=2",
                "level-type=minecraft:flat",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    output: list[str] = []
    ready = threading.Event()
    proc = subprocess.Popen(
        [str(java), "-Xms256M", "-Xmx1024M", "-jar", str(server_jar), "--nogui"],
        cwd=evidence,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    def reader():
        assert proc.stdout is not None
        for line in proc.stdout:
            output.append(line)
            if "Done (" in line:
                ready.set()

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()

    try:
        if not ready.wait(90):
            raise ValidationError("Vanilla server did not become ready within 90 seconds")
        assert proc.stdin is not None
        proc.stdin.write("reload\n")
        proc.stdin.flush()
        time.sleep(8)
        proc.stdin.write("datapack list enabled\n")
        proc.stdin.flush()
        time.sleep(3)
    finally:
        if proc.poll() is None:
            assert proc.stdin is not None
            proc.stdin.write("stop\n")
            proc.stdin.flush()
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.terminate()
        thread.join(timeout=5)

    report = "".join(output)
    (evidence / "console.log").write_text(report, encoding="utf-8")
    errors = [line.strip() for line in output if any(pattern in line.lower() for pattern in ERROR_PATTERNS)]
    if errors:
        raise ValidationError("Vanilla server reported datapack/parser errors:\n" + "\n".join(errors[:30]))

    print(f"PASS vanilla smoke {pack.name}: server boot + reload, evidence: {evidence}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", help="Directory name under datapacks/")
    parser.add_argument("--java", type=Path, help="Java executable for optional vanilla server smoke test")
    parser.add_argument("--server-jar", type=Path, help="Official Minecraft server JAR for optional smoke test")
    parser.add_argument("--accept-eula", action="store_true", help="Required before starting the server smoke test")
    args = parser.parse_args()

    pack = DATAPACKS / args.pack
    static_validation(pack)

    if args.java or args.server_jar:
        if not (args.java and args.server_jar and args.accept_eula):
            raise SystemExit("For runtime smoke testing, provide --java, --server-jar, and --accept-eula together.")
        server_smoke(pack, args.java.resolve(), args.server_jar.resolve())


if __name__ == "__main__":
    try:
        main()
    except ValidationError as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
