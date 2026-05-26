#!/usr/bin/env python3
"""
swf_gui.py — Launch the RED ONE MX mock camera server + Ruffle SWF GUI.

Starts both processes, streams combined tagged output, and highlights key
boot milestones.  Type button injection commands directly (they are forwarded
to the mock server).  Press Ctrl-C or use --timeout to stop both processes.

Milestone events detected:
  AUTH OK         OTP handshake → role=admin
  BOOT COMPLETE   SYNC_EVENT_2 done; GoSplash / GoCamera about to run
  GOREADY FIRED   GUI_STATE_2; panels.xml parsed, splash should clear
  FULLY READY     GUI_STATE_5; button injection will work

Usage:
    python3 firmware/tools/swf_gui.py [options]

    --log FILE       Combined log (default: firmware/tools/swf_gui.log)
    --ruffle PATH    Ruffle binary (default: libraries/ruffle)
    --swf PATH       SWF file
    --assets DIR     Assets dir used as Ruffle --base URL
    --mock-port N    XMLSocket port (default: 49152)
    --http-port N    HTTP asset server port (default: 8000)
    --timeout SEC    Stop after SEC seconds (agentic mode)
    --rust-log LVL   RUST_LOG for Ruffle: warn | info | debug (default: info)
    -v, --verbose    -v for mock + RUST_LOG=debug for Ruffle
    --sensor-orig    Original RED ONE sensor splash
    --set NAME=VAL   Override camera param (repeatable)
"""

import argparse
import asyncio
import datetime
import os
import signal
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent   # firmware/tools/
REPO_ROOT  = SCRIPT_DIR.parent.parent          # r1mx/

# ── Boot milestone detection ─────────────────────────────────────────────────
# (match_string, banner | None)
# None = log the line, no extra banner printed

MILESTONES: list[tuple[str, str | None]] = [
    ("role=admin",                       "AUTH OK — admin session"),
    ("role=user",                        "AUTH OK — user session"),
    ("role=UNKNOWN",                     "AUTH FAILED — wrong password"),
    ("SYNC_EVENT_2",                     "BOOT COMPLETE — GoSplash / GoCamera about to run"),
    ("GUI_STATE_2_ACTIVATE_CALLBACKS",   "GOREADY FIRED — panels.xml parsed, splash clearing"),
    ("GUI_STATE_3_INITIALIZE_GUI_STATE", "INIT GUI STATE"),
    ("GUI_STATE_5_READY",                "FULLY READY — button injection enabled"),
    ("panels.xml",                       None),
    ("no subscribed clients",            None),
]


def _ts() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]


def _emit(text: str, log):
    print(text, flush=True)
    if log:
        print(text, file=log, flush=True)


def _banner(msg: str, log):
    bar = "=" * 66
    _emit(f"\n{bar}", log)
    _emit(f"  >>> {msg}", log)
    _emit(f"{bar}\n", log)


async def _stream(reader: asyncio.StreamReader, tag: str, log, reached: set):
    """Read lines from a subprocess stream, tag, log, and detect milestones."""
    while True:
        try:
            raw = await reader.readline()
        except Exception:
            break
        if not raw:
            break
        line = raw.decode("utf-8", errors="replace").rstrip()
        if not line:
            continue
        if tag != "RUFFLE":
            _emit(f"[{_ts()}][{tag}] {line}", log)
        for pat, banner in MILESTONES:
            if pat in line:
                reached.add(pat)
                if banner:
                    _banner(banner, log)
                break


async def _wait_ready(stream: asyncio.StreamReader, tag: str, log) -> bool:
    """Drain startup output until 'Listening on'; return True on success."""
    while True:
        raw = await stream.readline()
        if not raw:
            return False
        line = raw.decode().rstrip()
        _emit(f"[{_ts()}][{tag}] {line}", log)
        if "Listening on" in line:
            return True


