/* 0x00021d9c  FUN_00021d9c  size=244 bytes */


int FUN_00021d9c(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = param_1 * 0x430;
  iVar2 = -1;
  iVar3 = param_2 * 600 + iVar1 + 0x108e6a0;
  if ((((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) && (iRam00e10734 != 0))
      && (*(int *)(iVar1 + 0x108e9e4) != 0)) && (*(char *)(iVar3 + 0x234) == '\0')) {
    iVar2 = 0;
    if ((*(ushort *)(iVar3 + 0xaa) & 8) != 0) {
      FUN_005accf4(iVar1 + 0x108e964,0xffffffff);
      FUN_00021a68(param_1,param_2,iVar3);
      FUN_005ad104(iVar1 + 0x108e964);
      iVar2 = (int)*(short *)(iVar3 + 0xb6);
    }
  }
  return iVar2;
}

