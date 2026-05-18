/* $Id: xdmacentral_selftest.c,v 1.3 2007/11/29 11:22:11 svemula Exp $ */
/******************************************************************************
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
******************************************************************************/
/*****************************************************************************/
/**
*
* @file xdmacentral_selftest.c
*
* Contains a diagnostic self-test function for the XDmaCentral driver.
*
* See xdmacentral.h for more information.
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who  Date     Changes
* ----- ---- -------- ------------------------------------------------------
* 1.00a xd   03/12/04 First release
* 1.00b xd   01/13/05 Modified to support both OPB Central DMA and PLB
*                     Central DMA.
* 1.10b mta  03/21/07 Updated to new coding style
* </pre>
*
*****************************************************************************/

/***************************** Include Files ********************************/

#include "xstatus.h"
#include "xdmacentral.h"

/************************** Constant Definitions ****************************/

#define XDMC_SELFTEST_BUFSIZE 16 /**< size of transfer test buffer in bytes */
#define XDMC_SELFTEST_BUFSIZE_INWORD XDMC_SELFTEST_BUFSIZE/sizeof(u32)

/**************************** Type Definitions ******************************/

/***************** Macros (Inline Functions) Definitions ********************/

/************************** Variable Definitions ****************************/

/*
 * Source buffer and Destination buffer for self-test purpose.
 * 32-bit alignment is used because word(4 bytes) will be used as transfer
 * data size.
 */
static u32 SrcBuffer[XDMC_SELFTEST_BUFSIZE_INWORD];
static u32 DestBuffer[XDMC_SELFTEST_BUFSIZE_INWORD];

/************************** Function Prototypes *****************************/


/*****************************************************************************/
/**
*
* Run a self-test on the driver/device. The test resets the device, starts a
* DMA transfer, compares the contents of destination buffer and source
* buffer after the DMA transfer is finished, and resets the device again
* before the function returns.
*
* Note that this is a destructive test in that resets of the device are
* performed. Please refer to the device specification for the device status
* after the reset operation.
*
* If the hardware system is not built correctly, this function may never
* return to the caller.
*
* As this self-test function is supposed to support OPB Central DMA, PLB
* Central DMA and XPS Central DMA, word (4 bytes) is chosen as data size
* for the test transfer.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
*
* @return
*		- XST_SUCCESS if the DMA transfer could get finished and the
*		contents of destination buffer were the same as the
*		source buffer after the transfer.
*		- XST_FAILURE if a Bus error  or Bus timeout occurred or the
*		contents of the destination buffer were different from the
*		source buffer after the transfer was finished.
*
* @note		Caching must be turned off for this function to work.
*
******************************************************************************/
int XDmaCentral_SelfTest(XDmaCentral * InstancePtr)
{
	int Index;
	u32 RegValue;
	u8 *SrcPtr, *DestPtr;

	/*
	 * Assert the argument
	 */
	XASSERT_NONVOID(InstancePtr != NULL);
	XASSERT_NONVOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);

	/*
	 * Initialize the source buffer bytes with a pattern and the
	 * the destination buffer bytes to zero.
	 */
	SrcPtr = (u8 *) SrcBuffer;
	DestPtr = (u8 *) DestBuffer;

	for (Index = 0; Index < XDMC_SELFTEST_BUFSIZE; Index++) {
		SrcPtr[Index] = Index;
		DestPtr[Index] = 0;
	}

	/*
	 * Reset the device to get it back to its default state
	 */
	XDmaCentral_Reset(InstancePtr);

	/* Setup the DMA Control register to be:
	 *        - source address incrementing
	 *        - destination address incrementing
	 *        - using word data size
	 */

	XDmaCentral_SetControl(InstancePtr,
			       XDMC_DMACR_SOURCE_INCR_MASK |
			       XDMC_DMACR_DEST_INCR_MASK |
			       XDMC_DMACR_DATASIZE_4_MASK);


	/*
	 * Flush the Data Cache in the case the Data Cache is enabled.
	 */
	XCACHE_FLUSH_DCACHE_RANGE(&SrcBuffer,  XDMC_SELFTEST_BUFSIZE);
	XCACHE_FLUSH_DCACHE_RANGE(&DestBuffer, XDMC_SELFTEST_BUFSIZE);

	/*
	 * Start the DMA transfer.
	 */
	XDmaCentral_Transfer(InstancePtr, (void *) SrcBuffer,
			     (void *) DestBuffer, XDMC_SELFTEST_BUFSIZE);

	/*
	 * Wait until the DMA transfer is done
	 */
	do {
		/*
		 * Poll DMA status register
		 */
		RegValue = XDmaCentral_GetStatus(InstancePtr);
	}
	while ((RegValue & XDMC_DMASR_BUSY_MASK) == XDMC_DMASR_BUSY_MASK);


	/*
	 * If Bus error or timeout occurs, reset the device and return the error
	 * code.
	 */
	if (RegValue & (XDMC_DMASR_BUS_ERROR_MASK |
	XDMC_DMASR_BUS_TIMEOUT_MASK)) {
		XDmaCentral_Reset(InstancePtr);
		return XST_FAILURE;
	}

	/*
	 * DMA transfer is completely successful, check the destination buffer.
	 */
	for (Index = 0; Index < XDMC_SELFTEST_BUFSIZE; Index++) {
		if (DestPtr[Index] != SrcPtr[Index]) {
			/*
			 * Destination buffer's contents are different from the
			 * source buffer. Reset the device again and return
			 * error code.
			 */
			XDmaCentral_Reset(InstancePtr);
			return XST_FAILURE;
		}
	}

	/*
	 * Destination buffer's contents are the same as the source buffer
	 * Reset the device again and return success code.
	 */
	XDmaCentral_Reset(InstancePtr);
	return XST_SUCCESS;
}

