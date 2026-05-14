/* $Id: xdmacentral.h,v 1.5 2007/11/29 11:22:11 svemula Exp $ */
/*****************************************************************************
*
*       XILINX IS PROVIDING THIS DESIGN, CODE, OR INFORMATION "AS IS"
*       AS A COURTESY TO YOU, SOLELY FOR USE IN DEVELOPING PROGRAMS AND
*       SOLUTIONS FOR XILINX DEVICES.  BY PROVIDING THIS DESIGN, CODE,
*       OR INFORMATION AS ONE POSSIBLE IMPLEMENTATION OF THIS FEATURE,
*       APPLICATION OR STANDARD, XILINX IS MAKING NO REPRESENTATION
*       THAT THIS IMPLEMENTATION IS FREE FROM ANY CLAIMS OF INFRINGEMENT,
*       AND YOU ARE RESPONSIBLE FOR OBTAINING ANY RIGHTS YOU MAY REQUIRE
*       FOR YOUR IMPLEMENTATION.  XILINX EXPRESSLY DISCLAIMS ANY
*       WARRANTY WHATSOEVER WITH RESPECT TO THE ADEQUACY OF THE
*       IMPLEMENTATION, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OR
*       REPRESENTATIONS THAT THIS IMPLEMENTATION IS FREE FROM CLAIMS OF
*       INFRINGEMENT, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
*       FOR A PARTICULAR PURPOSE.
*
*       (c) Copyright 2004-2007 Xilinx Inc.
*       All rights reserved.
*
*****************************************************************************/
/****************************************************************************/
/**
*
* @file xdmacentral.h
*
* This header file contains prototypes of high-level driver function that can
* be used to access the Central DMA device on the OPB or the PLB bus.
*
*
* <b>DESCRIPTION</b>
*
* Central DMA is a standalone IP core, as opposed to a DMA channel component
* distributed in devices.
*
* Central DMA allows a CPU to minimize the CPU interaction required to move
* data between a memory and a device.  The CPU requests the Central DMA to
* perform a DMA operation and typically continues performing other processing
* until the DMA operation completes.  DMA could be considered a primitive form
* of multiprocessing such that caching and address translation can be an issue.
*
* A feature the Central DMA device contains is supporting different data
* sizes used in each data transfer on the bus.
* Currently data sizes of Byte, Half word (2 bytes) and Word ( 4 bytes) are
* supported by OPB Central DMA device, data sizes of Double word (8 bytes) and
* Word (4 bytes) are supported by PLB Central DMA, and data size of word
* (4 bytes).is supported by XPS Central DMA.
*
*
* !!! Using invalid transfer data size may cause unexpected results !!!
*
* Please be aware that in OPB Central DMA, only Word data size supports
* Keyhole addressing.
*
* Another difference between PLB/XPS Central DMA and OPB Central DMA is that Bus
* Timeout bit in status register is supported only in OPB Central DMA. The bit
* is not defined in PLB/XPS Central DMA.
*
* The user should refer to the hardware device specification for more
* details of the device operation.
*
*
* <b>CONFIGURATION</b>
*
* The Central DMA device supports a parameter, C_READ_OPTIONAL_REGS, at
* hardware design time. The Source Address register, Destination Address
* register, DMA Control register and Interrupt Enable register are:
*
*   - write only if C_READ_OPTIONAL_REGS = 0
*   - readable/writable if C_READ_OPTIONAL_REGS = 1
*
* If the application needs to read the contents of these register, it is
* the responsibility of the application developer to make sure the hardware
* parameter mentioned above is set to 1. This could be done by checking
* data member, ReadOptionalRegs, in the device configuration structure
* XDmaCentral_Config defined in xdmacentral.h. Note that the registers above
* are readable/writable if ReadOptionalRegs equals TRUE, write only if
* ReadOptionalRegs equals FALSE.
*
* This driver does not maintain the current states of these registers. It is
* the responsibility of the application to manage those states if needed.
*
*
* <b>INTERRUPTS</b>
*
* Central DMA has the ability to generate an interrupt. It is the
* responsibility of the caller of DMA functions to manage the interrupt
* including connecting to the interrupt and enabling/disabling the interrupt.
*
*
* <b>CRITICAL SECTIONS</b>
*
* This driver does not use critical sections and it does access registers using
* read-modify-write operations.  Calls to DMA functions from a main thread
* and from an interrupt context could produce unpredictable behavior such that
* the caller must provide the appropriate critical sections.
*
*
* <b>ADDRESS TRANSLATION</b>
*
* All addresses of data structures which are passed to DMA functions must
* be physical (real) addresses as opposed to logical (virtual) addresses.
*
*
* <b>CACHING</b>
*
* The caller of DMA functions is responsible for ensuring that any data
* buffers which are passed to the Central DMA have been flushed from the cache.
*
* The caller of DMA functions is responsible for ensuring that the cache is
* invalidated prior to using any data buffers which are the result of a DMA
* operation.
*
*
* <b>MEMORY ALIGNMENT</b>
*
* The addresses of data buffers which are passed to DMA functions must be
* multiples of the data size currently used by the Central DMA hardware.
* Data size could be set by using DMA functions provided in this driver.
* The caller of this driver should refer to the device specification for
* more details.
*
*
* <b>MUTUAL EXCLUSION</b>
*
* The functions of the Central DMA are not thread safe such that the caller
* of all DMA functions is responsible for ensuring mutual exclusion for a
* Central DMA device.  Mutual exclusion across multiple Central DMA device is
* not necessary.
*
* The user should refer to the hardware device specification for more
* details of the device operation.
*
* <pre>
*
* MODIFICATION HISTORY:
*
* Ver   Who  Date     Changes
* ----- ---- -------- -------------------------------------------------------
* 1.00a xd   03/11/04 First release.
* 1.00b xd   01/13/05 Modified to support both OPB Central DMA and PLB
*                     Central DMA.
* 1.10b mta  03/21/07 Updated to new coding style
*
* </pre>
*
*****************************************************************************/

