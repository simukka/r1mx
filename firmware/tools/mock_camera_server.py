#!/usr/bin/env python3
"""
Mock RED ONE MX camera XML socket server (port 49152).

Speaks Flash XMLSocket protocol: null-terminated UTF-8 XML strings.
Implements the GPDB boot handshake so swf_gui_1.swf can run outside the camera.

Usage:
    python3 firmware/tools/mock_camera_server.py [options]

    --factory-defaults PATH   factory_defaults.xml (default: firmware/tools/factory_defaults.xml)
    --port PORT               TCP port (default: 49152)
    --assets-dir DIR          Directory served via HTTP for panels.xml (default: firmware/reverse/build_32/assets)
    --http-port PORT          HTTP port for asset server (default: 8000)
    --sensor-mx               Set SENSOR.REVISION_NUMBER=1 (MX splash, default)
    --sensor-orig             Set SENSOR.REVISION_NUMBER=0 (original RED ONE splash)
    --version STR             SYSTEM.VERSION.RED_RELEASE (default: 32.0.3#1)
    --serial STR              SYSTEM.MANUFACTURING.CAMERA_SERIAL_NUMBER
    --set NAME=VALUE          Override any param value (repeatable)
    -v, --verbose             Log all messages

The server also starts an HTTP server (default port 8000) so the SWF's
OsdXml.load("panels.xml") resolves to http://127.0.0.1:8000/panels.xml
instead of a file:// URL that Ruffle doesn't handle reliably.

Load the SWF via the printed HTTP URL — e.g.:
    libraries/ruffle 'http://127.0.0.1:8000/swf_gui_1.swf' --base 'http://127.0.0.1:8000/' --tcp-connections allow

The --base flag is required: without it Ruffle resolves relative URLs (like panels.xml)
against the working directory instead of the HTTP server.

The SWF shows RemoteConnectMC → enter IP 127.0.0.1 → click Camera.

Button injection (type in the mock's terminal while the SWF is connected):
    record      GUI.RAWINPUT.BUTTON.RECORD
    menu        GUI.RAWINPUT.BUTTON.MENU.SYSTEM
    sensor      GUI.RAWINPUT.BUTTON.MENU.SENSOR
    video       GUI.RAWINPUT.BUTTON.MENU.VIDEO
    sw1..sw4    SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW1..SW4
    user_a/b/c  GUI.RAWINPUT.BUTTON.USER_DEFINED.A/B/C
    dev         GUI.RAWINPUT.BUTTON.COMBOKEY.USER_H  (Developer panel)
    exit        GUI.RAWINPUT.BUTTON.COMBOKEY.EXIT
    set NAME=VALUE   push an arbitrary <Param> to all subscribed clients
    help        show this list
"""

import argparse
import asyncio
import functools
import http.server
import re
import sys
import threading
import xml.etree.ElementTree as ET
from pathlib import Path

