/* 0x0039725c  FUN_0039725c  size=120 bytes */


undefined4 FUN_0039725c(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 *puStack_10;
  undefined4 uStack_c;
  undefined4 uStack_8;
  
  if ((*(int *)(param_2 + 4) == param_2) && (*(char *)(param_2 + 10) == 'f')) {
    uStack_18 = param_1;
    uStack_14 = FUN_0039b0f0();
    puStack_10 = &uStack_18;
    uStack_c = 1;
    uStack_8 = uStack_14;
    uVar1 = FUN_00397a4c(param_2,&puStack_10);
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

