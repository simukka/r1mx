/* $Id: xdmacentral.c,v 1.4 2007/06/11 07:06:29 svemula Exp $ */
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
* @file xdmacentral.c
*
* This file contains the driver API functions that can be used to access
* the Central DMA device on the OPB or the PLB bus.
*
* Please refer to the xdmacentral.h header file for more information about
* this driver.
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who  Date     Changes
* ----- ---- -------- --------------------------------------------------------
* 1.00a xd   03/11/04 First release
* 1.00b xd   01/13/05 Modified to support both OPB Central DMA and PLB
*                     Central DMA.
* 1.00b mta  03/21/07 Modified to support Central DMA on PLB bus.
* 1.10b mta  03/21/07 Updated to new coding style
* </pre>
*
*****************************************************************************/

/***************************** Include Files ********************************/

#include "xio.h"
#include "xdmacentral.h"
#include "xparameters.h"

/************************** Constant Definitions ****************************/


/**************************** Type Definitions ******************************/


/***************** Macros (Inline Functions) Definitions ********************/


/************************** Function Prototypes *****************************/


/************************** Variable Definitions ****************************/

extern XDmaCentral_Config XDmaCentral_ConfigTable[];

/****************************************************************************/
/**
*
* Initialize a specific XDmaCentral instance. This function must be called
* prior to using a Central DMA device. Initialization of a device includes
* looking up the configuration for the given device instance, initializing
* the instance structure, and resetting the device such that it is in a known
* state.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance to be
*		worked on.
* @param	DeviceId is the unique id of the device controlled by this
		XDmaCentral instance.
*
* @return
* 		- XST_SUCCESS if everything initializes as expected.
* 		- XST_DEVICE_NOT_FOUND if the requested device is not found
*
* @note		None.
*
*****************************************************************************/
int XDmaCentral_Initialize(XDmaCentral * InstancePtr, u16 DeviceId)
{
	XDmaCentral_Config *ConfigPtr;

	/*
	 * Assert validates the input arguments
	 */
	XASSERT_NONVOID(InstancePtr != NULL);

	/*
	 * Lookup the device configuration. Use this configuration info below
	 * when initializing this device.
	 */
	ConfigPtr = XDmaCentral_LookupConfig(DeviceId);
	if (ConfigPtr == (XDmaCentral_Config *) NULL) {
		InstancePtr->IsReady = 0;
		return XST_DEVICE_NOT_FOUND;
	}

	/*
	 * Set some default values.
	 */
	InstancePtr->BaseAddress = ConfigPtr->BaseAddress;
	InstancePtr->SupportReadRegs = ConfigPtr->SupportReadRegs;

	/*
	 * Indicate the instance is now ready to use, initialized without error
	 */
	InstancePtr->IsReady = XCOMPONENT_IS_READY;

	/*
	 * Reset the device such that it is in a known state.
	 */
	XDmaCentral_Reset(InstancePtr);

	return XST_SUCCESS;
}


/*****************************************************************************/
/**
*
* Force a software reset to occur in the device.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
*
* @return	None.
*
* @note		This function is a destructive operation such that it should not
*		be called while a DMA transfer is ongoing. Please read the
*		device specification for the device status after this reset
*		operation is executed.
*
******************************************************************************/
void XDmaCentral_Reset(XDmaCentral * InstancePtr)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_VOID(InstancePtr != NULL);
	XASSERT_VOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);

	/*
	 * Write the reset value to the reset register
	 */
	XDmaCentral_mWriteReg(InstancePtr->BaseAddress, XDMC_RST_OFFSET,
			      XDMC_RST_MASK);
}


/*****************************************************************************/
/**
*
* Look up the device configuration given an unique device ID. The table
* XDmaCentral_ConfigTable, defined in xdmacentral_g.c, contains the
* configuration info for each device in the system.
*
* @param	DeviceId is the unique device ID to look for.
*
* @return	A pointer to the configuration data for the device, or NULL if
*		no match is found.
*
* @note		None.
*
******************************************************************************/
XDmaCentral_Config *XDmaCentral_LookupConfig(u16 DeviceId)
{
	XDmaCentral_Config *CfgPtr = NULL;
	int i;

	for (i = 0; i < XPAR_XDMACENTRAL_NUM_INSTANCES; i++) {
		if (XDmaCentral_ConfigTable[i].DeviceId == DeviceId) {
			CfgPtr = &XDmaCentral_ConfigTable[i];
			break;
		}
	}

	return CfgPtr;
}


