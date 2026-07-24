/* 0x0039b780  FUN_0039b780  size=116 bytes */


int FUN_0039b780(int param_1,int param_2,int param_3)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1 + 0x76c;
  iVar1 = 0;
  if (uVar2 == (((int)uVar2 >> 2) + (uint)((int)uVar2 < 0 && (uVar2 & 3) != 0)) * 4) {
    if (param_1 + 0x76c == ((param_1 + 0x76c) / 100) * 100) goto LAB_0039b7b4;
  }
  else {
LAB_0039b7b4:
    if (param_1 + 0x76c != ((param_1 + 0x76c) / 400) * 400) goto LAB_0039b7d8;
  }
  if (1 < param_2) {
    iVar1 = 1;
  }
LAB_0039b7d8:
  return iVar1 + param_3 + *(int *)(param_2 * 4 + 0xe2749c);
}

