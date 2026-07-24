/* 0x00399c6c  FUN_00399c6c  size=56 bytes */


void FUN_00399c6c(int param_1,int param_2,int *param_3)

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

