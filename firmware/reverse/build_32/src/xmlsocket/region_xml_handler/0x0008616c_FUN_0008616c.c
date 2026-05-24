/* 0x0008616c  FUN_0008616c  size=68 bytes */


uint FUN_0008616c(undefined4 param_1,int param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  uVar2 = 0;
  uVar1 = 0;
  iVar4 = 0;
  if (0 < param_3) {
    do {
      iVar3 = *(int *)(param_2 + iVar4 * 4);
      uVar2 = uVar2 + iVar3;
      uVar1 = uVar1 + iVar3 * iVar4;
      iVar4 = iVar4 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return uVar1 / uVar2;
}

