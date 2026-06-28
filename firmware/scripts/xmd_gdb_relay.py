#!/usr/bin/env python
"""TCP relay: 0.0.0.0:2345 <-> 127.0.0.1:1234 (the XMD gdb stub).

Fallback for xmd_gdb_relay.tcl when running the relay outside XMD. Works on
Python 2.7 (Windows XP's last supported Python) and Python 3. No dependencies.

Run inside the VM AFTER `connect ppc hw`:
    python xmd_gdb_relay.py
The host then reaches the stub at host:2345 (VBox NAT -> guest NIC:2345).
"""
import socket
import threading
import sys

LISTEN = ("0.0.0.0", 2345)
STUB = ("127.0.0.1", 1234)


def _pump(a, b):
    try:
        while True:
            data = a.recv(4096)
            if not data:
                break
            b.sendall(data)
    except Exception:
        pass
    finally:
        for s in (a, b):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s.close()
            except Exception:
                pass


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(LISTEN)
    srv.listen(1)
    sys.stdout.write("xmd_gdb_relay: listening on %s:%d -> %s:%d (Ctrl-C to stop)\n"
                     % (LISTEN[0], LISTEN[1], STUB[0], STUB[1]))
    sys.stdout.flush()
    while True:
        client, addr = srv.accept()
        try:
            stub = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            stub.connect(STUB)
        except Exception as e:
            sys.stdout.write("relay: cannot reach stub %s:%d (%s) - run 'connect ppc hw'\n"
                             % (STUB[0], STUB[1], e))
            sys.stdout.flush()
            client.close()
            continue
        sys.stdout.write("relay: client %s:%d <-> stub\n" % (addr[0], addr[1]))
        sys.stdout.flush()
        threading.Thread(target=_pump, args=(client, stub)).start()
        threading.Thread(target=_pump, args=(stub, client)).start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
