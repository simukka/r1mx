/* 0x000860bc  FUN_000860bc  size=68 bytes */


int FUN_000860bc(undefined4 param_1,int param_2,int param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < param_3) {
    do {
      if (*(int *)(param_2 + iVar1 * 4) != 0) {
        return iVar1;
      }
      iVar1 = iVar1 + 1;
    } while (iVar1 < param_3);
  }
  return -1;
}

