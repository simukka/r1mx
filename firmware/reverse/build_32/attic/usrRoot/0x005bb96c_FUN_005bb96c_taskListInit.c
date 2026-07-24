/* 0x005bb96c  FUN_005bb96c_taskListInit  size=164 bytes */


void FUN_005bb96c(void)

{
  uint uVar1;
  
  uVar1 = FUN_00371ec8();
  FUN_00371ed0(uVar1 & 0xfffffdff);
  uVar1 = FUN_005bbbf0();
  uRam00e3b8a0 = uRam00e3b8a0 | uVar1 & 0x80000000;
  FUN_005bbc18(0x7ec0000);
  uVar1 = FUN_005bbbf0();
  FUN_005bbbf8(uVar1 & 0xbf00ffff);
  FUN_005bbc08(0);
  FUN_005bbc28(0);
  FUN_005bbc38(0);
  FUN_005bbc48(0);
  FUN_005bbc58(0);
  FUN_005bbc68(0);
  FUN_005bbc78(0);
  return;
}

