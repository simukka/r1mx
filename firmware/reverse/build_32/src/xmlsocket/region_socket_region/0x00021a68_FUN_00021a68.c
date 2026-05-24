/* 0x00021a68  FUN_00021a68  size=588 bytes */


undefined4 FUN_00021a68(int param_1,int param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = param_1 * 0x430;
  iVar5 = 0;
  if (6 < iRam00e107b4) {
    FUN_00443f20(0xd358c4,param_1,param_2,0,0,0,0);
  }
  do {
    FUN_0000a07c(*(undefined4 *)(iVar4 + 0x108ea20),(param_2 << 4 | 0xffffffa0U) & 0xff);
    FUN_00020390(param_1,0x40);
    uVar1 = FUN_0036fd0c();
    FUN_0000a07c(*(undefined4 *)(iVar4 + 0x108ea24),0xec);
    *(undefined4 *)(iVar4 + 0x108ea48) = 1;
    FUN_0036fd24(uVar1);
    iVar2 = FUN_005accf4(iVar4 + 0x108e8f8,*(undefined4 *)(iVar4 + 0x108e9d8));
    iVar5 = iVar5 + 1;
    if (((*(uint *)(iVar4 + 0x108e9f8) & 1) == 0) && (iVar2 != -1)) {
      FUN_00020390(param_1,8);
      FUN_0000a140(*(undefined4 *)(iVar4 + 0x108ea04),param_3,0x100);
      if (6 < iRam00e107b4) {
        FUN_00443f20(0xd358b4,0,0,0,0,0,0);
      }
      return 0;
    }
    if (8 < iRam00e107b4) {
      uVar1 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea08));
      FUN_00443f20(0xd35868,param_1,param_2,uVar1,*(undefined4 *)(iVar4 + 0x108e9f8),uVar3,iVar2);
    }
  } while (iVar5 <= iRam00e107c4);
  return 0xffffffff;
}

