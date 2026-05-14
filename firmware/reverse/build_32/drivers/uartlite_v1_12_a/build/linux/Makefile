#
# Makefile for the Xilinx UART Lite
#

ifeq ($(CONFIG_PPC32),y)
EXTRA_CFLAGS		+= -I$(TOPDIR)/arch/ppc/platforms/xilinx_ocp
endif

list-multi		:= xilinx_uartlite.o

# The Linux adapter for the Xilinx driver code.
xilinx_uartlite-objs		+= xuartlite_serial.o

# The Xilinx OS independent code.
xilinx_uartlite-objs		+= xuartlite.o xuartlite_sinit.o \
				xuartlite_g.o xuartlite_intr.o xuartlite_l.o

obj-$(CONFIG_XILINX_UARTLITE) := xilinx_uartlite.o

xilinx_uartlite.o: $(xilinx_uartlite-objs)
	$(LD) -r -o $@ $(xilinx_uartlite-objs)

include $(TOPDIR)/Rules.make