#ifndef XDMACENTRAL_H_		/* Prevent circular inclusions */
#define XDMACENTRAL_H_		/* by using protection macros */

#ifdef __cplusplus
extern "C" {
#endif

/***************************** Include Files ********************************/

#include "xbasic_types.h"
#include "xstatus.h"
#include "xdmacentral_l.h"
#include "xenv.h"

/************************** Constant Definitions ****************************/


/**************************** Type Definitions ******************************/

/**
 * This typedef contains configuration information for the Central DMA device.
 */
typedef struct {
	u16 DeviceId;		/**< Unique ID of device */
	u32 BaseAddress;	/**< Register base address */
	int SupportReadRegs;	/**< Supports reading IER, CR, SA and DA  */
} XDmaCentral_Config;


/**
 * The driver's instance data. The user is required to allocate a variable
 * of this type for every Central DMA device in the system. A pointer to
 * a variable of this type is then passed to the driver API functions.
 */
typedef struct {
	u32 BaseAddress;	/**< Base address of device */
	u32 IsReady;		/**< Device is initialized and ready */
	int SupportReadRegs;	/**< Supports reading IER, CA, SA and DA ? */
} XDmaCentral;


/***************** Macros (Inline Functions) Definitions ********************/


/************************** Function Prototypes *****************************/

/**
 * Functions in xdmacentral.c
 */
int XDmaCentral_Initialize(XDmaCentral * InstancePtr, u16 DeviceId);
void XDmaCentral_Reset(XDmaCentral * InstancePtr);
XDmaCentral_Config *XDmaCentral_LookupConfig(u16 DeviceId);
void XDmaCentral_SetControl(XDmaCentral * InstancePtr, u32 Value);
u32 XDmaCentral_GetControl(XDmaCentral * InstancePtr);
u32 XDmaCentral_GetStatus(XDmaCentral * InstancePtr);
u32 XDmaCentral_GetSrcAddress(XDmaCentral * InstancePtr);
u32 XDmaCentral_GetDestAddress(XDmaCentral * InstancePtr);
void XDmaCentral_Transfer(XDmaCentral * InstancePtr,
			  void *SourcePtr, void *DestinationPtr, u32 ByteCount);

/**
 * Diagnostic function in xdmacentral_selftest.c
 */
int XDmaCentral_SelfTest(XDmaCentral * InstancePtr);

/**
 * Interrupt functions in xdmacentral_intr.c
 */
void XDmaCentral_InterruptEnableSet(XDmaCentral * InstancePtr, u32 Mask);
u32 XDmaCentral_InterruptEnableGet(XDmaCentral * InstancePtr);
u32 XDmaCentral_InterruptStatusGet(XDmaCentral * InstancePtr);
void XDmaCentral_InterruptClear(XDmaCentral * InstancePtr, u32 Mask);


#ifdef __cplusplus
}
#endif

#endif /* End of protection macro. */

