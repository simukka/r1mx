/* $Id: xiic_g.c,v 1.1 2007/12/03 15:44:58 meinelte Exp $ */
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
*       (c) Copyright 2002 Xilinx Inc.
*       All rights reserved.
*
******************************************************************************/
/*****************************************************************************/
/**
*
* @file xiic_g.c
*
* This file contains a configuration table that specifies the configuration of
* IIC devices in the system. Each IIC device should have an entry in this table.
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who  Date     Changes
* ----- --- ------- -----------------------------------------------
* 1.01a rfp  10/19/01 release
* 1.01c ecm  12/05/02 new rev
* 1.01d jhl  10/08/03 Added general purpose output feature
* 1.13a wgr  03/22/07 Converted to new coding style.
* </pre>
*
******************************************************************************/

/***************************** Include Files *********************************/

#include "xiic.h"
#include "xparameters.h"

/************************** Constant Definitions *****************************/

/**************************** Type Definitions *******************************/


/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes ******************************/


/************************** Variable Definitions *****************************/

/**
 * The IIC configuration table, sized by the number of instances
 * defined in xparameters.h.
 */
XIic_Config XIic_ConfigTable[XPAR_XIIC_NUM_INSTANCES] = {
	{
	 XPAR_IIC_0_DEVICE_ID,	/* Device ID for instance */
	 XPAR_IIC_0_BASEADDR,	/* Base address */
	 XPAR_IIC_0_TEN_BIT_ADR,	/* Uses 10 bit addressing */
	 XPAR_IIC_0_GPO_WIDTH,	/* Number of bits in GPO register */
	 }
	,
	{
	 XPAR_IIC_1_DEVICE_ID,	/* Device ID for instance */
	 XPAR_IIC_1_BASEADDR,	/* Base address */
	 XPAR_IIC_1_TEN_BIT_ADR	/* Uses 10 bit addressing */
	 XPAR_IIC_1_GPO_WIDTH,	/* Number of bits in GPO register */
	 }
};
