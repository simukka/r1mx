/* 0x000239c8  FUN_000239c8  size=272 bytes */


undefined4 FUN_000239c8(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = param_1 * 0x430;
  iVar3 = param_2 * 600 + iVar1 + 0x108e6a0;
  if ((((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) && (iRam00e10734 != 0))
      && (*(int *)(iVar1 + 0x108e9e4) != 0)) && (*(char *)(iVar3 + 0x234) == '\0')) {
    iVar1 = *(int *)(iVar3 + 0x23c);
    if (iVar1 == 1) {
      uVar2 = FUN_00023808();
      return uVar2;
    }
    if (iVar1 < 2) {
      if (iVar1 == 0) {
        return 0;
      }
    }
    else if (iVar1 == 2) {
      uVar2 = FUN_0002367c();
      return uVar2;
    }
  }
  else if (8 < iRam00e107b4) {
    FUN_00443f20(0xd35cbc,0x65c7b0,param_1,param_2,iRam00e10734,*(undefined4 *)(iVar1 + 0x108e9e4),
                 *(undefined1 *)(iVar3 + 0x234));
  }
  return 0xffffffff;
}

