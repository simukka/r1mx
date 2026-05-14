/* xtag_csp_uartns550_v1_10_b.c - Xilinx driver inclusion file */

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

  (c) Copyright 2002 Xilinx Inc.
  All rights reserved.

*/

/*

modification history
--------------------
01a,02apr02,rmm  First release.
01a,13oct05,jvb  version 1.01a of driver

*/

/*
DESCRIPTION
This file is used to compile the UARTNS550 component of the Xilinx Chip Support
Package (CSP).

INCLUDE FILES:

SEE ALSO:
*/
#include "vxWorks.h"
#include "config.h"

#ifdef INCLUDE_XUARTNS550
#  include "xuartns550.c"
#  include "xuartns550_sinit.c"
#  include "xuartns550_g.c"
#  include "xuartns550_l.c"
#  include "xuartns550_format.c"
#  include "xuartns550_intr.c"
#  include "xuartns550_options.c"
#  include "xuartns550_stats.c"
#  include "xuartns550_selftest.c"

#  ifdef INCLUDE_XUARTNS550_VXWORKS5_4
#    include "xuartns550_adapter.c"
#  endif
#endif

