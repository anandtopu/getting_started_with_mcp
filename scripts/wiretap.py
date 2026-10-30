"""Proxy stdio without changing bytes; write redacted diagnostics to stderr.

Run: uv run python scripts/wiretap.py --capture .runtime/wire.jsonl -- python server.py
Concept: MCP stdio framing (specification/2026-07-28/basic/transports/stdio).
Expected: protocol on stdout; client->server/server->client timing on stderr.
"""

import argparse
import importlib.metadata
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from common.pretty import redact


def proxy(command: list[str], capture: Path | None = None, timeout: float | None = None) -> int:
    start = time.monotonic()
    lock = threading.Lock()
    secrets = tuple(
        v
        for k, v in os.environ.items()
        if any(word in k.upper() for word in ("TOKEN", "SECRET", "PASSWORD", "API_KEY"))
    )
    if capture:
        capture.parent.mkdir(parents=True, exist_ok=True)
    log = capture.open("w", encoding="utf-8", newline="\n") if capture else None

    def record(direction: str, payload: bytes) -> None:
        try:
            message = json.loads(payload)
        except (ValueError, UnicodeDecodeError):
            message = {"non_json_bytes": len(payload)}
        event = {
            "direction": direction,
            "elapsed_ms": round((time.monotonic() - start) * 1000, 3),
            "message": redact(message, secrets),
        }
        with lock:
            print(json.dumps(event, ensure_ascii=True), file=sys.stderr, flush=True)
            if log:
                log.write(json.dumps(event, ensure_ascii=True) + "\n")
                log.flush()

    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
    except OSError:
        if log:
            log.close()
        print("Cannot launch server. Run uv run python scripts/check_env.py.", file=sys.stderr)
        return 127

    def relay(source, target, direction: str) -> None:
        try:
            while payload := source.readline(1024 * 1024):
                # KEY IDEA: never decode/re-encode the protocol bytes being forwarded.
                remaining = memoryview(payload)
                while remaining:
                    written = target.write(remaining)
                    if not written:
                        raise BrokenPipeError("Protocol stream closed")
                    remaining = remaining[written:]
                target.flush()
                record(direction, payload)
        except (BrokenPipeError, OSError, ValueError):
            return
        finally:
            if direction == "client->server":
                try:
                    target.close()
                except OSError:
                    pass

    def diagnostics() -> None:
        for payload in iter(process.stderr.readline, b""):
            # Arbitrary child logs may contain secrets: sanitize before displaying.
            with lock:
                print(
                    redact(payload.decode("utf-8", errors="replace"), secrets),
                    end="",
                    file=sys.stderr,
                    flush=True,
                )

    if log:
        recorded_command = []
        for argument in command:
            if argument == sys.executable:
                recorded_command.append("python")
            elif Path(argument).is_absolute() and Path(argument).is_relative_to(Path.cwd()):
                recorded_command.append(Path(argument).relative_to(Path.cwd()).as_posix())
            else:
                recorded_command.append(argument)
        log.write(
            json.dumps(
                {
                    "capture_version": 1,
                    "command": redact(recorded_command, secrets),
                    "transport": "stdio",
                    "python": sys.version.split()[0],
                    "mcp": importlib.metadata.version("mcp"),
                }
            )
            + "\n"
        )
    incoming = threading.Thread(
        target=relay, args=(sys.stdin.buffer, process.stdin, "client->server"), daemon=True
    )
    outgoing = threading.Thread(
        target=relay, args=(process.stdout, sys.stdout.buffer, "server->client"), daemon=True
    )
    errors = threading.Thread(target=diagnostics, daemon=True)
    for thread in (incoming, outgoing, errors):
        thread.start()
    try:
        code = process.wait(timeout=timeout)
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        code = 124
    outgoing.join(timeout=3)
    errors.join(timeout=3)
    with lock:
        if log:
            log.close()
            log = None
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("Supply a server command after --")
    if args.timeout is not None and args.timeout <= 0:
        parser.error("--timeout must be positive")
    return proxy(command, args.capture, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