async def run(args) -> int:
    assets_dir = Path(args.assets).resolve()
    swf_path   = Path(args.swf).resolve()
    log_path   = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Use HTTP base so XML.load("panels.xml") fetches via HTTP (Ruffle's XML.load
    # silently fails with file:// URLs when the SWF itself is also loaded from file://)
    base_url = f"http://127.0.0.1:{args.http_port}/"

    mock_script = SCRIPT_DIR / "mock_camera_server.py"

    mock_cmd = [
        sys.executable, str(mock_script),
        "--port",       str(args.mock_port),
        "--http-port",  str(args.http_port),
        "--assets-dir", str(assets_dir),
    ]
    if args.verbose:
        mock_cmd.append("-v")
    if args.sensor_orig:
        mock_cmd.append("--sensor-orig")
    for kv in (args.set or []):
        mock_cmd += ["--set", kv]

    # Load SWF via HTTP too so XML.load() relative URLs resolve from the same origin.
    # (Ruffle silently blocks file:// → http:// cross-scheme requests.)
    swf_name = swf_path.name
    swf_url  = f"http://127.0.0.1:{args.http_port}/{swf_name}"
    ruffle_cmd = [
        str(Path(args.ruffle)),
        swf_url,
        "--base",                   base_url,
        "--filesystem-access-mode", "allow",
        "--tcp-connections",        "allow",
    ]

    rust_log  = "debug" if args.verbose else args.rust_log
    ruffle_env = {**os.environ, "RUST_LOG": rust_log}

    with log_path.open("w", encoding="utf-8") as log:
        header = "\n".join([
            f"swf_gui  {datetime.datetime.now().isoformat()}",
            f"Mock:     {' '.join(mock_cmd)}",
            f"Ruffle:   {' '.join(ruffle_cmd)}",
            f"Base URL: {base_url}",
            f"RUST_LOG: {rust_log}",
            "─" * 66,
        ])
        for ln in header.splitlines():
            _emit(ln, log)

        # ── Mock server ──────────────────────────────────────────────────────
        # stdin=None: inherit terminal so the user can type button commands
        # (mock_camera_server.py reads stdin for injection via stdin_injector)
        mock_proc = await asyncio.create_subprocess_exec(
            *mock_cmd,
            stdin=None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(REPO_ROOT),
        )
        _emit(f"[{_ts()}][swf_gui] Waiting for mock server (PID {mock_proc.pid})...", log)

        if not await _wait_ready(mock_proc.stdout, "MOCK  ", log):
            _emit("ERROR: mock server failed to start", log)
            mock_proc.terminate()
            return 1

        # ── Ruffle ───────────────────────────────────────────────────────────
        ruffle_proc = await asyncio.create_subprocess_exec(
            *ruffle_cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=ruffle_env,
            cwd=str(REPO_ROOT),
        )
        _emit(
            f"[{_ts()}][swf_gui] Ruffle PID={ruffle_proc.pid} — "
            f"enter IP 127.0.0.1, click Camera\n"
            f"[{_ts()}][swf_gui] Button commands go to the mock server stdin (type here)",
            log,
        )

        reached: set[str] = set()
        stream_tasks = [
            asyncio.create_task(_stream(mock_proc.stdout,   "MOCK  ", log, reached)),
            asyncio.create_task(_stream(ruffle_proc.stdout, "RUFFLE", log, reached)),
            asyncio.create_task(_stream(ruffle_proc.stderr, "RUFFLE", log, reached)),
        ]

        stop = asyncio.Event()
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop.set)

        # Also trigger stop when Ruffle exits on its own
        async def _watch_ruffle():
            await ruffle_proc.wait()
            _emit(f"[{_ts()}][swf_gui] Ruffle exited (rc={ruffle_proc.returncode})", log)
            stop.set()

        watch_task = asyncio.create_task(_watch_ruffle())

        try:
            if args.timeout:
                try:
                    await asyncio.wait_for(stop.wait(), timeout=args.timeout)
                except asyncio.TimeoutError:
                    _emit(f"[{_ts()}][swf_gui] --timeout {args.timeout}s elapsed", log)
            else:
                await stop.wait()
        finally:
            watch_task.cancel()
            for t in stream_tasks:
                t.cancel()

            for proc, name in ((ruffle_proc, "Ruffle"), (mock_proc, "mock")):
                try:
                    proc.terminate()
                    await asyncio.wait_for(proc.wait(), timeout=3.0)
                    _emit(f"[{_ts()}][swf_gui] {name} stopped", log)
                except (ProcessLookupError, asyncio.TimeoutError):
                    try:
                        proc.kill()
                    except ProcessLookupError:
                        pass

            # ── Session summary ───────────────────────────────────────────────
            _emit(f"\n[{_ts()}][swf_gui] ── Session summary ──", log)
            all_ok = True
            for pat, banner in MILESTONES:
                if banner and pat not in ("panels.xml", "no subscribed clients"):
                    mark = "✓" if pat in reached else "✗"
                    if pat not in reached:
                        all_ok = False
                    _emit(f"  {mark} {banner}", log)
            if all_ok:
                _emit("  All milestones reached!", log)
            _emit(f"\n[{_ts()}][swf_gui] Log: {log_path}", log)

    return 0


def parse_args():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--ruffle",     default="libraries/ruffle")
    ap.add_argument("--swf",        default="firmware/reverse/build_32/assets/swf_gui_1.swf")
    ap.add_argument("--assets",     default="firmware/reverse/build_32/assets")
    ap.add_argument("--log",        default=str(SCRIPT_DIR / "swf_gui.log"))
    ap.add_argument("--mock-port",  type=int, default=49152, metavar="N")
    ap.add_argument("--http-port",  type=int, default=8000,  metavar="N")
    ap.add_argument("--timeout",    type=int, default=None,  metavar="SEC",
                    help="Stop after N seconds (for agentic / automated runs)")
    ap.add_argument("--rust-log",   default="info", metavar="LEVEL",
                    help="RUST_LOG for Ruffle: warn | info | debug  (default: info)")
    ap.add_argument("-v", "--verbose",  action="store_true",
                    help="-v for mock server + RUST_LOG=debug for Ruffle")
    ap.add_argument("--sensor-orig",    action="store_true")
    ap.add_argument("--set", action="append", metavar="NAME=VALUE",
                    help="Override camera param (repeatable)")
    return ap.parse_args()


if __name__ == "__main__":
    sys.exit(asyncio.run(run(parse_args())))
