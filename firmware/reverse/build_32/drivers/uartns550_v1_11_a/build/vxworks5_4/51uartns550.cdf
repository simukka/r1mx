
/*******************************************************************************
* UART component and parameters
*******************************************************************************/

Folder FOLDER_xtag_csp_UARTNS550 {
  NAME       UART 16550 Core
  SYNOPSIS   UART 16550 Core
  _CHILDREN  FOLDER_xtag_csp_CSP
}

Component INCLUDE_XUARTNS550 {
  NAME       UART 16550
  SYNOPSIS   Xilinx 16550 UART driver 
  REQUIRES   
  _CHILDREN  FOLDER_xtag_csp_UARTNS550
}

