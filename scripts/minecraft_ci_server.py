"""Fail-fast diagnostics for local vanilla Minecraft CI server startup."""
from __future__ import annotations

import subprocess
import threading
import time
from pathlib import Path


def wait_for_server_ready(
    ready: threading.Event,
    proc: subprocess.Popen,
    output: list[str],
    work: Path,
    *,
    timeout: float = 180,
    label: str = "Minecraft server",
) -> None:
    """Wait for Minecraft's 'Done (' line, diagnose early exit or a slow startup.

    The log is captured even if startup fails before any test function executes.
    It makes CI failures actionable instead of hiding startup errors behind a
    generic AssertionError after 90 seconds.
    """
    deadline = time.monotonic() + timeout
    while not ready.is_set():
        returncode = proc.poll()
        if returncode is not None:
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        ready.wait(min(1.0, remaining))
    if ready.is_set():
        return

    if proc.poll() is not None:
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
    log_path = work / "console.log"
    log_path.write_text("".join(output), encoding="utf-8")
    tail = "".join(output[-100:]).strip()
    if not tail:
        tail = "(no output from Minecraft process)"
    message = (
        f"{label} failed to become ready within {timeout:g}s "
        f"(returncode={proc.poll()}). Full log: {log_path}\n"
        f"----- last 100 console lines -----\n{tail}\n"
        "----- end Minecraft log -----"
    )
    print(message, flush=True)
    raise RuntimeError(message)
