#
# Makefile for the Xilinx I2C driver
#

ifeq ($(CONFIG_PPC32),y)
EXTRA_CFLAGS		+= -I$(TOPDIR)/arch/ppc/platforms/xilinx_ocp
endif

list-multi		:= xilinx_iic.o

# The Linux driver
xilinx_iic-objs		+= i2c-algo-xilinx.o

# The Xilinx OS independent code.
xilinx_iic-objs		+= xiic.o xiic_sinit.o xiic_g.o xiic_intr.o \
			   xiic_master.o xiic_options.o  xiic_dyn_master.o \
                           xiic_l.o
                           

obj-$(CONFIG_I2C_XILINX) := xilinx_iic.o

xilinx_iic.o: $(xilinx_iic-objs)
	$(LD) -r -o $@ $(xilinx_iic-objs)

include $(TOPDIR)/Rules.make
