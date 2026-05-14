
/*******************************************************************************
* IIC component and parameters
*******************************************************************************/

 Folder FOLDER_xtag_csp_IIC {
   NAME       IIC Core
   SYNOPSIS   IIC Core
   _CHILDREN  FOLDER_xtag_csp_CSP
 }
 
 Component INCLUDE_XIIC {
   NAME       IIC 
   SYNOPSIS   Xilinx IIC driver
   REQUIRES   
   _CHILDREN  FOLDER_xtag_csp_IIC
 }