# ── OTP key extracted from Authenticate.as ──────────────────────────────────
OTP_KEY = [
    187,80,170,228,27,81,20,193,15,239,143,166,69,163,96,191,104,80,187,206,
    176,174,2,148,155,179,105,51,121,28,77,19,95,99,38,195,92,126,146,140,
    189,55,235,64,1,181,10,112,76,213,14,45,171,156,59,106,229,48,237,113,
    211,53,169,137,34,190,188,92,218,87,38,230,68,202,65,225,222,96,58,162,
    16,222,7,173,185,40,80,96,238,37,8,43,72,35,39,9,154,164,142,203,223,38,
    212,245,35,184,112,71,107,123,247,236,209,107,28,52,79,191,15,239,116,
    181,172,202,89,44,177,92,26,137,253,144,21,166,45,16,202,6,3,98,106,7,
    123,87,223,155,22,17,132,173,179,24,34,30,155,252,141,15,201,202,195,253,
    92,141,163,236,214,149,223,25,54,106,9,223,36,9,13,68,83,48,220,144,201,
    201,110,174,192,203,74,129,229,88,27,242,80,15,93,178,53,176,140,112,88,
    159,114,187,109,32,237,225,179,193,226,126,85,5,231,159,88,111,83,72,46,
    228,32,59,216,173,27,31,35,221,209,1,12,43,57,116,213,55,61,99,124,12,
    217,110,142,75,108,239,250,108,170,35,5,9,127,2,230,119,120,30,201,129,
    140,155,66,233,248,243,225,94,122,202,59,215,46,166,150,36,248,179,93,
    251,243,200,115,61,58,197,160,97,215,35,0,230,40,21,188,74,155,143,78,
    229,220,57,39,209,73,96,44,113,94,2,16,82,49,205,91,166,234,233,174,140,
    159,11,100,128,227,110,217,13,167,214,233,140,242,17,246,110,235,84,232,
    34,162,209,235,122,20,119,130,171,17,39,11,255,206,173,211,140,186,73,76,
    112,145,37,221,196,249,179,248,81,151,65,108,198,187,41,0,176,24,139,202,
    107,225,242,176,21,5,114,186,151,47,97,29,194,217,127,118,244,140,149,
    199,91,89,166,215,87,3,164,151,115,93,220,99,222,80,161,96,192,37,239,
    160,41,150,187,23,80,108,185,227,17,92,82,16,178,160,210,56,73,40,201,
    144,4,209,137,163,126,108,174,135,159,91,161,130,192,88,37,72,12,211,128,
    193,192,124,237,3,41,10,118,194,55,57,153,166,176,23,32,76,127,148,45,27,
    24,91,85,220,14,240,37,235,171,219,137,149,153,5,67,171,228,121,152,132,
    248,59,111,8,163,18,158,150,47,62,131,8,139,144,254,136,202,73,240,143,
    209,158,192,121,223,59,12,155,147,68,247,5,160,97,107,58,220,189,237,58,
    29,249,255,95,115,149,63,20,170,152,84,196,149,195,92,56,184,159,97,27,
    60,122,8,132,6,171,252,216,156,103,186,165,187,69,202,2,236,149,135,141,
    29,8,134,235,202,247,206,173,27,33,156,2,103,233,195,251,31,218,51,230,
    181,38,130,100,185,173,56,243,209,136,100,65,130,200,87,190,69,123,164,
    156,156,75,57,181,104,199,113,130,214,164,115,123,210,220,148,167,97,67,
    235,212,73,199,154,20,184,163,246,72,229,69,102,117,60,178,253,112,38,
    148,84,73,106,241,168,162,157,250,34,249,120,153,97,134,250,227,26,100,
    182,223,214,166,69,67,228,168,242,65,163,105,122,109,184,44,0,131,126,
    158,113,130,50,83,236,243,99,105,243,240,85,203,21,93,10,130,175,246,2,
    155,203,100,253,234,11,180,172,176,184,132,25,136,198,233,177,152,122,17,
    173,93,96,121,106,83,1,128,73,59,122,227,202,30,56,253,68,228,158,53,37,
    57,151,249,121,101,183,138,43,79,251,26,166,211,65,232,85,238,17,110,97,
    245,243,13,137,29,2,5,214,14,163,101,123,155,186,147,57,16,150,1,163,161,
    69,42,128,212,61,191,137,40,60,7,98,249,15,94,132,50,174,172,110,162,138,
    228,30,121,76,202,32,148,217,94,242,31,134,137,22,205,122,117,244,41,51,
    12,44,77,149,200,135,185,214,182,98,117,94,117,46,255,204,65,176,110,223,
    244,250,87,138,174,181,184,110,129,210,55,136,243,129,67,80,173,232,60,
    111,111,25,196,216,7,29,76,208,50,170,5,76,62,78,87,98,116,215,235,208,
    41,128,112,229,168,12,90,66,18,156,46,63,187,181,134,88,65,79,142,101,
    178,61,101,132,52,52,21,150,232,130,244,143,248,14,226,180,116,167,237,
    228,192,69,12,135,255,153,79,147,186,84,77,252,249,219,19,40,20,216,92,
    85,177,30,74,219,108,101,194,175,230,36,83,11,119,26,190,66,8,218,90,55,
    232,28,228,126,45,90,189,137,87,35,180,42,60,172,231,31,76,130,139,49,61,
    137,96,15,144,59,61,111,196,243,240,219,2,111,75,218,192,20,198,105,158,
    1,251,152,
]

