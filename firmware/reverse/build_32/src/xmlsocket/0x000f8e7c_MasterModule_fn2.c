
undefined4 MasterModule_fn2(int param_1,uint *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_120 [256];
  undefined1 auStack_20 [20];
  
  uVar1 = *param_2;
  if (uVar1 == 5) {
    iVar3 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar3 = *(int *)(param_1 + 0x28);
    }
    uVar2 = 0xd4a094;
    if (param_2[2] != 0) {
      uVar2 = 0xd4a0a0;
    }
    FUN_0005e784(2,3,0x1f,0xd49df8,0x661878,0x1aa,0xd4a0ac,iVar3,uVar2);
    FUN_000f890c(param_1,param_2[2]);
  }
  else if (uVar1 < 6) {
    if (uVar1 != 2) {
LAB_000f8eb4:
      iVar3 = param_1 + 0x28;
      if (0xf < *(uint *)(param_1 + 0x3c)) {
        iVar3 = *(int *)(param_1 + 0x28);
      }
      FUN_0005e784(0,3,0x1f,0xd49df8,0x661878,0x1cb,0xd3fb78,iVar3);
      return 0;
    }
    iVar3 = FUN_00359680(0x106314,param_1);
    if (iVar3 == 0) {
      iVar3 = FUN_00359e74(0,0x100c,auStack_20);
      if (iVar3 != -1) {
        FUN_000f890c(param_1,0);
      }
    }
    else {
      iVar3 = param_1 + 0x28;
      if (0xf < *(uint *)(param_1 + 0x3c)) {
        iVar3 = *(int *)(param_1 + 0x28);
      }
      FUN_0005e784(0,3,0x1f,0xd49df8,0x661878,0x1a4,0xd4a068,iVar3);
    }
  }
  else {
    if (uVar1 != 6) goto LAB_000f8eb4;
    iVar3 = *(int *)(param_1 + 100);
    if (iVar3 == 1) {
      FUN_0039ac74(auStack_120,param_2 + 3,0x100);
      uVar2 = FUN_000f6500(param_1,auStack_120,0);
      *(undefined4 *)(param_1 + 100) = uVar2;
    }
    else if (iVar3 == 2) {
      FUN_0039ac74(auStack_120,param_2 + 3,0x100);
      uVar2 = FUN_000f7a4c(param_1,auStack_120);
      *(undefined4 *)(param_1 + 100) = uVar2;
    }
    else if (iVar3 == 3) {
      FUN_0039ac74(auStack_120,param_2 + 3,0x100);
    }
  }
  return 1;
}