/****************************************************************************/
/**
*
* Set the contents of DMA Control register. Use the XDMC_DMACR_* constants
* defined in xdmacentral_l.h to create the bit-mask to be written to the
* register.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
* @param	Mask is the 32-bit value to write to the DMA Control register.
*
* @return	None.
*
* @note		OPB Central DMA supports ONLY the  data size of
*		- Byte (XDMC_DMACR_DATASIZE_1_MASK),
*		- Half word (XDMC_DMACR_DATASIZE_2_MASK) or
*		- Word (XDMC_DMACR_DATASIZE_4_MASK).
*
*		PLB Central DMA supports ONLY the  data size of
*		- Word (XDMC_DMACR_DATASIZE_4_MASK)
*		- Double Word (XDMC_DMACR_DATASIZE_8_MASK)
*
*		XPS Central DMA supports ONLY the  data size of
*		- Word (XDMC_DMACR_DATASIZE_4_MASK)
*
*		Using invalid data size may cause unexpected results.
*		This function does not assert using invalid data size.
*		<br><br>
*		The caller is also responsible for making sure different
*		XDMC_DMACR_DATASIZE_*_MASKs are NOT used at the same time. This
*		function asserts using single XDMC_DMACR_DATASIZE_*_MASK.
*
*****************************************************************************/
void XDmaCentral_SetControl(XDmaCentral * InstancePtr, u32 Mask)
{
	u32 DataSize;

	/*
	 * Assert the arguments
	 */
	XASSERT_VOID(InstancePtr != NULL);
	XASSERT_VOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);

	DataSize = Mask & XDMC_DMACR_DATASIZE_MASK;

	XASSERT_VOID((DataSize == XDMC_DMACR_DATASIZE_1_MASK) ||
			(DataSize == XDMC_DMACR_DATASIZE_2_MASK) ||
			(DataSize == XDMC_DMACR_DATASIZE_4_MASK) |
			(DataSize == XDMC_DMACR_DATASIZE_8_MASK));


	/*
	 * Write the mask to the DMA Control register
	 */
	XDmaCentral_mWriteReg(InstancePtr->BaseAddress, XDMC_DMACR_OFFSET,
			      Mask);
}


/****************************************************************************/
/**
*
* Get the contents of DMA Control register. Use the XDMC_DMACR_* constants
* defined in xdmacentral_l.h to interpret the value.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
*
* @return	A 32-bit value representing the contents of DMA Control
*		register.
*
* @note		The hardware parameter C_READ_OPTIONAL_REGS must be set to 1 for
*		this function to work. This function asserts if the
*		hardware parameter is set to 0. Please read the device
*		specification to get more detailed information.
*
*****************************************************************************/
u32 XDmaCentral_GetControl(XDmaCentral * InstancePtr)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_NONVOID(InstancePtr != NULL);
	XASSERT_NONVOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);
	XASSERT_NONVOID(InstancePtr->SupportReadRegs == TRUE);

	/*
	 * Read the DMA Control register
	 */
	return XDmaCentral_mReadReg(InstancePtr->BaseAddress,
				    XDMC_DMACR_OFFSET);
}

/****************************************************************************/
/**
*
* Get the contents of the DMA Status register. Use the XDMC_DMASR_* constants
* defined in xdmacentral_l.h to interpret the value.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
*
* @return	A 32-bit value representing the contents of the Status register.
*
* @note		None
*
*
*****************************************************************************/
u32 XDmaCentral_GetStatus(XDmaCentral * InstancePtr)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_NONVOID(InstancePtr != NULL);
	XASSERT_NONVOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);

	/*
	 * Read the DMA Status register
	 */
	return XDmaCentral_mReadReg(InstancePtr->BaseAddress,
				    XDMC_DMASR_OFFSET);
}


/****************************************************************************/
/**
*
* Get the contents of the Source Address register.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
*
* @return	A 32-bit value representing the contents of the Source Address
*		   register.
*
* @note		The hardware parameter C_READ_OPTIONAL_REGS must be set to 1 for
*		his function to work. This function asserts if the
*		hardware parameter is set to 0. Please read the device
*		specification to get more detailed information.
*
*****************************************************************************/
u32 XDmaCentral_GetSrcAddress(XDmaCentral * InstancePtr)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_NONVOID(InstancePtr != NULL);
	XASSERT_NONVOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);
	XASSERT_NONVOID(InstancePtr->SupportReadRegs == TRUE);

	/*
	 * Read the DMA Source Address register
	 */
	return XDmaCentral_mReadReg(InstancePtr->BaseAddress, XDMC_SA_OFFSET);
}