ADMIN_MD5 = "1b772ea5a3dc1e140c4240b335b1d8b8"
USER_MD5  = "c73f8496a6dc61cee28acf80851e004a"

# ── Hardware-only params not in factory_defaults.xml ────────────────────────
# GoCamera managers (LcdManager, GpioManager, MediaManager, FormatManager,
# ProfileMgr) call addCallback/paramGet on these at constructor time.  Without
# them GPDB.getParam() throws and GoCamera aborts before MenuManager.LoadPanels().
# Keyed by param name → (type, default_value).
HARDWARE_STUB_PARAMS: dict[str, tuple[str, str]] = {
    # LcdManager — LCD button events + brightness
    "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW2":      ("boolean", "false"),
    "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW3":      ("boolean", "false"),
    "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW4":      ("boolean", "false"),
    "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW4_LONG": ("boolean", "false"),
    "SYSTEM.DEV.LCD.BRIGHTNESS":               ("number",  "80"),
    # GpioManager — GPIO inputs/outputs; FlagRecordActive reads TRIGGER at ctor time
    "SYSTEM.DEV.GPIO.SETTING.INPUT_1":             ("string", ""),
    "SYSTEM.DEV.GPIO.SETTING.INPUT_2":             ("string", ""),
    "SYSTEM.DEV.GPIO.CONFIG.INPUT_1.POLARITY":     ("string", ""),
    "SYSTEM.DEV.GPIO.CONFIG.INPUT_2.POLARITY":     ("string", ""),
    "SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.POLARITY":    ("string", ""),
    "SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.POLARITY":    ("string", ""),
    "SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.TRIGGER":     ("string", ""),
    "SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.TRIGGER":     ("string", ""),
    "VIDEO.PLAYBACK.REQUESTED":                    ("boolean", "false"),
    "GUI.PAINT.WHITE_BALANCE.AUTO":                ("boolean", "false"),
    "VIDEO.RECORD.ACK":                            ("boolean", "false"),
    # MediaManager — DIGMAG magazine events
    "MEDIA.DIGMAG.DRIVE0.EJECT_DONE":  ("boolean", "false"),
    "MEDIA.DIGMAG.DRIVE1.EJECT_DONE":  ("boolean", "false"),
    "MEDIA.DIGMAG.MEDIA_PATH":         ("string",  ""),
    "MEDIA.DIGMAG.CLIP_LIST":          ("string",  ""),
    # FormatManager — DIGMAG format completion events
    "MEDIA.DIGMAG.DRIVE0.FORMAT_DONE": ("boolean", "false"),
    "MEDIA.DIGMAG.DRIVE1.FORMAT_DONE": ("boolean", "false"),
    # ProfileMgr — profile import/export/restore status
    "SYSTEM.PROFILE.IMPORT.STATUS":    ("string",  ""),
    "SYSTEM.PROFILE.EXPORT.STATUS":    ("string",  ""),
    "SYSTEM.PROFILE.RESTORE.REQUESTED": ("boolean", "false"),
    "SYSTEM.PROFILE.RESTORE.STATUS":   ("string",  ""),
    "GUI.PROFILE.IMPORT_PATHNAME.LOOK":    ("string", ""),
    "GUI.PROFILE.IMPORT_PATHNAME.USER":    ("string", ""),
    "GUI.PROFILE.IMPORT_PATHNAME.PROJECT": ("string", ""),
}

