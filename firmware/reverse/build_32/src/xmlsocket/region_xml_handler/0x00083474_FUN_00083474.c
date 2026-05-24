/* 0x00083474  FUN_00083474  size=632 bytes */


undefined4
FUN_00083474(int param_1,undefined4 param_2,undefined4 param_3,int param_4,int param_5,
            undefined4 param_6,undefined4 param_7)

{
  int iVar1;
  undefined4 *puVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 auStack_208 [4];
  undefined4 uStack_1f8;
  undefined4 uStack_1f4;
  undefined1 auStack_1f0 [32];
  undefined1 auStack_1d0 [32];
  undefined4 uStack_1b0;
  undefined1 auStack_1ac [400];
  undefined1 uStack_1c;
  
  uVar5 = 0;
  if (*(char *)(param_1 + 0x9c94) == '\0') {
    puVar2 = (undefined4 *)FUN_00398e40();
    iVar1 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar1 = *(int *)(param_1 + 0x28);
    }
    uVar5 = *puVar2;
    uVar4 = 0xd41518;
LAB_000836b0:
    FUN_0039995c(uVar5,uVar4,iVar1,param_7);
    uVar5 = 0xffffffff;
  }
  else {
    uStack_1c = 0;
    uStack_1f8 = param_2;
    uStack_1f4 = param_3;
    uStack_1b0 = param_6;
    if (param_4 == 0) {
      FUN_0039b1d4(auStack_1f0,0xd414d4,0x20);
      if (param_5 == 0) goto LAB_00083640;
LAB_000834f0:
      FUN_0039b1d4(auStack_1d0,param_5,0x20);
      FUN_0039b1d4(auStack_1ac,param_7,400);
      iVar1 = FUN_001d9664();
      if (iVar1 == *(int *)(param_1 + 0x18)) {
LAB_00083678:
        uVar3 = FUN_001d9140(*(undefined4 *)(param_1 + 0x9c98));
        if (0x1b5 < uVar3) {
          puVar2 = (undefined4 *)FUN_00398e40();
          iVar1 = param_1 + 0x28;
          if (0xf < *(uint *)(param_1 + 0x3c)) {
            iVar1 = *(int *)(param_1 + 0x28);
          }
          uVar5 = *puVar2;
          uVar4 = 0xd414e4;
          goto LAB_000836b0;
        }
      }
    }
    else {
      FUN_0039b1d4(auStack_1f0,param_4,0x20);
      if (param_5 != 0) goto LAB_000834f0;
LAB_00083640:
      FUN_0039b1d4(auStack_1d0,0xd414dc,0x20);
      FUN_0039b1d4(auStack_1ac,param_7,400);
      iVar1 = FUN_001d9664();
      if (iVar1 == *(int *)(param_1 + 0x18)) goto LAB_00083678;
    }
    if ((*(int *)(param_1 + 4) == 2) ||
       (FUN_000832bc(param_1,&uStack_1f8), *(int *)(param_1 + 4) == 2)) {
      iVar1 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x9c98),&uStack_1f8,0x1e0,0xffffffff);
    }
    else {
      iVar1 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x9c98),&uStack_1f8,0x1e0,0);
    }
    if (iVar1 != 0) {
      puVar2 = (undefined4 *)FUN_00398e40();
      iVar1 = param_1 + 0x28;
      if (0xf < *(uint *)(param_1 + 0x3c)) {
        iVar1 = *(int *)(param_1 + 0x28);
      }
      FUN_0039995c(*puVar2,0xd414a0,iVar1,param_7);
      uVar5 = 0xffffffff;
    }
    if (*(int *)(param_1 + 4) - 2U < 2) {
      auStack_208[0] = 5;
      iVar1 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x20),auStack_208,8,0);
      if (iVar1 != 0) {
        uVar5 = 0xffffffff;
      }
    }
  }
  return uVar5;
}

