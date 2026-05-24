/* 0x000372c8  FUN_000372c8  size=544 bytes */


undefined4 FUN_000372c8(int *param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  iVar4 = param_1[1];
  iVar3 = *param_1;
  iVar6 = *(int *)(iVar3 + 0x30);
  uVar8 = param_1[0xd];
  uVar2 = uVar8;
  if ((1 < uVar8) && (uVar8 < *(uint *)(iVar6 + 0x5c))) goto LAB_00037330;
  if (uVar8 == 0 && param_1[0xc] == 0) {
    uVar2 = *(uint *)(iVar4 + 0xc);
    param_1[7] = (uVar2 - 2) * (uint)*(ushort *)(iVar3 + 0x5e) + *(int *)(iVar3 + 0x78);
    if (*(uint *)(iVar6 + 0x6c) < uVar2) goto LAB_00037478;
  }
  else if (*(uint *)(iVar6 + 0x6c) < uVar8) {
LAB_00037478:
    uVar2 = (**(code **)(iVar6 + 0x34))(param_1,*(undefined1 *)(iVar6 + 0x54),param_1[0xc]);
  }
  if ((uVar2 < 2) || (*(uint *)(iVar6 + 0x5c) <= uVar2)) {
    param_1[0xd] = uVar2;
    return 0xffffffff;
  }
LAB_00037330:
  if ((uVar2 < (uint)param_1[8]) && (*(uint *)(iVar4 + 0xc) <= uVar2)) {
    uVar8 = uVar2 + param_2;
    uVar7 = uVar8;
    if ((uint)param_1[8] <= uVar8) {
      uVar7 = param_1[8];
      uVar8 = *(uint *)(iVar6 + 0x70);
    }
  }
  else {
    uVar5 = uVar2 + param_2;
    uVar1 = uVar2;
    if (*(uint *)(iVar6 + 0x5c) < uVar5) {
      uVar5 = *(uint *)(iVar6 + 0x5c);
    }
    do {
      uVar7 = uVar1;
      if (uVar5 <= uVar1) break;
      uVar7 = uVar1 + 1;
      uVar8 = (**(code **)(iVar6 + 0x34))(param_1,*(undefined1 *)(iVar6 + 0x54),uVar1);
      uVar1 = uVar7;
    } while (uVar7 == uVar8);
    if (param_1[0xf] == 1) {
      return 0xffffffff;
    }
  }
  param_1[0xd] = uVar8;
  param_1[0xc] = uVar7 - 1;
  param_1[7] = (uVar2 - 2) * (uint)*(ushort *)(iVar3 + 0x5e) + *(int *)(iVar3 + 0x78);
  param_1[6] = param_1[7];
  param_1[9] = (uVar7 - uVar2) * (uint)*(ushort *)(iVar3 + 0x5e);
  return 0;
}