# ── Button shortname → GPDB param ───────────────────────────────────────────
# Values derived from ButtonManager.as and LcdManager.as callbacks.
BUTTON_MAP: dict[str, str] = {
    "record":   "GUI.RAWINPUT.BUTTON.RECORD",
    "rec":      "GUI.RAWINPUT.BUTTON.RECORD",
    "menu":     "GUI.RAWINPUT.BUTTON.MENU.SYSTEM",
    "sensor":   "GUI.RAWINPUT.BUTTON.MENU.SENSOR",
    "video":    "GUI.RAWINPUT.BUTTON.MENU.VIDEO",
    "sw1":      "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW1",
    "sw2":      "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW2",
    "sw3":      "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW3",
    "sw4":      "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW4",
    "user_a":   "GUI.RAWINPUT.BUTTON.USER_DEFINED.A",
    "user_b":   "GUI.RAWINPUT.BUTTON.USER_DEFINED.B",
    "user_c":   "GUI.RAWINPUT.BUTTON.USER_DEFINED.C",
    "side_rec": "GUI.RAWINPUT.BUTTON.SIDE.RECORD",
    "dev":      "GUI.RAWINPUT.BUTTON.COMBOKEY.USER_H",
    "exit":     "GUI.RAWINPUT.BUTTON.COMBOKEY.EXIT",
    "back":     "GUI.RAWINPUT.BUTTON.COMBOKEY.SYSTEM",
    "pre_rec":  "GUI.RAWINPUT.BUTTON.COMBOKEY.RECORD",
}

BUTTON_HELP = """\
Button shortcuts:
  record / rec    GUI.RAWINPUT.BUTTON.RECORD
  menu            GUI.RAWINPUT.BUTTON.MENU.SYSTEM
  sensor          GUI.RAWINPUT.BUTTON.MENU.SENSOR
  video           GUI.RAWINPUT.BUTTON.MENU.VIDEO
  sw1 .. sw4      SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW1..SW4
  user_a/b/c      GUI.RAWINPUT.BUTTON.USER_DEFINED.A/B/C
  side_rec        GUI.RAWINPUT.BUTTON.SIDE.RECORD
  dev             GUI.RAWINPUT.BUTTON.COMBOKEY.USER_H  (Developer panel)
  exit            GUI.RAWINPUT.BUTTON.COMBOKEY.EXIT
  back            GUI.RAWINPUT.BUTTON.COMBOKEY.SYSTEM
  pre_rec         GUI.RAWINPUT.BUTTON.COMBOKEY.RECORD
  set NAME=VALUE  push arbitrary <Param> to all subscribed clients
  help            show this list"""


# ── OTP helpers ─────────────────────────────────────────────────────────────

def otp_encrypt(plaintext: str, offset: int) -> str:
    """XOR-encrypt a string with the OTP key starting at offset, return hex string."""
    key_len = len(OTP_KEY)
    result = []
    for i, ch in enumerate(plaintext):
        byte = ord(ch) ^ OTP_KEY[(offset + i) % key_len]
        result.append(f"{byte:02x}")
    return "".join(result)