/****************************************************************************/
/**
*
* Get the contents of the Destination Address register.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
*
* @return	A 32-bit value representing the contents of the Destination
*		Address register.
*
* @note	 	The hardware parameter C_READ_OPTIONAL_REGS must be set to 1 for
*		this function to work. This function asserts if the
*		hardware parameter is set to 0. Please read the device
*		specification to get more detailed information.
*
*****************************************************************************/
u32 XDmaCentral_GetDestAddress(XDmaCentral * InstancePtr)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_NONVOID(InstancePtr != NULL);
	XASSERT_NONVOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);
	XASSERT_NONVOID(InstancePtr->SupportReadRegs == TRUE);

	/*
	 * Read the DMA Destination Address register
	 */
	return XDmaCentral_mReadReg(InstancePtr->BaseAddress, XDMC_DA_OFFSET);
}


/****************************************************************************/
/**
*
* This function starts the DMA transferring data from a memory source
* to a memory destination. This function only starts the operation and returns
* before the operation may be completed.  If the interrupt is enabled, an
* interrupt will be generated when the operation is completed, otherwise it is
* necessary to poll the Status register to determine when it's completed. It is
* the responsibility of the caller to determine when the operation is completed
* by handling the generated interrupt or polling the DMA Status register. (See
* XDmaCentral_GetStatus())
*
* <b>Padding</b>
*
* If the input transfer length is not a multiple of data size, The DMA device
* will pad the destination buffer with extra bytes needed to reach a full
* data size at the end of the transfer. For example, assume the DMA transfer
* length parameter passed into this function equals X,
*
*   - If current data size is double word, then ((X+7)/8)*8 bytes will be
*	 actually transferred.
*   - If current data size is word, then ((X+3)/4)*4 bytes will be actually
*	 transferred.
*   - If the current data size is half word, then ((X+1)/2)*2 bytes will be
*	 actually transferred.
*   - If current data size is byte, then X bytes will be actually transferred.
*
* @param	InstancePtr is a pointer to the XDmaCentral instance.
* @param	SourcePtr contains a pointer to the source memory where the data
*		is to be transferred from and must be aligned to the data size
*		currently used by the Central DMA device.
* @param	DestinationPtr contains a pointer to the destination memory
*		where the data is to be transferred to and must be aligned to
*		the data size currently used by the Central DMA device.
*
* @param	ByteCount contains the number of bytes to transfer during the
*		DMA operation. Please refer to the padding note above.
*
* @return	None.
*
* @note		It is the responsibility of the caller to ensure that the cache
*		is flushed and invalidated both before the DMA operation is
*		started and after the DMA operation completes if the memory
*		pointed to is  cached. The caller must also ensure that the
*		pointers contain physical address rather than a virtual address
*		if address translation is being used.
*		<br><br>
*		The caller is also responsible for setting up the device by
*		writing the correct value to the Control register of the device
*		before this function is called.
*
*****************************************************************************/
void XDmaCentral_Transfer(XDmaCentral * InstancePtr,
			  void *SourcePtr, void *DestinationPtr, u32 ByteCount)
{
	/*
	 * Assert the arguments
	 */
	XASSERT_VOID(InstancePtr != NULL);
	XASSERT_VOID(InstancePtr->IsReady == XCOMPONENT_IS_READY);
	XASSERT_VOID(SourcePtr != DestinationPtr);

	/*
	 * Setup the Source Address and Destination Address registers for the
	 * transfer.
	 */
	XDmaCentral_mWriteReg(InstancePtr->BaseAddress, XDMC_SA_OFFSET,
			      (u32) SourcePtr);

	XDmaCentral_mWriteReg(InstancePtr->BaseAddress, XDMC_DA_OFFSET,
			      (u32) DestinationPtr);

	/*
	 * Start the DMA transfer to copy from the source buffer to the
	 * destination buffer by writing the length to the Length register.
	 */
	XDmaCentral_mWriteReg(InstancePtr->BaseAddress, XDMC_LENGTH_OFFSET,
			      ByteCount);
}
