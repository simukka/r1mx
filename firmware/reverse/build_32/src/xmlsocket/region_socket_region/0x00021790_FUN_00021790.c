/* 0x00021790  FUN_00021790  size=248 bytes */


undefined4 FUN_00021790(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = param_1 * 0x430;
  uVar3 = 0xffffffff;
  iVar2 = param_2 * 600 + iVar1 + 0x108e6a0;
  if ((((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) && (iRam00e10734 != 0))
      && (*(int *)(iVar1 + 0x108e9e4) != 0)) && (*(char *)(iVar2 + 0x234) == '\0')) {
    uVar3 = 0xffffffff;
    if ((*(ushort *)(iVar2 + 0xa4) & 8) != 0) {
      FUN_005accf4(iVar1 + 0x108e964,0xffffffff);
      uVar3 = FUN_00020988(param_1,param_2,0xef,0x85,0);
      FUN_005ad104(iVar1 + 0x108e964);
    }
  }
  return uVar3;
}

