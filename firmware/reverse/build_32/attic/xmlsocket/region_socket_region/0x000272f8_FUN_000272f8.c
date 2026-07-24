/* 0x000272f8  FUN_000272f8  size=300 bytes */


undefined4 FUN_000272f8(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = param_1 * 0x430;
  uVar3 = 0xffffffff;
  iVar2 = param_2 * 600 + iVar1 + 0x108e6a0;
  if (((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) && (iRam00e10734 != 0)) &&
     (*(int *)(iVar1 + 0x108e9e4) != 0)) {
    if (*(char *)(iVar2 + 0x234) == '\0') {
      FUN_005accf4(iVar1 + 0x108e964,0xffffffff);
      uVar3 = FUN_00021a68(param_1,param_2,iVar2);
      FUN_005ad104(iVar1 + 0x108e964);
      FUN_0039ac74(param_3,iVar2,0x200);
    }
    else {
      FUN_0039acec(iVar2,0,0x200);
      FUN_0039acec(param_3,0,0x200);
      uVar3 = 0xffffffff;
    }
  }
  return uVar3;
}

