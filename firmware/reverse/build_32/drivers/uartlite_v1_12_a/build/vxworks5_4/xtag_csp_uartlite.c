/* xtag_csp_uartlite.c - Xilinx driver inclusion file */

/*
  XILINX IS PROVIDING THIS DESIGN, CODE, OR INFORMATION "AS IS"
  AS A COURTESY TO YOU, SOLELY FOR USE IN DEVELOPING PROGRAMS AND
  SOLUTIONS FOR XILINX DEVICES.  BY PROVIDING THIS DESIGN, CODE,
  OR INFORMATION AS ONE POSSIBLE IMPLEMENTATION OF THIS FEATURE,
  APPLICATION OR STANDARD, XILINX IS MAKING NO REPRESENTATION
  THAT THIS IMPLEMENTATION IS FREE FROM ANY CLAIMS OF INFRINGEMENT,
  AND YOU ARE RESPONSIBLE FOR OBTAINING ANY RIGHTS YOU MAY REQUIRE
  FOR YOUR IMPLEMENTATION.  XILINX EXPRESSLY DISCLAIMS ANY
  WARRANTY WHATSOEVER WITH RESPECT TO THE ADEQUACY OF THE
  IMPLEMENTATION, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OR
  REPRESENTATIONS THAT THIS IMPLEMENTATION IS FREE FROM CLAIMS OF
  INFRINGEMENT, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
  FOR A PARTICULAR PURPOSE.

  (c) Copyright 2002-2007 Xilinx Inc.
  All rights reserved.

*/

/*

modification history
--------------------
01a,02apr02,rmm  First release.
01a,13oct05,jvb  version 1.01a of driver
02a,13feb07,rpm  version 1.02a of driver

*/

/*
DESCRIPTION
This file is used to compile the UARTLITE component of the Xilinx Chip Support
Package (CSP).

INCLUDE FILES:

SEE ALSO:
*/
#include "vxWorks.h"
#include "config.h"

#ifdef INCLUDE_XUARTLITE
#  include "xuartlite.c"
#  include "xuartlite_sinit.c"
#  include "xuartlite_g.c"
#  include "xuartlite_l.c"
#  include "xuartlite_intr.c"
#  include "xuartlite_selftest.c"
#  include "xuartlite_stats.c"
#endif

#ifdef INCLUDE_XUARTLITE_VXWORKS5_4
#  include "xuartlite_sio_adapter.c"
#endif





