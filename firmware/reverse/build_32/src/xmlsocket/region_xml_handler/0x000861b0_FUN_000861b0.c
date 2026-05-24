/* 0x000861b0  FUN_000861b0  size=68 bytes */


int FUN_000861b0(undefined4 param_1,int param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  iVar2 = 0;
  uVar4 = 0;
  iVar3 = 0;
  if (0 < param_3) {
    do {
      uVar1 = *(uint *)(param_2 + iVar3 * 4);
      if (uVar4 < uVar1) {
        iVar2 = iVar3;
        uVar4 = uVar1;
      }
      iVar3 = iVar3 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return iVar2;
}

