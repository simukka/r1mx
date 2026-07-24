/* 0x00396e1c  FUN_00396e1c  size=96 bytes */


uint FUN_00396e1c(int param_1,int *param_2)

{
  int iVar1;
  
  if ((*(int *)(param_1 + 4) == param_1) && (*(char *)(param_1 + 10) == 'f')) {
    iVar1 = FUN_0039798c();
    *param_2 = iVar1;
    return ((uint)(byte)((iVar1 == -1) << 1) << 8) >> 9;
  }
  return 0xffffffff;
}

