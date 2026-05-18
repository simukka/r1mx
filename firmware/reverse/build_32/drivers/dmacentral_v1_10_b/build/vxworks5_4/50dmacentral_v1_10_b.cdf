
/*******************************************************************************
* DMA Central component and parameters
*******************************************************************************/

Folder FOLDER_xtag_csp_DMACENTRAL {
  NAME       DMA Central
  SYNOPSIS   DMA Central support
  _CHILDREN  FOLDER_xtag_csp_CSP
}

Component INCLUDE_XDMACENTRAL {
  NAME       DMA Central interface
  SYNOPSIS   DMA Central interface
  REQUIRES   
  _CHILDREN  FOLDER_xtag_csp_DMACENTRAL
}
