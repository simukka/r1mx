/* 0x0001fbe8  FUN_0001fbe8  size=100 bytes */


void FUN_0001fbe8(int param_1)

{
  byte bVar1;
  
  param_1 = param_1 * 0x430;
  FUN_0000a05c(*(undefined4 *)(param_1 + 0x108ea3c));
  FUN_0000a0bc(*(undefined4 *)(param_1 + 0x108ea3c),0x60000);
  bVar1 = FUN_0000a05c(*(undefined4 *)(param_1 + 0x108ea40));
  FUN_0000a07c(*(undefined4 *)(param_1 + 0x108ea40),bVar1 | 6);
  return;
}

