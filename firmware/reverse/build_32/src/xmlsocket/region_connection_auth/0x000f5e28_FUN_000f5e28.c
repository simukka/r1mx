/* 0x000f5e28  FUN_000f5e28  size=64 bytes */


void FUN_000f5e28(undefined4 param_1,byte *param_2,int param_3,uint param_4)

{
  uint uVar1;
  
  for (; param_3 != 0; param_3 = param_3 + -1) {
    uVar1 = param_4 & 0x3ff;
    param_4 = param_4 + 1;
    *param_2 = *param_2 ^ *(byte *)(uVar1 + 0x661264);
    param_2 = param_2 + 1;
  }
  return;
}

