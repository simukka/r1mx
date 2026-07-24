/* 0x00088680  FUN_00088680  size=36 bytes */


void FUN_00088680(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  param_1 = param_2 * 0xc + param_1;
  *(undefined4 *)(param_1 + 0xfbfc) = param_5;
  *(undefined4 *)(param_1 + 0xfbf8) = param_3;
  *(undefined4 *)(param_1 + 0xfbf4) = param_4;
  return;
}

