/* 0x00128938  FUN_00128938  size=600 bytes */


undefined4 FUN_00128938(int param_1)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  int *apiStack_38 [4];
  int *apiStack_28 [4];
  
  apiStack_38[0] = *(int **)(param_1 + 0x38);
  uVar4 = 0;
  if (apiStack_38[0] != (int *)0x0) {
    bVar1 = 0xf < uRam00ea09bc;
    iVar5 = param_1 + 0x30;
    *(int **)(param_1 + 0x30) = apiStack_38[0];
    uVar3 = 0xea09a8;
    if (bVar1) {
      uVar3 = uRam00ea09a8;
    }
    apiStack_28[0] = apiStack_38[0];
    FUN_002264b0(apiStack_38,iVar5,uVar3);
    uVar3 = 0xea0874;
    if (0xf < uRam00ea0888) {
      uVar3 = uRam00ea0874;
    }
    FUN_002264b0(apiStack_28,apiStack_38,uVar3);
    if (((apiStack_28[0] != (int *)0x0) &&
        (iVar2 = (**(code **)(*apiStack_28[0] + 0x2c))(), iVar2 != 0)) &&
       (iVar2 = (**(code **)(*apiStack_28[0] + 0x2c))(), iVar2 != 0)) {
      uVar4 = FUN_00127d5c(param_1);
    }
    uVar3 = 0xea09a8;
    if (0xf < uRam00ea09bc) {
      uVar3 = uRam00ea09a8;
    }
    FUN_002264b0(apiStack_38,iVar5,uVar3);
    uVar3 = 0xea0858;
    if (0xf < uRam00ea086c) {
      uVar3 = uRam00ea0858;
    }
    FUN_002264b0(apiStack_28,apiStack_38,uVar3);
    if (((apiStack_28[0] != (int *)0x0) &&
        (iVar2 = (**(code **)(*apiStack_28[0] + 0x2c))(), iVar2 != 0)) &&
       (iVar2 = (**(code **)(*apiStack_28[0] + 0x2c))(), iVar2 != 0)) {
      uVar4 = FUN_00127454(param_1);
    }
    uVar3 = 0xea09a8;
    if (0xf < uRam00ea09bc) {
      uVar3 = uRam00ea09a8;
    }
    FUN_002264b0(apiStack_38,iVar5,uVar3);
    uVar3 = 0xea083c;
    if (0xf < uRam00ea0850) {
      uVar3 = uRam00ea083c;
    }
    FUN_002264b0(apiStack_28,apiStack_38,uVar3);
    if (((apiStack_28[0] != (int *)0x0) &&
        (iVar5 = (**(code **)(*apiStack_28[0] + 0x2c))(), iVar5 != 0)) &&
       (iVar5 = (**(code **)(*apiStack_28[0] + 0x2c))(), iVar5 != 0)) {
      uVar4 = FUN_00126a1c(param_1);
    }
  }
  return uVar4;
}

