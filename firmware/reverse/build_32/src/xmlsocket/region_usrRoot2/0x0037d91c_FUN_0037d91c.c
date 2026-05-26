/* 0x0037d91c  FUN_0037d91c  size=136 bytes */


undefined4 FUN_0037d91c(int *param_1)

{
  int *piVar1;
  uint uVar2;
  
  piVar1 = (int *)param_1[1];
  uVar2 = param_1[7];
  *piVar1 = *param_1;
  *(int **)(*param_1 + 4) = piVar1;
  if (((int)uVar2 < 0) && ((uVar2 & 0x10) == 0)) {
    FUN_0036c134(param_1[3],param_1[4],0);
  }
  *param_1 = (int)piRam00e9c0f4;
  piRam00e9c0f4 = param_1;
  param_1[1] = 0xe9c0f4;
  *(int **)(*param_1 + 4) = param_1;
  return 0;
}

