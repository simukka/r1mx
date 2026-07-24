/* 0x00024734  FUN_00024734  size=1576 bytes */


undefined4
FUN_00024734(int param_1,uint param_2,uint param_3,uint param_4,uint param_5,undefined4 param_6,
            uint param_7,int param_8)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  byte bVar6;
  undefined4 uVar5;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  
  iVar2 = param_1 * 0x430;
  iVar1 = (param_1 + param_2) * 0x14;
  iVar10 = iVar2 + 0x108e6a0;
  iVar9 = param_2 * 600 + iVar10;
  iVar8 = 0;
  if (6 < iRam00e107b4) {
    FUN_00443f20(0xd3605c,param_1,param_2,param_3,param_4,param_5,param_6);
  }
  if (6 < iRam00e107b4) {
    FUN_00443f20(0xd358ec,param_7,param_8,0,0,0,0);
  }
  *(int *)(iVar9 + 0x250) = *(int *)(iVar9 + 0x250) + 1;
  do {
    uVar3 = FUN_0000a6ec(param_1,0);
    if ((uVar3 & 0xf0f) != 0x103) {
      return 0xffffffff;
    }
    if (6 < iRam00e107b4) {
      FUN_00443f20(0xd36004,iVar8,0,0,0,0,0);
    }
    iVar4 = FUN_0002447c(param_1,param_6,*(int *)(iVar1 + 0xe0bb30) * param_7,param_8,
                         *(undefined4 *)(iVar9 + 0x220),*(undefined4 *)(iVar9 + 0x224));
    if (iVar4 == -1) {
      uVar5 = FUN_00021e90(param_1,param_2,param_3,param_4,param_5,param_6,param_7,param_8);
      return uVar5;
    }
    FUN_00020390(param_1,0x40);
    bVar6 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea40));
    if (param_2 == 0) {
      bVar6 = bVar6 | 0x26;
    }
    else {
      bVar6 = bVar6 | 0x46;
    }
    FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea40),bVar6);
    if (*(short *)(iVar9 + 0x208) == 0) {
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea0c),*(uint *)(iVar1 + 0xe0bb34) & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea14),param_5 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea18),param_3 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea1c),param_3 >> 8 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea10),param_7 & 0xff);
      if (*(short *)(iVar9 + 0x206) != 0) {
        uVar5 = *(undefined4 *)(iVar2 + 0x108ea20);
        uVar3 = (param_2 & 0xf) << 4 | param_4 & 0xf;
        goto LAB_000248f8;
      }
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea20),(param_2 & 0xf) << 4 | param_4 & 0xf | 0xa0);
      *(undefined4 *)(iVar2 + 0x108ea48) = 1;
      *(undefined4 *)(iVar2 + 0x108ea4c) = 1;
      if (param_8 == 1) goto LAB_00024b18;
LAB_00024914:
      if (pcRam00e29374 != reset_vector) {
        (*pcRam00e29374)(1,param_6,*(int *)(iVar1 + 0xe0bb30) * param_7);
      }
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea3c),8);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea24),
                   (-(*(short *)(iVar9 + 0x208) == 0) & 0xa3U) + 0x25);
      uVar5 = *(undefined4 *)(iVar2 + 0x108ea3c);
      uVar7 = 9;
    }
    else {
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea0c),0);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea10),param_7 >> 8 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea14),param_3 >> 0x18);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea18),0);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea1c),0);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea0c),0);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea10),param_7 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea14),param_3 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea18),param_3 >> 8 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea1c),param_3 >> 0x10 & 0xff);
      uVar5 = *(undefined4 *)(iVar2 + 0x108ea20);
      uVar3 = (param_2 & 0xf) << 4;
LAB_000248f8:
      FUN_0000a07c(uVar5,uVar3 | 0xe0);
      *(undefined4 *)(iVar2 + 0x108ea48) = 1;
      *(undefined4 *)(iVar2 + 0x108ea4c) = 1;
      if (param_8 != 1) goto LAB_00024914;
LAB_00024b18:
      if (pcRam00e29370 != reset_vector) {
        (*pcRam00e29370)(1,param_6,*(int *)(iVar1 + 0xe0bb30) * param_7);
      }
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea3c),0);
      FUN_0000a07c(*(undefined4 *)(iVar2 + 0x108ea24),
                   (-(*(short *)(iVar9 + 0x208) == 0) & 0x95U) + 0x35);
      uVar5 = *(undefined4 *)(iVar2 + 0x108ea3c);
      uVar7 = 1;
    }
    FUN_0000a07c(uVar5,uVar7);
    iVar4 = FUN_005accf4(iVar2 + 0x108e8f8,*(undefined4 *)(iVar2 + 0x108e9d8));
    if (iRam00e9c3b8 == 0x55) {
      FUN_00443f20(0xd36090,1,2,3,4,5,6);
      FUN_0000daac(iVar10,0);
      return 0xffffffff;
    }
    if (iRam00e9c3bc == 0x55) {
      FUN_00443f20(0xd360b0,1,2,3,4,5,6);
      FUN_0000daac(iVar10,1);
      return 0xffffffff;
    }
    if (((*(uint *)(iVar2 + 0x108e9fc) & 2) == 0) && (iVar4 != -1)) {
      uVar3 = FUN_0000a6ec(param_1,1);
      if (((uVar3 & 0x3fa0000) == 0) && ((*(uint *)(iVar2 + 0x108e9f8) & 1) == 0)) {
        if (6 < iRam00e107b4) {
          FUN_00443f20(0xd360d0,1,2,3,4,5,6);
          return 0;
        }
        return 0;
      }
      *(int *)(iVar9 + 0x254) = *(int *)(iVar9 + 0x254) + 1;
      uVar5 = FUN_0000a6ec(param_1,1);
      FUN_0000a658(param_1,1,uVar5);
    }
    FUN_0001fbe8(param_1);
    uVar5 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea08));
    uVar7 = FUN_0000a05c(*(undefined4 *)(iVar2 + 0x108ea2c));
    if (6 < iRam00e107b4) {
      FUN_00443f20(0xd36014,*(undefined4 *)(iVar2 + 0x108e9f8),uVar7,
                   *(undefined4 *)(iVar2 + 0x108e9fc),iVar4,uVar5,6);
    }
    iVar8 = iVar8 + 1;
    if (iRam00e107c4 <= iVar8) {
      return 0xffffffff;
    }
  } while( true );
}

