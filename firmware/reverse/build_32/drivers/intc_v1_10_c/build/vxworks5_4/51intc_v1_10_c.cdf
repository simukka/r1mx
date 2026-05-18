
/*******************************************************************************
* Interrupt controller
*******************************************************************************/

Folder FOLDER_xtag_csp_INTC {
  NAME       Interrupt controller Core
  SYNOPSIS   Interrupt controller Core
  _CHILDREN  FOLDER_xtag_csp_CSP
}

Component INCLUDE_XINTC {
  NAME       INTC
  SYNOPSIS   Xilinx Interrupt controller
  REQUIRES   
  _CHILDREN  FOLDER_xtag_csp_INTC
}
