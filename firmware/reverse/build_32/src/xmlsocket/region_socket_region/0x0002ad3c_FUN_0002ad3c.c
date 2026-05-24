/* 0x0002ad3c  FUN_0002ad3c  size=128 bytes */


undefined4
FUN_0002ad3c(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  *(undefined4 *)(param_2 + 8) = param_3;
  *(undefined4 *)(param_2 + 0xc) = param_4;
  *(undefined4 *)(param_2 + 0x10) = *(undefined4 *)(param_1 + 0x60);
  *(undefined4 *)(param_2 + 0x1c) = 0;
  *(undefined4 *)(param_2 + 0x20) = param_5;
  *(undefined4 *)(param_2 + 0x24) = 0x3ad18;
  *(undefined4 *)(param_2 + 0x28) = *(undefined4 *)(param_1 + 0x70);
  *(undefined4 *)(param_2 + 0x2c) = 0;
  FUN_005b80c8(*(undefined4 *)(param_1 + 0x28));
  FUN_005accf4(*(undefined4 *)(param_1 + 0x70),0xffffffff);
  return *(undefined4 *)(param_2 + 0x1c);
}

