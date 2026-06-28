# xmd_agent.tcl -- file-queue bridge so the Linux host can drive XMD without
# networking. Runs INSIDE XMD (EDK 10.1) in the WinXP VM; communicates through
# the shared folder that maps Y:\r1mx\ <-> /home/simukka/src/RED/r1mx/.
#
# This is Channel B (see host_xmd_bridge.md): the fallback for when the GDB-stub
# TCP bridge (Channel A) is unavailable, and the only path for XMD-only commands
# the GDB stub doesn't expose (gated `mrd` of DCR/peripheral regs, JTAG ops,
# and any SPR access XMD supports).
#
# Usage (inside XMD, after `connect ppc hw`):
#     source {Y:/r1mx/firmware/scripts/xmd_agent.tcl}
#     agent_loop                 ;# blocks, polling for commands
#   (Ctrl-C in the XMD console to stop.)
#
# Protocol (host writes cmd, agent writes result):
#     <dir>/xmd_cmd.txt   one XMD command (host creates; agent deletes)
#     <dir>/xmd_out.txt   command result, terminated by a line "__DONE__"
#
# GUARDED: `rst`/`mwr`/`rwr` are allowed this session (cold-boot lockstep), but
# ROM/flash is NEVER writable -- mwr at/above $::ROM_FLOOR is refused, and the
# flash/FPGA programming ops stay hard-denied. See host_xmd_bridge.md.

set ::AGENT_DIR {Y:/r1mx/firmware/scratch/xmd_bridge}
set ::AGENT_CMD "$::AGENT_DIR/xmd_cmd.txt"
set ::AGENT_OUT "$::AGENT_DIR/xmd_out.txt"

# Ops that touch flash/FPGA config ROM -- never allowed (protect the ROM).
set ::AGENT_DENY {dow program erase init_fpga fpga}
# Any memory write at/above this address is NOR flash (0xf0000000) or boot ROM
# (0xffff0000) -- refuse writes there even though mwr is otherwise permitted.
set ::ROM_FLOOR 0xf0000000

proc addr_in_rom {a} {
    # Parse an XMD address token (hex, optional 0x). Fail-safe: unparseable -> ROM.
    if {[scan $a "0x%x" v] != 1 && [scan $a "%x" v] != 1} { return 1 }
    return [expr {$v >= $::ROM_FLOOR && $v <= 0xffffffff}]
}

proc agent_denied {cmd} {
    set toks [split [string trim $cmd]]
    set first [string tolower [lindex $toks 0]]
    if {[lsearch -exact $::AGENT_DENY $first] >= 0} { return 1 }
    # Memory-write ops: never into ROM/flash.
    if {$first eq "mwr" || $first eq "mset"} {
        if {[addr_in_rom [lindex $toks 1]]} { return 1 }
    }
    return 0
}

proc agent_write {text} {
    set f [open $::AGENT_OUT w]
    fconfigure $f -translation binary -encoding binary
    puts -nonewline $f $text
    puts -nonewline $f "\n__DONE__\n"
    close $f
}

proc agent_once {} {
    if {![file exists $::AGENT_CMD]} { return 0 }
    set f [open $::AGENT_CMD r]
    set cmd [string trim [read $f]]
    close $f
    file delete -force $::AGENT_CMD
    if {$cmd eq ""} { return 1 }
    if {[agent_denied $cmd]} {
        agent_write "ERROR: command refused (read-only guard): $cmd"
        return 1
    }
    if {[catch {uplevel #0 $cmd} res]} {
        agent_write "ERROR: $res"
    } else {
        agent_write $res
    }
    return 1
}

proc agent_loop {{poll_ms 200}} {
    file mkdir $::AGENT_DIR
    puts "xmd_agent: polling $::AGENT_CMD every ${poll_ms}ms (Ctrl-C to stop)"
    while {1} {
        if {[catch {agent_once} err]} {
            catch {agent_write "AGENT-FAULT: $err"}
        }
        after $poll_ms
    }
}
