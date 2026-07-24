/* 0x000211d8  FUN_000211d8  size=236 bytes */


undefined4 FUN_000211d8(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = param_1 * 0x430;
  uVar2 = 0xffffffff;
  if ((((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) && (iRam00e10734 != 0))
      && (*(int *)(iVar1 + 0x108e9e4) != 0)) &&
     (*(char *)(param_2 * 600 + iVar1 + 0x108e8d4) == '\0')) {
    FUN_005accf4(iVar1 + 0x108e964,0xffffffff);
    uVar2 = FUN_00020988(param_1,param_2,0xb0,0xd3,0);
    FUN_005ad104(iVar1 + 0x108e964);
  }
  return uVar2;
}

