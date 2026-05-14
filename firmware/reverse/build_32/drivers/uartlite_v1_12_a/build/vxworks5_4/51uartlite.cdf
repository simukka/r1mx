
/*******************************************************************************
* UARTLite component and parameters
*******************************************************************************/

Folder FOLDER_xtag_csp_UARTLITE {
  NAME       UARTLite
  SYNOPSIS   UARTLite support
  _CHILDREN  FOLDER_xtag_csp_CSP
}

Component INCLUDE_XUARTLITE {
  NAME       UARTLite interface
  SYNOPSIS   UARTLite interface
  REQUIRES   
  _CHILDREN  FOLDER_xtag_csp_UARTLITE
}

