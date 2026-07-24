/* 0x00396dac  FUN_00396dac  size=112 bytes */


uint FUN_00396dac(int param_1)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  
  if ((*(int *)(param_1 + 4) == param_1) && (*(char *)(param_1 + 10) == 'f')) {
    iVar3 = *(int *)(param_1 + 0x10) + -1;
    *(int *)(param_1 + 0x10) = iVar3;
    if (iVar3 < 0) {
      uVar2 = FUN_00398758();
      return uVar2;
    }
    bVar1 = **(byte **)(param_1 + 0xc);
    *(byte **)(param_1 + 0xc) = *(byte **)(param_1 + 0xc) + 1;
    return (uint)bVar1;
  }
  return 0xffffffff;
}

