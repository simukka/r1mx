/* 0x00120f6c  FUN_00120f6c  size=496 bytes */


void FUN_00120f6c(int param_1,int param_2)

{
  bool bVar1;
  byte unaff_cr3;
  
  if (((uint)(param_2 == 0xffff) & ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {
    FUN_0024ba14(0xea0758);
    FUN_005ea3bc(0xea073c,0xd38c84);
    FUN_005ea3bc(0xea0720,0xd38c84);
    FUN_005ea3bc(0xea0704,0xd38c90);
    FUN_005ea3bc(0xea06e8,0xd38c88);
    FUN_005ea3bc(0xea06cc,0xd769bc);
    FUN_005ea3bc(0xea06b0,0xd4bbf4);
    FUN_005ea3bc(0xea0694,0xd4bc00);
    FUN_005ea3bc(0xea0678,0xd49de4);
    FUN_005ea3bc(0xea065c,0xd49dd0);
  }
  if (((uint)(param_2 == 0xffff) & ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {
    FUN_005ea3bc(0xea0640,0xd4bbe0);
    FUN_005ea3bc(0xea0624,0xd4bbec);
    FUN_005ea3bc(0xea0608,0xd49ddc);
    bVar1 = 0xfffffffe < uRam011533ec;
    uRam011533ec = uRam011533ec + 1;
    iRam011533e8 = iRam011533e8 + (uint)bVar1;
    if ((iRam011533e8 == 0) && (uRam011533ec == 1)) {
      uRam011533f8 = 0;
    }
  }
  if (((uint)(param_2 == 0xffff) & ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {
    bVar1 = 0xfffffffe < uRam01153414;
    uRam01153414 = uRam01153414 + 1;
    iRam01153410 = iRam01153410 + (uint)bVar1;
    if ((iRam01153410 == 0) && (uRam01153414 == 1)) {
      uRam01153418 = 0;
    }
  }
  if (((uint)(param_2 == 0xffff) & ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {
    bVar1 = 0xfffffffe < uRam01153404;
    uRam01153404 = uRam01153404 + 1;
    iRam01153400 = iRam01153400 + (uint)bVar1;
    if ((iRam01153400 == 0) && (uRam01153404 == 1)) {
      uRam01153408 = 0;
    }
  }
  if (((uint)(param_2 == 0xffff) & ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {
    bVar1 = 0xfffffffe < uRam011533e4;
    uRam011533e4 = uRam011533e4 + 1;
    iRam011533e0 = iRam011533e0 + (uint)bVar1;
    if ((iRam011533e0 == 0) && (uRam011533e4 == 1)) {
      uRam011533f0 = 0;
    }
  }
  if (param_2 != 0xffff || param_1 != 0) {
    return;
  }
  FUN_005e8e00(0xea0608);
  FUN_005e8e00(0xea0624);
  FUN_005e8e00(0xea0640);
  FUN_005e8e00(0xea065c);
  FUN_005e8e00(0xea0678);
  FUN_005e8e00(0xea0694);
  FUN_005e8e00(0xea06b0);
  FUN_005e8e00(0xea06cc);
  FUN_005e8e00(0xea06e8);
  FUN_005e8e00(0xea0704);
  FUN_005e8e00(0xea0720);
  FUN_005e8e00(0xea073c);
  FUN_0024b634(0xea0758);
  return;
}

