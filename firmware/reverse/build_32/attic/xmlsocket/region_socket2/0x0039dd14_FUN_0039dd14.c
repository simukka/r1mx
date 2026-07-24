/* 0x0039dd14  FUN_0039dd14  size=264 bytes */


undefined4 FUN_0039dd14(undefined4 *param_1,int *param_2,int param_3)

{
  int iVar1;
  undefined4 *puVar2;
  
  *param_2 = 0;
  do {
    FUN_005accf4(*param_1,0xffffffff);
    if ((param_1[2] == 0) && ((uint)param_1[6] < (uint)param_1[7])) {
      param_1[6] = param_1[6] + 1;
      param_1[5] = param_1[5] + 1;
      iVar1 = FUN_0039efe4(param_1[3] + 8);
      param_1[2] = iVar1;
      if ((code *)param_1[8] != reset_vector) {
        (*(code *)param_1[8])(iVar1 + 8,param_1[3]);
      }
    }
    puVar2 = (undefined4 *)param_1[2];
    if (puVar2 != (undefined4 *)0x0) {
      param_1[2] = *puVar2;
      *param_2 = (int)(puVar2 + 2);
      param_1[5] = param_1[5] + -1;
    }
    FUN_005ad104(*param_1);
    if (*param_2 != 0) {
      return 0;
    }
    if (param_3 != 1) {
      return 0x2c;
    }
    FUN_005accf4(param_1[1],0xffffffff);
  } while (*param_2 == 0);
  return 0;
}

