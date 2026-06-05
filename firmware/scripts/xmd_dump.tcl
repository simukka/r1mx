# xmd_dump.tcl -- bulk memory dump helpers for XMD (EDK 10.1) over PPC405 JTAG.
#
# Usage inside XMD (after `connect ppc hw`):
#     source {Y:/r1mx/firmware/scripts/xmd_dump.tcl}
#     dumpmem 0x005bb000 0x400 {Y:/r1mx/components/cpu_io_board/test.bin}
#
# Reads `len` bytes starting at `start` and writes them, byte-for-byte
# (PPC is big-endian), to `fname`. `mrd` is issued in bursts of `chunk`
# words to amortize JTAG overhead; its printed "ADDR:  VALUE" lines are
# parsed back into raw bytes.
#
# READ-ONLY: this script never writes target memory or resets the CPU.

proc dumpmem {start len fname {chunk 1024}} {
    set f [open $fname w]
    fconfigure $f -translation binary -encoding binary
    set end  [expr {$start + $len}]
    set addr $start
    set t0   [clock seconds]
    while {$addr < $end} {
        set n $chunk
        if {[expr {$addr + $n * 4}] > $end} {
            set n [expr {($end - $addr) / 4}]
        }
        set out [mrd $addr $n]
        foreach line [split $out "\n"] {
            set ci [string first ":" $line]
            if {$ci < 0} continue
            foreach w [string range $line [expr {$ci + 1}] end] {
                if {[string is xdigit -strict $w]} {
                    scan $w %x v
                    puts -nonewline $f [binary format I $v]
                }
            }
        }
        incr addr [expr {$n * 4}]
    }
    close $f
    puts "dumpmem: wrote [expr {$end - $start}] bytes to $fname in [expr {[clock seconds] - $t0}]s"
}

# Coherent snapshot: halt the CPU for the duration of the dump, then resume.
# WARNING: a long halt may trip a hardware watchdog and reboot the camera.
# Test watchdog tolerance with a short range before dumping tens of MB.
proc snapshot {start len fname {chunk 1024}} {
    stop
    dumpmem $start $len $fname $chunk
    con
}
