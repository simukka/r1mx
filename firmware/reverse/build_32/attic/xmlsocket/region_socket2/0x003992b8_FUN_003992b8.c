/* 0x003992b8  FUN_003992b8  size=204 bytes */


undefined4 FUN_003992b8(int param_1)

{
  int iVar1;
  undefined1 *puVar2;
  int iVar3;
  undefined1 *puVar4;
  
  if (param_1 + 0x38 == *(int *)(param_1 + 0x28)) {
    iVar1 = FUN_0045b974(0x400);
    if (iVar1 == 0) {
      return 0xffffffff;
    }
    *(int *)(param_1 + 0x28) = iVar1;
    *(undefined4 *)(param_1 + 0x2c) = 0x400;
    puVar4 = (undefined1 *)(iVar1 + 0x400);
    puVar2 = (undefined1 *)(param_1 + 0x3b);
    iVar3 = 2;
    do {
      puVar2 = puVar2 + -1;
      iVar3 = iVar3 + -1;
      puVar4 = puVar4 + -1;
      *puVar4 = *puVar2;
    } while (-1 < iVar3);
    *(int *)(param_1 + 0xc) = iVar1 + 0x3fd;
  }
  else {
    iVar3 = *(int *)(param_1 + 0x2c);
    iVar1 = FUN_00459fd0(*(int *)(param_1 + 0x28),iVar3 << 1);
    if (iVar1 == 0) {
      return 0xffffffff;
    }
    FUN_0036c8ac(iVar1,iVar1 + iVar3,iVar3);
    *(int *)(param_1 + 0xc) = iVar1 + iVar3;
    *(int *)(param_1 + 0x28) = iVar1;
    *(int *)(param_1 + 0x2c) = iVar3 << 1;
  }
  return 0;
}

