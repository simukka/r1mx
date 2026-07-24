/* 0x0039dc8c  FUN_0039dc8c  size=136 bytes */


undefined4 FUN_0039dc8c(undefined4 *param_1)

{
  int iVar1;
  
  FUN_005ac50c(*param_1);
  FUN_005ac50c(param_1[1]);
  iVar1 = param_1[2];
  while (iVar1 != 0) {
    iVar1 = *(int *)param_1[2];
    if ((code *)param_1[9] != reset_vector) {
      (*(code *)param_1[9])((int *)param_1[2] + 2,param_1[3]);
    }
    FUN_0039f108(param_1[2]);
    param_1[2] = iVar1;
  }
  FUN_0039f108(param_1);
  return 0;
}

