/* 0x00026c1c  FUN_00026c1c  size=416 bytes */


undefined4 FUN_00026c1c(int param_1)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_60 [12];
  byte **ppbStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  byte abStack_30 [4];
  byte abStack_2c [12];
  byte *apbStack_20 [5];
  
  apbStack_20[0] = abStack_30;
  if (6 < iRam00e107b4) {
    FUN_00443f20(0xd36470,*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0,0,0,0);
  }
  iVar4 = 0xb;
  auStack_60[0] = 0x25;
  iVar3 = 1;
  do {
    auStack_60[iVar3] = 0;
    iVar3 = iVar3 + 1;
    iVar4 = iVar4 + -1;
  } while (iVar4 != 0);
  ppbStack_54 = apbStack_20;
  uStack_4c = 2;
  uStack_48 = 8;
  uStack_40 = 0;
  uStack_50 = 8;
  uStack_44 = 0;
  iVar3 = FUN_00026628(param_1,auStack_60);
  uVar1 = 0xffffffff;
  if (iVar3 == 0) {
    iVar4 = 4;
    *(undefined4 *)(param_1 + 0x18) = 0;
    iVar3 = 0;
    *(undefined4 *)(param_1 + 0x1c) = 0;
    uVar2 = 0x18;
    do {
      *(uint *)(param_1 + 0x18) =
           *(int *)(param_1 + 0x18) + ((uint)abStack_30[iVar3] << (uVar2 & 0x3f));
      iVar3 = iVar3 + 1;
      uVar2 = uVar2 - 8;
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    iVar3 = 4;
    *(int *)(param_1 + 0x18) = *(int *)(param_1 + 0x18) + 1;
    iVar4 = 4;
    uVar2 = 0x18;
    *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_1 + 0x18);
    do {
      *(uint *)(param_1 + 0x1c) =
           *(int *)(param_1 + 0x1c) + ((uint)abStack_30[iVar3] << (uVar2 & 0x3f));
      iVar3 = iVar3 + 1;
      uVar2 = uVar2 - 8;
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    if (6 < iRam00e107b4) {
      FUN_00443f20(0xd36438,*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),
                   *(undefined4 *)(param_1 + 0x18),*(undefined4 *)(param_1 + 0x1c),0,0);
    }
    uVar1 = 0;
  }
  return uVar1;
}

