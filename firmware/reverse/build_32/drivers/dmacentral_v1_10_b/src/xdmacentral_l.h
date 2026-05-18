/* $Id: xdmacentral_l.h,v 1.3 2007/06/11 07:06:29 svemula Exp $ */
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
* @file xdmacentral_l.h
*
* This header file contains identifiers and basic driver functions (or
* macros) that can be used to access the Central DMA device on the PLB bus.
*
* @note
*
* All provided functions which are register accessors do not provide a lot
* of error detection to minimize the overhead in these functions.
* The caller is expected to understand the impact of a function call based
* upon the current state of the Central DMA.
* <br><br>
* Refer to the device specifications and xdmacentral.h for more information
* about this driver and the device.
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

#ifndef XDMACENTRAL_L_H_ /* Prevent circular inclusions */
#define XDMACENTRAL_L_H_ /* by using protection macros */

#ifdef __cplusplus
extern "C" {
#endif

/***************************** Include Files ********************************/

#include "xbasic_types.h"
#include "xio.h"

/************************** Constant Definitions ****************************/

/**
 * The following constants provide access to each of the registers of the
 * Central DMA device.
 */
#define XDMC_RST_OFFSET		0x00	/**< Reset register */
#define XDMC_MIR_OFFSET		0x00	/**< Module Information register */
#define XDMC_DMACR_OFFSET	0x04	/**< DMA Control register */
#define XDMC_SA_OFFSET		0x08	/**< Source Address register */
#define XDMC_DA_OFFSET		0x0C	/**< Destination Address register */
#define XDMC_LENGTH_OFFSET	0x10	/**< Length register */
#define XDMC_DMASR_OFFSET	0x14	/**< DMA Status register */
#define XDMC_ISR_OFFSET		0x2C	/**< Interrupt Status register */
#define XDMC_IER_OFFSET		0x30	/**< Interrupt Enable register */

/**
 * Central DMA Reset register mask(s)
 */
#define XDMC_RST_MASK 0x0000000AUL	/**< Value used to reset the device */

/**
 * The following constants provide access to the bit fields of the DMA Control
 * register (DMACR). Multiple constants could be "OR"ed together and written
 * to the DMACR. The only exception is that different
 * XDMC_DMACR_DATASIZE_X_MASKs should NOT be used at the same time.
 *
 * !!!Important!!!
 *
 * PLB Central DMA only supports double word (8 bytes) or word
 * (4 bytes) as transfer data size. OPB Central DMA only supports word
 * (4 bytes), half word (2 bytes) or byte as transfer data size.
 * XPS Central DMA only supports word (4 bytes) as transfer data size.
 * Using invalid data size may cause unexpected results. Please read
 * xdmacentral.h and device specifications for details.
 *
 * In OPB Central DMA, only word data size supports Keyhole addressing.
 */
#define XDMC_DMACR_SOURCE_INCR_MASK 0x80000000UL /**<increment source address*/
#define XDMC_DMACR_DEST_INCR_MASK   0x40000000UL /**<increment dest address  */
#define XDMC_DMACR_DATASIZE_8_MASK  0x00000008UL /**<transfer Dsize = 8 bytes*/
#define XDMC_DMACR_DATASIZE_4_MASK  0x00000004UL /**<transfer Dsize = 4 bytes*/
#define XDMC_DMACR_DATASIZE_2_MASK  0x00000002UL /**<transfer Dsize = 2 bytes*/
#define XDMC_DMACR_DATASIZE_1_MASK  0x00000001UL /**<transfer Dsize = 1 byte */
#define XDMC_DMACR_DATASIZE_MASK    0x0000000FUL /**<transfer data size mask */


/**
 * The following constants provide access to the bit fields of the DMA Status
 * register (DMASR)
 *
 * !!!Important!!!
 *
 * PLB/XPS Central DMA supports bus error, but does NOT support bus timeout
 * error. OPB Central DMA supports both bus timeout and bus error. Please read
 * xdmacentral.h and device specifications for details.
 */
#define XDMC_DMASR_BUSY_MASK	     0x80000000UL /**< device is busy */
#define XDMC_DMASR_BUS_ERROR_MASK    0x40000000UL /**< bus error occurred */
#define XDMC_DMASR_BUS_TIMEOUT_MASK  0x20000000UL /**< bus timeout occurred */


/**
 * The following constants provide access to the bit fields of the Interrupt
 * Status register (ISR) and the Interrupt Enable register (IER), bit masks
 * match for both registers such that they are named IXR
 */
#define XDMC_IXR_DMA_DONE_MASK	   0x00000001UL	 /**< DMA operation done  */
#define XDMC_IXR_DMA_ERROR_MASK	   0x00000002UL	 /**< DMA operation error */


/**************************** Type Definitions ******************************/


/***************** Macros (Inline Functions) Definitions ********************/

/****************************************************************************/
/**
*
* Read a register of the Central DMA. This macro provides register access to
* all registers using the register offsets defined above.
*
* @param	BaseAddress contains the base address of the device.
* @param	RegOffset is the offset of the register to read.
*
* @return	The contents of the register.
*
* @note		C-style Signature:
*		u32 XDmaCentral_mReadReg(u32 BaseAddress, u32 RegOffset)
*
******************************************************************************/
#define XDmaCentral_mReadReg(BaseAddress, RegOffset) \
				XIo_In32((BaseAddress) + (RegOffset))


/****************************************************************************/
/**
*
* Write a register of the Central DMA. This macro provides register access to
* all registers using the register offsets defined above.
*
* @param	BaseAddress contains the base address of the device.
* @param	RegOffset is the offset of the register to write.
* @param	Data is the value to write to the register.
*
* @return	None.
*
* @note		C-style Signature:
*		void XDmaCentral_mWriteReg(u32 BaseAddress, u32 RegOffset,
*						u32 Data)
*
******************************************************************************/
#define XDmaCentral_mWriteReg(BaseAddress, RegOffset, Data) \
				XIo_Out32((BaseAddress) + (RegOffset), (Data))


/************************** Function Prototypes *****************************/

#ifdef __cplusplus
}
#endif

#endif /* End of protection macro. */