def otp_decrypt(hexstr: str, offset: int) -> str:
    """Decrypt a hex-encoded OTP-encrypted string."""
    key_len = len(OTP_KEY)
    result = []
    for i in range(0, len(hexstr), 2):
        byte = int(hexstr[i:i+2], 16) ^ OTP_KEY[(offset + i // 2) % key_len]
        result.append(chr(byte))
    return "".join(result)


# ── XML helpers ──────────────────────────────────────────────────────────────

def xml_cmnd(name: str, arg: str) -> str:
    arg_escaped = arg.replace("&", "&amp;").replace('"', "&quot;")
    return f'<Cmnd name="{name}" arg="{arg_escaped}"/>'


def xml_sync(event_id: str) -> str:
    return f'<Sync id="{event_id}"/>'


def xml_param(name: str, ptype: str, value: str) -> str:
    value_escaped = str(value).replace("&", "&amp;").replace('"', "&quot;")
    return f'<Param name="{name}" type="{ptype}" value="{value_escaped}"/>'


# ── Parameter store ──────────────────────────────────────────────────────────

class ParamStore:
    def __init__(self, factory_xml_path: Path):
        self.defs: dict[str, dict] = {}   # name → {type, value, ...}
        self._load(factory_xml_path)
        # Add hardware-only stubs for params not covered by factory_defaults.xml.
        # Only fills gaps — factory_defaults.xml entries take precedence.
        for name, (ptype, value) in HARDWARE_STUB_PARAMS.items():
            if name not in self.defs:
                self.defs[name] = {"type": ptype, "value": value}

    def _load(self, path: Path):
        text = path.read_text(encoding="utf-8", errors="replace")
        # value is optional — some params (events/triggers) have no value attribute
        for m in re.finditer(
            r'<Param\s[^>]*name\s*=\s*"([^"]+)"[^>]*type\s*=\s*"([^"]+)"'
            r'(?:[^>]*value\s*=\s*"([^"]*)")?',
            text, re.DOTALL
        ):
            name, ptype = m.group(1), m.group(2)
            value = m.group(3) if m.group(3) is not None else ""
            self.defs[name] = {"type": ptype, "value": value}

    def set(self, name: str, value: str):
        if name in self.defs:
            self.defs[name]["value"] = value
        else:
            self.defs[name] = {"type": "string", "value": value}

    def get(self, name: str) -> str | None:
        return self.defs.get(name, {}).get("value")

    def registration_xml(self) -> str:
        """Full <RedParameters> block with type+value for registration (GuiBoot1)."""
        lines = ["<RedParameters>"]
        for name, info in self.defs.items():
            v = info["value"].replace("&", "&amp;").replace('"', "&quot;")
            lines.append(f'  <Param name="{name}" type="{info["type"]}" value="{v}"/>')
        lines.append("</RedParameters>")
        return "\n".join(lines)

    def values_xml(self) -> str:
        """<RedParameters> block with current values only (GuiBoot2 GET_PARAM *)."""
        lines = ["<RedParameters>"]
        for name, info in self.defs.items():
            v = info["value"].replace("&", "&amp;").replace('"', "&quot;")
            lines.append(f'  <Param name="{name}" type="{info["type"]}" value="{v}"/>')
        lines.append("</RedParameters>")
        return "\n".join(lines)


# ── Connection handler ───────────────────────────────────────────────────────

class CameraSession:
    def __init__(self, params: ParamStore, verbose: bool = False):
        self.params = params
        self.verbose = verbose
        self._auth_seed_str: str | None = None
        self._authenticated: bool = False
        self._subscribed: bool = False   # set True when ADD_TERM received
        self.push_queue: asyncio.Queue[str] = asyncio.Queue()

    def _log(self, direction: str, msg: str):
        tag = msg[:60].replace("\n", "↵")
        print(f"  [{direction}] {tag}", flush=True)

    def handle_message(self, raw: str) -> list[str]:
        """Parse one null-terminated XML message; return list of response strings."""
        raw = raw.strip()
        if not raw:
            return []
        if self.verbose:
            self._log("←", raw)
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            print(f"  [XML parse error] {e}: {raw[:80]}", flush=True)
            return []

        responses = []
        if root.tag == "Cmnd":
            r = self._handle_cmnd(root.get("name", ""), root.get("arg", ""))
            if r:
                responses.append(r)
        elif root.tag == "Param":
            name = root.get("name", "?")
            value = root.get("value", "")
            self.params.set(name, value)
            print(f"  [param set] {name} = {value!r}", flush=True)
        return responses

    def _handle_cmnd(self, name: str, arg: str) -> str | None:
        # Pre-auth: command names are OTP-encrypted. The seed is the plaintext arg.
        if not self._authenticated and self._auth_seed_str is None:
            # First message: name=enc(AUTH_INIT, seed), arg=seed (plaintext)
            try:
                seed = int(arg) % len(OTP_KEY)
                plainname = otp_decrypt(name, seed)
                if plainname == "AUTH_INIT":
                    return self._auth_init(arg)
            except (ValueError, Exception):
                pass
            # ADD_TERM is permitted before authentication (firmware allows it)
            if name == "ADD_TERM":
                return self._add_term(arg)
            print(f"  [cmnd] {name} arg={arg!r}", flush=True)
            return None
        elif not self._authenticated and self._auth_seed_str is not None:
            # Second message: name=enc(AUTH_PASS, seed), arg=enc(hash, seed)
            try:
                seed = int(self._auth_seed_str) % len(OTP_KEY)
                plainname = otp_decrypt(name, seed)
                if plainname == "AUTH_PASS":
                    return self._auth_pass(arg)
            except (ValueError, Exception):
                pass
            print(f"  [cmnd] {name} arg={arg!r}", flush=True)
            return None

        # Post-auth: command names are plaintext
        if name == "GET_FILE":
            return self._get_file(arg)
        elif name == "GET_PARAM":
            return self._get_params()
        elif name == "SYNC":
            print(f"  [sync] {arg}", flush=True)
            return xml_sync(arg)
        elif name == "ADD_TERM":
            return self._add_term(arg)
        else:
            print(f"  [cmnd] {name} arg={arg!r}", flush=True)
            return None

    def _auth_init(self, seed_str: str) -> str:
        self._auth_seed_str = seed_str
        seed = int(seed_str) % len(OTP_KEY)
        enc_name = otp_encrypt("AUTH_INIT", seed)
        print(f"  [auth] AUTH_INIT seed={seed_str}", flush=True)
        return f'<Cmnd name="{enc_name}" arg="{seed_str}"/>'

    def _auth_pass(self, encrypted_pass: str) -> str:
        seed = int(self._auth_seed_str or "0") % len(OTP_KEY)
        decrypted = otp_decrypt(encrypted_pass, seed)
        # decrypted IS the MD5 hash string the SWF sends; compare directly
        role = "admin" if decrypted == ADMIN_MD5 else ("user" if decrypted == USER_MD5 else "UNKNOWN")
        print(f"  [auth] password → role={role}", flush=True)
        self._authenticated = True
        self._subscribed = True   # Flash GUI sessions always receive server pushes
        enc_name = otp_encrypt("AUTH_PASS", seed)
        enc_arg  = otp_encrypt("JJRC1", seed)
        return f'<Cmnd name="{enc_name}" arg="{enc_arg}"/>'

    def _add_term(self, arg: str) -> str:
        # Firmware: ADD_TERM registers this connection as a GPDB subscriber.
        # The arg is a connection-type string the camera compares against its own type;
        # we always accept it and set the subscription flag.
        self._subscribed = True
        print(f"  [ADD_TERM] subscribed, arg={arg!r}", flush=True)
        return xml_cmnd("ADD_TERM", arg)

    def _get_file(self, filename: str) -> str:
        print(f"  [GET_FILE] {filename}", flush=True)
        return self.params.registration_xml()

    def _get_params(self) -> str:
        print(f"  [GET_PARAM *] sending {len(self.params.defs)} params", flush=True)
        return self.params.values_xml()

    async def push_param(self, name: str, value: str):
        """Enqueue a server-push <Param> to this client."""
        ptype = self.params.defs.get(name, {}).get("type", "boolean")
        await self.push_queue.put(xml_param(name, ptype, value))


# ── Async server ─────────────────────────────────────────────────────────────

async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    params: ParamStore,
    sessions: list,
    verbose: bool,
):
    peer = writer.get_extra_info("peername")
    print(f"\n[+] Client connected: {peer}", flush=True)
    session = CameraSession(params, verbose)
    sessions.append(session)

    async def rx_loop():
        buf = b""
        try:
            while True:
                chunk = await reader.read(8192)
                if not chunk:
                    break
                buf += chunk
                while b"\x00" in buf:
                    msg_bytes, buf = buf.split(b"\x00", 1)
                    try:
                        msg = msg_bytes.decode("utf-8", errors="replace")
                    except Exception:
                        continue
                    responses = session.handle_message(msg)
                    for resp in responses:
                        if verbose:
                            session._log("→", resp)
                        writer.write((resp + "\x00").encode("utf-8"))
                        await writer.drain()
        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            # Signal tx_loop to exit by pushing a sentinel
            await session.push_queue.put(None)  # type: ignore[arg-type]

    async def tx_loop():
        try:
            while True:
                msg = await session.push_queue.get()
                if msg is None:
                    break
                if verbose:
                    session._log("→push", msg)
                writer.write((msg + "\x00").encode("utf-8"))
                await writer.drain()
        except (ConnectionResetError, BrokenPipeError):
            pass

    try:
        await asyncio.gather(rx_loop(), tx_loop())
    finally:
        sessions.remove(session)
        print(f"[-] Client disconnected: {peer}", flush=True)
        writer.close()


# ── Button injection via stdin ───────────────────────────────────────────────

async def stdin_injector(sessions: list, verbose: bool):
    """Read lines from stdin and push button events to all subscribed sessions."""
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    print("Button injection ready. Type 'help' for available commands.", flush=True)

    async def broadcast(param: str, value: str):
        targets = [s for s in sessions if s._subscribed]
        if not targets:
            print("  [inject] no subscribed clients", flush=True)
            return
        for s in targets:
            await s.push_param(param, value)

    while True:
        try:
            line_bytes = await reader.readline()
        except Exception:
            break
        if not line_bytes:
            break
        line = line_bytes.decode("utf-8", errors="replace").strip()
        if not line:
            continue

        if line == "help":
            print(BUTTON_HELP, flush=True)
        elif line.startswith("set ") and "=" in line:
            # set PARAM_NAME=VALUE
            rest = line[4:]
            k, _, v = rest.partition("=")
            param = k.strip()
            value = v.strip()
            print(f"  [inject] set {param} = {value!r}", flush=True)
            await broadcast(param, value)
        elif line in BUTTON_MAP:
            param = BUTTON_MAP[line]
            print(f"  [inject] {line} → {param}", flush=True)
            await broadcast(param, "true")
            await asyncio.sleep(0.1)
            await broadcast(param, "false")
        else:
            # Allow typing the full param name directly
            print(f"  [inject] unknown: {line!r}  (try 'help')", flush=True)


# ── HTTP asset server ────────────────────────────────────────────────────────

def start_http_server(assets_dir: Path, port: int) -> http.server.HTTPServer:
    """Serve the assets directory over HTTP in a daemon thread."""
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(assets_dir.resolve()),
    )
    # Log only notable requests (panels.xml, .swf) to stdout for debugging
    def _log_request(self, format, *args):
        path = args[0].split()[1] if args else "?"
        if any(x in path for x in ("panels", ".swf", ".xml")):
            print(f"  [HTTP] {path}", flush=True)
    handler.log_message = _log_request  # type: ignore[method-assign]
    httpd = http.server.HTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


