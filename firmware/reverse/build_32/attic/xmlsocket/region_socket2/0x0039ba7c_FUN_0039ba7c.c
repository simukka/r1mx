/* 0x0039ba7c  FUN_0039ba7c  size=84 bytes */


void FUN_0039ba7c(int *param_1,int *param_2,int param_3)

{
  int iVar1;
  
  *param_1 = *param_1 + *param_2 / param_3;
  iVar1 = *param_2 - (*param_2 / param_3) * param_3;
  *param_2 = iVar1;
  if (-1 < iVar1 - (iVar1 / param_3) * param_3) {
    return;
  }
  *param_1 = *param_1 + -1;
  *param_2 = param_3 + *param_2;
  return;
}

