/* 0x00399cec  FUN_00399cec  size=56 bytes */


void FUN_00399cec(int param_1,int param_2,int *param_3)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1 / param_2;
  *param_3 = iVar2;
  iVar1 = param_1 - param_2 * iVar2;
  param_3[1] = iVar1;
  if (-1 < param_1) {
    return;
  }
  if (iVar1 < 1) {
    return;
  }
  *param_3 = iVar2 + 1;
  param_3[1] = iVar1 - param_2;
  return;
}

