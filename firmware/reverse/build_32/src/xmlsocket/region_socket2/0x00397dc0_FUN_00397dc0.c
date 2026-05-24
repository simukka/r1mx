/* 0x00397dc0  FUN_00397dc0  size=152 bytes */


uint FUN_00397dc0(undefined4 param_1,uint param_2,uint param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_28;
  int iStack_24;
  undefined4 *puStack_20;
  undefined4 uStack_1c;
  int iStack_18;
  
  if ((*(int *)(param_4 + 4) == param_4) && (*(char *)(param_4 + 10) == 'f')) {
    iVar2 = param_3 * param_2;
    puStack_20 = &uStack_28;
    uStack_1c = 1;
    uStack_28 = param_1;
    iStack_24 = iVar2;
    iStack_18 = iVar2;
    iVar1 = FUN_00397a4c(param_4,&puStack_20);
    if (iVar1 != 0) {
      param_3 = (uint)(iVar2 - iStack_18) / param_2;
    }
  }
  else {
    param_3 = 0;
  }
  return param_3;
}

