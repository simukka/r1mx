/* 0x0002253c  FUN_0002253c  size=580 bytes */


undefined4 FUN_0002253c(int param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  
  iVar4 = param_1 * 0x430;
  if (6 < iRam00e107b4) {
    FUN_00443f20(0xd359b4,param_1,param_2,0,0,0,0);
  }
  FUN_000206bc(param_1,0x88,1);
  uVar5 = (param_2 & 0xf) << 4 | 0xa0;
  FUN_0000a07c(*(undefined4 *)(iVar4 + 0x108ea20),uVar5);
  FUN_0000dc08();
  iVar1 = FUN_000206bc(param_1,0x88,1);
  if (iVar1 != 0) {
    FUN_0000a07c(*(undefined4 *)(iVar4 + 0x108ea20),uVar5);
    FUN_0000dc08();
  }
  *(undefined4 *)(iVar4 + 0x108ea48) = 1;
  FUN_0000a07c(*(undefined4 *)(iVar4 + 0x108ea24),0xa1);
  FUN_0000dc08();
  FUN_000206bc(param_1,0x80,0);
  iVar1 = FUN_005accf4(iVar4 + 0x108e8f8,1);
  uVar5 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea28));
  if (((uVar5 & 1) == 0) && (((uVar5 ^ 8) >> 3 & 1) == 0 && iVar1 == 0)) {
    FUN_0000a140(*(undefined4 *)(iVar4 + 0x108ea04),param_3,0x100);
    FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
    FUN_000206bc(param_1,0x40,1);
    if (6 < iRam00e107b4) {
      uVar2 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea28));
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea20));
      FUN_00443f20(0xd359cc,param_1,param_2,uVar2,uVar3,0,0);
    }
    return 0;
  }
  uVar2 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea08));
  if (8 < iRam00e107b4) {
    FUN_00443f20(0xd35964,param_1,param_2,uVar5,*(undefined4 *)(iVar4 + 0x108e9f8),uVar2,iVar1);
  }
  return 0xffffffff;
}

