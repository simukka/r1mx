/* 0x00027424  FUN_00027424  size=692 bytes */


undefined4 FUN_00027424(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  iVar1 = param_1 * 0x430;
  iVar6 = 0;
  if ((((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) && (iRam00e10734 != 0))
      && (*(int *)(iVar1 + 0x108e9e4) != 0)) &&
     (*(char *)(param_2 * 600 + iVar1 + 0x108e8d4) == '\0')) {
    if (6 < iRam00e107b4) {
      FUN_00443f20(0xd3660c,param_1,param_2,0,0,0,0);
    }
    iVar5 = iVar1 + 0x108e964;
    FUN_005accf4(iVar5,0xffffffff);
    do {
      FUN_0000a07c(*(undefined4 *)(iVar1 + 0x108ea20),(param_2 << 4 | 0xffffffa0U) & 0xff);
      FUN_00020390(param_1,0x40);
      uVar2 = FUN_0036fd0c();
      FUN_0000a07c(*(undefined4 *)(iVar1 + 0x108ea0c),param_4);
      FUN_0000a07c(*(undefined4 *)(iVar1 + 0x108ea18),0x4f);
      FUN_0000a07c(*(undefined4 *)(iVar1 + 0x108ea1c),0xc2);
      FUN_0000a07c(*(undefined4 *)(iVar1 + 0x108ea24),0xb0);
      *(undefined4 *)(iVar1 + 0x108ea48) = 1;
      FUN_0036fd24(uVar2);
      iVar3 = FUN_005accf4(iVar1 + 0x108e8f8,*(undefined4 *)(iVar1 + 0x108e9d8));
      iVar6 = iVar6 + 1;
      if (((*(uint *)(iVar1 + 0x108e9f8) & 1) == 0) && (iVar3 != -1)) {
        FUN_00020390(param_1,8);
        FUN_0000a140(*(undefined4 *)(iVar1 + 0x108ea04),param_3,0x100);
        if (6 < iRam00e107b4) {
          FUN_00443f20(0xd3662c,0,0,0,0,0,0);
        }
        FUN_005ad104(iVar5);
        return 0;
      }
      if (8 < iRam00e107b4) {
        uVar2 = FUN_0000a05c(*(undefined4 *)(iVar1 + 0x108ea2c));
        uVar4 = FUN_0000a05c(*(undefined4 *)(iVar1 + 0x108ea08));
        FUN_00443f20(0xd365bc,param_1,param_2,uVar2,*(undefined4 *)(iVar1 + 0x108e9f8),uVar4,iVar3);
      }
    } while (iVar6 <= iRam00e107c4);
    FUN_005ad104(iVar5);
  }
  return 0xffffffff;
}

