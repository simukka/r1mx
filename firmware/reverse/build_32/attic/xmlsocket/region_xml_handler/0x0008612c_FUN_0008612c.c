/* 0x0008612c  FUN_0008612c  size=64 bytes */


void FUN_0008612c(undefined4 param_1,int param_2,uint param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = 0;
  uVar2 = 0;
  if (0 < param_4) {
    do {
      uVar2 = uVar2 + *(int *)(param_2 + iVar1 * 4);
      if (param_3 >> 1 <= uVar2) {
        return;
      }
      iVar1 = iVar1 + 1;
    } while (iVar1 < param_4);
  }
  return;
}

