/* 0x0001d61c  FUN_0001d61c  size=196 bytes */


void FUN_0001d61c(int param_1,int param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    FUN_0000e4e0(0xd34d64,0x74);
  }
  else {
    uVar1 = 0x75;
    if ((param_2 != 0) && (uVar1 = 0x76, *(int *)(param_1 + 0x1c) == 0x11111111)) {
      uRam00e9c0ec = 0;
      *(int *)(param_1 + 0x40) = param_2;
      *(undefined4 *)(param_1 + 0x44) = param_3;
      return;
    }
    uRam00e9c0ec = 0;
    FUN_0000e4e0(0xd34d64,uVar1);
  }
  uRam00e9c0ec = 1;
  return;
}

