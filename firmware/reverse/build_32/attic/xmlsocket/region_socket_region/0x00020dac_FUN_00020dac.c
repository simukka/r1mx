/* 0x00020dac  FUN_00020dac  size=352 bytes */


undefined4 FUN_00020dac(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = param_1 * 0x430;
  if ((((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) && (iRam00e10734 != 0))
      && (*(int *)(iVar1 + 0x108e9e4) != 0)) &&
     (*(char *)(param_2 * 600 + iVar1 + 0x108e8d4) == '\0')) {
    iVar3 = iVar1 + 0x108e964;
    FUN_005accf4(iVar3,0xffffffff);
    iVar2 = FUN_00020988(param_1,param_2,0xb0,0xda,0);
    if (iVar2 == 0) {
      iVar2 = FUN_0000a05c(*(undefined4 *)(iVar1 + 0x108ea18));
      iVar1 = FUN_0000a05c(*(undefined4 *)(iVar1 + 0x108ea1c));
      if (iVar2 == 0x4f && iVar1 == 0xc2) {
        FUN_005ad104(iVar3);
        return 0;
      }
      if (iVar2 == 0xc2 && iVar1 == 0x4f) {
        FUN_005ad104(iVar3);
        return 1;
      }
    }
    FUN_005ad104(iVar3);
  }
  return 0xffffffff;
}

