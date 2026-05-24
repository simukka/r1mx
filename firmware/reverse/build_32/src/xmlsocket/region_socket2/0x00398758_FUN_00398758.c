/* 0x00398758  FUN_00398758  size=88 bytes */


uint FUN_00398758(int param_1)

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  
  iVar1 = FUN_0039856c();
  if (iVar1 == 0) {
    pbVar3 = *(byte **)(param_1 + 0xc);
    *(int *)(param_1 + 0x10) = *(int *)(param_1 + 0x10) + -1;
    *(byte **)(param_1 + 0xc) = pbVar3 + 1;
    uVar2 = (uint)*pbVar3;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

