# Makefile — compile-check refactored XML socket sources
#
# This is NOT a build for the actual VxWorks target.
# It verifies that the refactored C files are syntactically valid and
# consistent with the shared header (connection_protocol.h).
#
# Usage:
#   make         — compile all .c files to .o (warns suppressed by -w)
#   make clean   — remove generated .o files
#
# All symbols that are extern in connection_protocol.h (BSS globals, firmware
# FUN_XXXXXXXX stubs) will be left as unresolved references — that is expected.
# A linker pass against a VxWorks image would be needed to resolve them.

CC      = gcc
# -w suppresses warnings; additional flags silence int↔pointer casts that are
# correct in Ghidra decompiler output (PPC addresses stored as int locals).
CFLAGS  = -c -w -std=c99 -I. \
          -Wno-int-conversion \
          -Wno-incompatible-pointer-types \
          -Wno-int-to-pointer-cast \
          -Wno-pointer-to-int-cast

SRCS = connection_vxworks.c \
       connection_static_init.c \
       connection_process_gui_cmd.c \
       connection_authenticate.c \
       connection_dispatch.c

OBJS = $(SRCS:.c=.o)

all: $(OBJS)
	@echo "All files compiled successfully."

%.o: %.c connection_protocol.h
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(OBJS)

.PHONY: all clean
