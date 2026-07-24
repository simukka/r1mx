/* 0x0039393c  FUN_0039393c  size=40 bytes */


int FUN_0039393c(uint param_1)

{
  int iVar1;
  
  iVar1 = 0;
  for (; param_1 != 0; param_1 = param_1 >> 1) {
    iVar1 = iVar1 + (uint)((param_1 & 1) != 0);
  }
  return iVar1;
}

