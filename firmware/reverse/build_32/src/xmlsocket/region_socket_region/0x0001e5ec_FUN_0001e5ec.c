/* 0x0001e5ec  FUN_0001e5ec  size=272 bytes */


int FUN_0001e5ec(undefined4 *param_1,undefined2 param_2,undefined4 param_3)

{
  int iVar1;
  
  if (param_1 == (undefined4 *)0x0) {
    FUN_0000e4e0(0xd34ed8,0x96);
    uRam00e9c0ec = 1;
    return 0;
  }
  uRam00e9c0ec = 0;
  param_1[8] = param_3;
  FUN_0036fb4c(param_1[8]);
  *param_1 = 0xe10620;
  param_1[1] = 0x2ef68;
  param_1[3] = 0x2ef68;
  *(undefined2 *)(param_1 + 7) = param_2;
  iVar1 = FUN_0001d1a0(param_1 + 9,*(undefined2 *)(param_1 + 7));
  if (iVar1 != 0) {
    return iVar1;
  }
  FUN_0001d61c(param_1 + 9,0x2eea8,param_1);
  return 0;
}

