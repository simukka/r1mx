/* 0x0002ba90  FUN_0002ba90  size=100 bytes */


void FUN_0002ba90(int *param_1)

{
  int iVar1;
  
  iVar1 = *param_1;
  FUN_005accf4(*(undefined4 *)(*param_1 + 0x34),0xffffffff);
  *(short *)(param_1[1] + 0x40) = *(short *)(param_1[1] + 0x40) + -1;
  param_1[0x11] = 0;
  FUN_005ad104(*(undefined4 *)(iVar1 + 0x34));
  return;
}

