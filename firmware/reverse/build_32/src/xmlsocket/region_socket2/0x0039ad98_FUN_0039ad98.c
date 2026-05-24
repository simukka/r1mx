/* 0x0039ad98  FUN_0039ad98  size=148 bytes */


int FUN_0039ad98(int param_1)

{
  int iVar1;
  
  do {
    *(int *)(param_1 + 0x28) = param_1;
    iVar1 = FUN_0039b3d0(param_1,param_1 + 0x20,0x20,param_1 + 0x2c);
    if ((iVar1 != 0) && (*(char *)(param_1 + iVar1 + -1) == '\0')) {
      return iVar1 + -1;
    }
    if ((**(char **)(param_1 + 0x20) == '\0') && (*(char *)(param_1 + 0x2c) == '\x10')) {
      *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_1 + 0x24);
    }
  } while (iVar1 == 0);
  return iVar1;
}

