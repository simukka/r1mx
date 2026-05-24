/* 0x00069508  FUN_00069508  size=612 bytes */


undefined4 FUN_00069508(int param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  char cStack_30;
  char acStack_2f [3];
  undefined4 uStack_2c;
  uint uStack_28;
  uint auStack_24 [4];
  
  uStack_2c = 0;
  uStack_28 = 0;
  auStack_24[0] = 0;
  FUN_005f2a1c(0xd3b5e4,&cStack_30,6,0x65decc);
  FUN_005f2a1c(0xd3b608,acStack_2f,6,0x65decc);
  if ((cStack_30 == '\0') && (acStack_2f[0] == '\0')) {
    if (*(int *)(param_1 + 0x7c) != 0) {
      iVar2 = param_1 + 0x6c;
      if (0xf < *(uint *)(param_1 + 0x80)) {
        iVar2 = *(int *)(param_1 + 0x6c);
      }
      iVar2 = FUN_001aca78(iVar2,&uStack_2c,&uStack_28);
      if (iVar2 != 0) {
        iVar2 = param_1 + 0x28;
        if (0xf < *(uint *)(param_1 + 0x3c)) {
          iVar2 = *(int *)(param_1 + 0x28);
        }
        iVar3 = param_1 + 0x6c;
        if (0xf < *(uint *)(param_1 + 0x80)) {
          iVar3 = *(int *)(param_1 + 0x6c);
        }
        FUN_0005e784(0,3,6,0xd3e720,0x65dee4,0x7c3,0xd3ef98,iVar2,iVar3);
        uStack_2c = 0;
        uStack_28 = 0;
      }
      FUN_0005e8c0();
      uVar1 = FUN_000dae08();
      auStack_24[0] = uStack_28 / (uVar1 / 1000000);
    }
    iVar2 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar2 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(3,0x1000,6,0xd3e720,0x65dee4,2000,0xd3eed8,iVar2,uStack_2c,uStack_28,auStack_24[0])
    ;
    iVar2 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar2 = *(int *)(param_1 + 0x28);
    }
    FUN_005f348c(0xd3ef2c,&uStack_2c,6,iVar2);
    iVar2 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar2 = *(int *)(param_1 + 0x28);
    }
    FUN_005f348c(0xd3ef4c,&uStack_28,6,iVar2);
    iVar2 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar2 = *(int *)(param_1 + 0x28);
    }
    FUN_005f348c(0xd3ef70,auStack_24,6,iVar2);
    FUN_00068e08(param_1);
  }
  return 0;
}

