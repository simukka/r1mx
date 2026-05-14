/* xtag_csp_iic_v1_11_d.c - Xilinx driver inclusion file */

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
01d,09oct03,jhl  version 1.01d of driver
02a,13oct05,jvb  version 1.02a of driver
*/

/*
DESCRIPTION
This file is used to compile the IIC component of the Xilinx Chip Support
Package (CSP).

INCLUDE FILES:

SEE ALSO:
*/
#include "vxWorks.h"
#include "config.h"

#ifdef INCLUDE_XIIC
#  include "xiic.c"
#  include "xiic_sinit.c"
#  include "xiic_g.c"
#  include "xiic_l.c"
#  include "xiic_intr.c"
#  include "xiic_master.c"
#  include "xiic_multi_master.c"
#  include "xiic_options.c"
#  include "xiic_selftest.c"
#  include "xiic_slave.c"
#  include "xiic_stats.c"
#endif
