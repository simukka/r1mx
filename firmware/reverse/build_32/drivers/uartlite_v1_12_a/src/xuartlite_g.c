/* $Id: xuartlite_g.c,v 1.1 2007/05/15 07:00:27 mta Exp $ */
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
*       (c) Copyright 2002 Xilinx Inc.
*       All rights reserved.
*
*****************************************************************************/
/****************************************************************************/
/**
*
* @file xuartlite_g.c
*
* This file contains a configuration table that specifies the configuration of
* UART Lite devices in the system. Each device in the system should have an
* entry in the table.
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who  Date     Changes
* ----- ---- -------- -----------------------------------------------
* 1.00a ecm  08/31/01 First release
* 1.00b jhl  02/21/02 Repartitioned the driver for smaller files
* </pre>
*
******************************************************************************/

/***************************** Include Files *********************************/

#include "xuartlite.h"
#include "xparameters.h"

/************************** Constant Definitions *****************************/


/**************************** Type Definitions *******************************/


/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes ******************************/


/************************** Variable Prototypes ******************************/

/**
 * The configuration table for UART Lite devices
 */
XUartLite_Config XUartLite_ConfigTable[XPAR_XUARTLITE_NUM_INSTANCES] =
{
	{
		XPAR_UARTLITE_0_DEVICE_ID,	/* Unique ID of device */
		XPAR_UARTLITE_0_BASEADDR,	/* Device base address */
		XPAR_UARTLITE_0_BAUDRATE,	/* Fixed baud rate */
		XPAR_UARTLITE_0_USE_PARITY,	/* Fixed parity */
		XPAR_UARTLITE_0_ODD_PARITY,	/* Fixed parity type */
		XPAR_UARTLITE_0_DATA_BITS	/* Fixed data bits */
	},
};


