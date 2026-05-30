# Context

We've reverse-engineered the RED ONE MX SWF GUI and built a Python mock server. The camera exposes a TCP XML socket protocol on port 49152 (and an HTTP server on port 8000 for `panels.xml`). Now we want a **Rust SDK** that lets users programmatically connect to and control the camera via this protocol — replacing the Flash GUI with a clean programmatic interface.

---

# Goal

A `r1mx` Rust crate (library + optional CLI) that wraps the camera's XML socket protocol. Users can authenticate, get/set parameters, subscribe to live updates, and send commands.

---

# Protocol Recap

- **Transport**: TCP, port 49152; null-terminated UTF-8 XML strings
- **Auth**: OTP-XOR with a 512-byte key (hardcoded); MD5 hash of password
- **Commands** (`<Cmnd name="..." arg="..."/>`): GET_FILE, GET_PARAM, ADD_TERM, SYNC
- **Parameters** (`<Param name="..." type="..." value="..."/>`): bidirectional
- **Sync** (`<Sync id="..."/>`): server-sent flow control

Boot sequence: AUTH_INIT → AUTH_PASS → GET_FILE "FactoryDefaults.xml" → GET_PARAM "*" → SYNC × 3 → ADD_TERM → interactive

---

# SDK Design

## Crate layout

```
sdk/r1mx-sdk/
├── Cargo.toml
├── src/
│   ├── lib.rs          # public API re-exports
│   ├── client.rs       # CameraClient — high-level async API
│   ├── connection.rs   # low-level TCP framing (null-terminated XML read/write)
│   ├── auth.rs         # OTP key, encrypt/decrypt, MD5 hash
│   ├── protocol.rs     # Message enum (Cmnd, Param, Sync), XML serialization/parsing
│   ├── params.rs       # ParamValue enum (Bool, Num, Str), typed get/set helpers
│   └── error.rs        # CameraError enum
```

## Public API (`CameraClient`)

```rust
// Connect + authenticate
let mut cam = CameraClient::connect("192.168.1.1:49152").await?;
cam.login(Username::Admin).await?;   // or Username::User

// Get a parameter
let state: String = cam.get_param("VIDEO.RECORD.STATE").await?;

// Set a parameter
cam.set_param("SYSTEM.DEV.LCD.BRIGHTNESS", "80").await?;

// Subscribe to live parameter pushes
let mut sub = cam.subscribe().await?;
while let Some(update) = sub.next().await {
    println!("{} = {}", update.name, update.value);
}
```

## Key types

- `Message` — enum parsed from raw XML: `Message::Param`, `Message::Sync`, `Message::Cmnd`
- `ParamValue` — `Bool(bool)`, `Number(f64)`, `Str(String)`
- `CameraError` — `AuthFailed`, `Io(io::Error)`, `Xml(...)`, `Timeout`

---

# Implementation Notes

### OTP auth (auth.rs)
- Hardcoded 512-byte key (copy from `Authenticate.as` / `mock_camera_server.py`)
- `otp_encrypt(seed: u32, plaintext: &[u8]) -> String` — XOR + hex-encode
- `otp_decrypt(seed: u32, hex: &str) -> Vec<u8>`
- Password hashes: Admin = `1b772ea5a3dc1e140c4240b335b1d8b8`, User = `c73f8496a6dc61cee28acf80851e004a`
- Auth flow: parse seed from server's AUTH_INIT, send encrypted AUTH_PASS with MD5 hash

### Framing (connection.rs)
- Read until `\0`, then parse XML
- Write XML + `\0`
- Use `tokio::net::TcpStream` + `BufReader`

### XML parsing (protocol.rs)
- Use `quick-xml` (streaming, no-alloc friendly)
- Parse root tag name (`Cmnd`, `Param`, `Sync`) and attributes

### Subscriptions (client.rs)
- After `ADD_TERM`, background task reads incoming messages
- `tokio::sync::broadcast` channel: `CameraClient::subscribe()` returns a receiver

---

# Dependencies (Cargo.toml)

```toml
tokio = { version = "1", features = ["net", "io-util", "rt-multi-thread", "macros"] }
quick-xml = "0.36"
md5 = "0.7"
thiserror = "2"
```

---

# File locations

- New crate: `sdk/r1mx-sdk/`
- Reference the OTP key from: `firmware/reverse/build_32/src/xmlsocket/refactored/connection_protocol.h` or `firmware/tools/mock_camera_server.py`
- Reference param types from: `firmware/tools/factory_defaults.xml`

---

# Verification

1. `cargo build` — compiles cleanly
2. `cargo test` — unit tests for OTP encrypt/decrypt (round-trip), XML parse
3. Integration test against the mock server:
   ```bash
   python3 firmware/tools/mock_camera_server.py &
   cargo test --test integration -- --nocapture
   ```
   - Connect, authenticate, GET_PARAM VIDEO.RECORD.STATE, receive a value
   - SET_PARAM SYSTEM.DEV.LCD.BRIGHTNESS=50, verify echo back
   - Subscribe, inject a button press via mock stdin, observe push event
