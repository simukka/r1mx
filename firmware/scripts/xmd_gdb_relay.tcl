# xmd_gdb_relay.tcl — expose the XMD gdb stub to the host (Channel A).
#
# The XMD gdb stub (`connect ppc hw`) binds 127.0.0.1:1234 inside the VM, which
# VBox NAT cannot reach (it forwards to the guest NIC, not loopback). This relay
# listens on 0.0.0.0:2345 (reachable via NAT) and forwards bytes to the stub on
# 127.0.0.1:1234, so the host's rsp.py can drive the silicon with real HW
# breakpoints + task-context memory reads.
#
# Usage in the VM, AFTER `connect ppc hw`:
#   xmd% source {Y:/r1mx/firmware/scripts/xmd_gdb_relay.tcl}
# It blocks (event loop). Ctrl-C to stop. Do NOT also run agent_loop in the same
# console — this replaces Channel B for the duration.

proc _relay_pump {src dst} {
    if {[catch {eof $src} iseof] || $iseof} {
        catch {close $src}; catch {close $dst}; return
    }
    if {[catch {read $src} chunk]} {
        catch {close $src}; catch {close $dst}; return
    }
    if {$chunk ne ""} {
        if {[catch {puts -nonewline $dst $chunk; flush $dst}]} {
            catch {close $src}; catch {close $dst}; return
        }
    }
}

proc _relay_accept {chan addr port} {
    if {[catch {socket 127.0.0.1 1234} stub]} {
        puts "relay: cannot reach gdb stub 127.0.0.1:1234 ($stub) — did you run 'connect ppc hw'?"
        catch {close $chan}; return
    }
    fconfigure $chan -translation binary -buffering none -blocking 0
    fconfigure $stub -translation binary -buffering none -blocking 0
    fileevent $chan readable [list _relay_pump $chan $stub]
    fileevent $stub readable [list _relay_pump $stub $chan]
    puts "relay: host client $addr:$port <-> stub 127.0.0.1:1234"
}

set _relay_srv [socket -server _relay_accept 2345]
puts "xmd_gdb_relay: listening on 0.0.0.0:2345 -> 127.0.0.1:1234 (Ctrl-C to stop)"
vwait _relay_forever
