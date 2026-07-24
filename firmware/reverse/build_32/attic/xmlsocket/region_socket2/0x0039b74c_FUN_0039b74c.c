/* 0x0039b74c  FUN_0039b74c  size=52 bytes */


int FUN_0039b74c(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  if (param_1 < 0) {
    iVar1 = -2;
  }
  else {
    iVar1 = 1;
  }
  uVar2 = param_1 + iVar1;
  return param_2 + param_1 * 0x16d + ((int)uVar2 >> 2) + (uint)((int)uVar2 < 0 && (uVar2 & 3) != 0);
}