# ── Main ─────────────────────────────────────────────────────────────────────

async def main(args):
    factory_xml = Path(args.factory_defaults)
    if not factory_xml.exists():
        sys.exit(f"factory_defaults.xml not found: {factory_xml}")

    print(f"Loading parameters from {factory_xml}...", flush=True)
    params = ParamStore(factory_xml)
    print(f"  Loaded {len(params.defs)} parameters.", flush=True)

    # Apply overrides
    sensor_mx = not args.sensor_orig
    params.set("SENSOR.REVISION_NUMBER", "1" if sensor_mx else "0")
    params.set("SYSTEM.VERSION.RED_RELEASE", args.version)
    params.set("SYSTEM.MANUFACTURING.CAMERA_SERIAL_NUMBER", args.serial)
    params.set("UPGRADE.AVAILABLE", "false")
    params.set("UPGRADE.STATUS", "IDLE")

    for kv in args.set or []:
        if "=" in kv:
            k, v = kv.split("=", 1)
            params.set(k.strip(), v.strip())
            print(f"  Override: {k.strip()} = {v.strip()!r}", flush=True)

    splash_type = "Mysterium-X (MX)" if sensor_mx else "Original RED ONE"
    print(f"  Splash:  {splash_type}", flush=True)
    print(f"  Version: {params.get('SYSTEM.VERSION.RED_RELEASE')}", flush=True)
    print(f"  Serial:  {params.get('SYSTEM.MANUFACTURING.CAMERA_SERIAL_NUMBER')}", flush=True)

    sessions: list[CameraSession] = []

    # HTTP server so OsdXml.load("panels.xml") resolves via http:// not file://
    assets_dir = Path(args.assets_dir)
    swf_url = None
    if assets_dir.exists():
        start_http_server(assets_dir, args.http_port)
        swf_url = f"http://127.0.0.1:{args.http_port}/swf_gui_1.swf"
        print(f"HTTP assets: http://127.0.0.1:{args.http_port}/  (serving {assets_dir})", flush=True)
    else:
        print(f"Warning: assets dir not found: {assets_dir} — panels.xml won't load via HTTP", flush=True)

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, params, sessions, args.verbose),
        "0.0.0.0", args.port
    )
    print(f"\nListening on 0.0.0.0:{args.port}", flush=True)
    # --base is required so XML.load("panels.xml") resolves correctly.
    # Ruffle defaults base to the working directory, not the SWF's directory.
    assets_abs = assets_dir.resolve().as_uri() + "/"   # file:///abs/path/to/assets/
    print("Run Ruffle (file, recommended):", flush=True)
    print(f"  libraries/ruffle firmware/reverse/build_32/assets/swf_gui_1.swf"
          f" --base '{assets_abs}' --filesystem-access-mode allow --tcp-connections allow", flush=True)
    if swf_url:
        base_url = f"http://127.0.0.1:{args.http_port}/"
        print("Run Ruffle (HTTP alternative):", flush=True)
        print(f"  libraries/ruffle '{swf_url}' --base '{base_url}' --tcp-connections allow", flush=True)
    print("Enter IP:    127  .  0  .  0  .  1  then click Camera\n", flush=True)

    async with server:
        await asyncio.gather(
            server.serve_forever(),
            stdin_injector(sessions, args.verbose),
        )


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--factory-defaults",
                    default="firmware/tools/factory_defaults.xml",
                    metavar="PATH")
    ap.add_argument("--port", type=int, default=49152)
    ap.add_argument("--assets-dir",
                    default="firmware/reverse/build_32/assets",
                    metavar="DIR",
                    help="Directory to serve via HTTP for panels.xml / SWF (default: firmware/reverse/build_32/assets)")
    ap.add_argument("--http-port", type=int, default=8000, metavar="PORT",
                    help="HTTP port for the assets server (default: 8000)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sensor-mx",   dest="sensor_orig", action="store_false",
                   default=True, help="SENSOR.REVISION_NUMBER=1 — MX splash (default)")
    g.add_argument("--sensor-orig", dest="sensor_orig", action="store_true",
                   help="SENSOR.REVISION_NUMBER=0 — original RED ONE splash")
    ap.add_argument("--version", default="32.0.3#1",
                    metavar="STR", help="SYSTEM.VERSION.RED_RELEASE")
    ap.add_argument("--serial",
                    default="RED ONE 00000000000001234567890",
                    metavar="STR", help="SYSTEM.MANUFACTURING.CAMERA_SERIAL_NUMBER (23+ chars)")
    ap.add_argument("--set", action="append", metavar="NAME=VALUE",
                    help="Override any param (repeatable)")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="Log full XML messages")
    return ap.parse_args()


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
