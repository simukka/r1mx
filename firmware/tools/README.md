# RED ONE MX Camera GUI Emulation Tools

Run the camera's Flash GUI (`swf_gui_1.swf`) outside the physical camera using
a Python mock server and Ruffle (open-source Flash emulator).

## Quick Start

```bash
# Terminal 1 — start mock camera server:
python3 firmware/tools/mock_camera_server.py

# Terminal 2 — launch the GUI:
/tmp/ruffle firmware/reverse/build_32/assets/swf_gui_1.swf --tcp-connections allow
```

In the Ruffle window:
1. Set the four IP fields to `127` / `0` / `0` / `1`
2. Wait ~500ms for the "Camera" button to appear (socket probe)
3. Click **Camera** → GPDB boot sequence runs → SplashScreenMC renders

## Options

```
python3 firmware/tools/mock_camera_server.py \
    --sensor-mx          # Mysterium-X splash (default)
    --sensor-orig        # Original RED ONE splash
    --version 32.0.3#1   # SYSTEM.VERSION.RED_RELEASE
    --serial "RED ONE 00000000000001234567890"
    --set UPGRADE.AVAILABLE=true   # show firmware upgrade prompt
    -v                   # verbose: log all XML messages
```

## Files

| File | Description |
|------|-------------|
| `mock_camera_server.py` | Python asyncio mock server, port 49152 |
| `factory_defaults.xml` | 893 parameter definitions extracted from firmware offset 0xC6E1A4 |

## Protocol summary

Flash `XMLSocket` sends null-terminated UTF-8 XML strings. Boot sequence:

```
Flash → AUTH_INIT seed
Server → AUTH_INIT_ENCRYPTED (OTP-XOR of seed)
Flash → AUTH_PASS_ENCRYPTED (OTP-XOR of MD5 password)
Server → AUTH_PASS_ENCRYPTED (OTP-XOR of "JJRC1")
Flash → GET_FILE FactoryDefaults.xml
Server → <RedParameters> with all 893 param definitions
Flash → SYNC SYNC_EVENT_0
Server → <Sync id="SYNC_EVENT_0"/>
Flash → GET_PARAM *
Server → <RedParameters> with current param values
Flash → SYNC SYNC_EVENT_1  → GoSplash() fires → SplashScreenMC visible
Flash → SYNC SYNC_EVENT_2  → UpgradeMC.SmartUpgrade() fires
```

## Getting Ruffle

```bash
wget https://github.com/ruffle-rs/ruffle/releases/download/v0.2.0/ruffle-0.2.0-linux-x86_64.tar.gz
tar -xzf ruffle-0.2.0-linux-x86_64.tar.gz
# Binary: ./ruffle
```
