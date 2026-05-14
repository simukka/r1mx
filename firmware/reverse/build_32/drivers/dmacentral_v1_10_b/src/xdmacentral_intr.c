/* $Id: xdmacentral_intr.c,v 1.3 2007/05/31 00:29:40 wre Exp $ */
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
* @file xdmacentral_intr.c
*
* This file contains interrupt handling API functions of the Central DMA
* device on PLB.
*
* Please refer to xdmacentral.h header file for more information.
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who  Date     Changes
* ----- ---- -------- -------------------------------------------------------
* 1.00a xd   03/11/04 First release
* 1.00b xd   01/13/05 Modified to support both OPB Central DMA and PLB
*                     Central DMA.
* 1.10b mta  03/21/07 Updated to new coding style
* </pre>
*
******************************************************************************/

/***************************** Include Files *********************************/

#include "xio.h"
#include "xdmacentral.h"

/************************** Constant Definitions *****************************/


/**************************** Type Definitions *******************************/


/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes ******************************/


/************************** Variable Definitions *****************************/


/****************************************************************************/
/**
*
* Set the contents of Interrupt Enable Register. Use the XDMC_IXR_* constants
* defined in xdmacentral_l.h to create the bit-mask to enable interrupts.
*
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
* @param	Mask is the mask to enable. Bit positions of 1 are enabled. Bit
*		positions of 0 are disabled. This mask is formed by OR'ing
*		bits from XDMC_IXR_* bits which are contained in
*		xdmacentral_l.h.
*
* @return	None.
*
* @note		None.
*
*****************************************************************************/
void XDmaCentral_InterruptEnableSet(XDmaCentral * InstancePtr, u32 Mask)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_VOID(InstancePtr != NULL);
	XASSERT_VOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);

	/*
	 * Write the mask to the Interrupt Enable register
	 */
	XDmaCentral_mWriteReg(InstancePtr->BaseAddress, XDMC_IER_OFFSET, Mask);
}

/****************************************************************************/
/**
*
* Get the contents of the Interrupt Enable Register. Use the XDMC_IXR_*
* constants defined in xdmacentral_l.h to interpret the value.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance .
*
* @return	A 32-bit value representing the contents of the Interrupt Enable
*		register.
*
* @note	 	The hardware parameter C_READ_OPTIONAL_REGS must be set to 1 for
*		this function to work. This function asserts if the
*		hardware parameter is set to 0. Please read the device
*		specification to get more detailed information.
*
*****************************************************************************/
u32 XDmaCentral_InterruptEnableGet(XDmaCentral * InstancePtr)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_NONVOID(InstancePtr != NULL);
	XASSERT_NONVOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);
	XASSERT_NONVOID(InstancePtr->SupportReadRegs == TRUE);

	/*
	 * Read the Interrupt Enable register and return the contents
	 */
	return XDmaCentral_mReadReg(InstancePtr->BaseAddress, XDMC_IER_OFFSET);
}


/****************************************************************************/
/**
*
* Get the contents of the Interrupt Status register. Use the XDMC_IXR_*
* constants defined in xdmacentral_l.h to interpret the value.
*
* The Interrupt Status register indicates which interrupts are active
* for the Central DMA device.  The definitions of each bit in the register
* match the definitions of the bits in the Interrupt Enable register.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance .
*
* @return	A 32-bit value representing the contents of the Interrupt Status
*		register.
*
* @note		None.
*
*****************************************************************************/
u32 XDmaCentral_InterruptStatusGet(XDmaCentral * InstancePtr)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_NONVOID(InstancePtr != NULL);
	XASSERT_NONVOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);

	/*
	 * Return the value read from the Interrupt Status register
	 */
	return XDmaCentral_mReadReg(InstancePtr->BaseAddress, XDMC_ISR_OFFSET);
}


/****************************************************************************/
/**
*
* Clear pending interrupts with the provided mask. This function should be
* called after the software has serviced the interrupts that are pending.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
*
* @param	Mask is the mask to clear pending interrupts for. Bit positions
*		of 1 are cleared. This mask is formed by OR'ing bits from
*		XDMC_IXR_* bits which are defined in xdmacentral_l.h.
*
* @return	None.
*
* @note		None.
*
*****************************************************************************/
void XDmaCentral_InterruptClear(XDmaCentral * InstancePtr, u32 Mask)
{
	u32 IntrStatusValue;

	/*
	 * Assert the arguments
	 */
	XASSERT_VOID(InstancePtr != NULL);
	XASSERT_VOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);

	/*
	 * Read current value in Interrupt Status register
	 */
	IntrStatusValue = XDmaCentral_InterruptStatusGet(InstancePtr);

	/*
	 * Filter out any invalid bit in the input mask
	 */
	IntrStatusValue &= Mask;

	/*
	 * Write the mask to the Interrupt Status register to clear active
	 * interrupt(s).
	 */
	XDmaCentral_mWriteReg(InstancePtr->BaseAddress, XDMC_ISR_OFFSET,
			      IntrStatusValue);
}
