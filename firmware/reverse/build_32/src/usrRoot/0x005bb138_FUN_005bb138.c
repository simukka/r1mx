/* 0x005bb138  FUN_005bb138  size=500 bytes */


uint * FUN_005bb138(int param_1)

{
  uint uVar1;
  uint uVar2;
  bool bVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  uint *puVar7;
  uint *puVar8;
  uint uVar9;
  uint uVar10;
  uint *puVar11;
  uint uVar12;
  uint uVar13;
  
  puVar11 = *(uint **)(param_1 + 0x8c);
  uVar13 = *puVar11;
  puVar8 = puVar11 + 1;
  if ((uVar13 & 0xf0000000) == 0x40000000) {
    uVar12 = *(uint *)(param_1 + 0x88);
    uVar1 = uVar13 >> 0x1a;
    if ((uVar13 & 0x2000000) == 0) {
      puVar4 = (uint *)(uVar13 & 0x3fffffc);
    }
    else {
      puVar4 = (uint *)(uVar13 & 0xfffffffc | 0xf6000000);
    }
    uVar9 = uVar13 >> 0x15 & 0x1f;
    if ((uVar13 & 0x8000) == 0) {
      puVar7 = (uint *)(uVar13 & 0xfffc);
    }
    else {
      puVar7 = (uint *)(uVar13 & 0xfffffffc | 0xffff0000);
    }
    uVar2 = uVar9 >> 4;
    uVar6 = uVar9 >> 3 & 1;
    uVar5 = uVar9 >> 2 & 1;
    uVar10 = uVar9 >> 1 & 1;
    uVar9 = *(uint *)(param_1 + 0x90) >> (0x1f - (uVar13 >> 0x10 & 0x1f) & 0x3f) & 1;
    if (uVar1 == 0x10) {
      if (uVar5 == 0) {
        uVar12 = uVar12 - 1;
      }
      bVar3 = false;
      if ((uVar5 == 1) || ((uVar12 != 0) != (uVar10 != 0))) {
        if ((uVar2 == 1) || (uVar6 == uVar9)) {
          bVar3 = true;
        }
        if ((bVar3) && (puVar8 = puVar7, (uVar13 & 2) != 1)) {
          puVar8 = (uint *)((int)puVar7 + (int)puVar11);
        }
      }
    }
    else if (uVar1 == 0x12) {
      puVar8 = puVar4;
      if ((uVar13 & 2) != 1) {
        puVar8 = (uint *)((int)puVar4 + (int)puVar11);
      }
    }
    else if (uVar1 == 0x13) {
      if ((uVar13 & 0xfc0007fe) == 0x4c000420) {
        if (uVar5 == 0) {
          uVar12 = uVar12 - 1;
        }
        bVar3 = false;
        if (uVar5 != 1) {
          if (uVar12 != 0) {
            return puVar8;
          }
          if (uVar10 != 0) {
            return puVar8;
          }
        }
        if ((uVar2 == 1) || (uVar6 == uVar9)) {
          bVar3 = true;
        }
        if (bVar3) {
          puVar8 = (uint *)(uVar12 & 0xfffffffc);
        }
      }
      if ((uVar13 & 0xfc0007fe) == 0x4c000020) {
        if (uVar5 == 0) {
          uVar12 = uVar12 - 1;
        }
        bVar3 = false;
        if ((uVar5 == 1) || ((uVar12 == 0 && (uVar10 == 0)))) {
          if ((uVar2 == 1) || (uVar6 == uVar9)) {
            bVar3 = true;
          }
          if (bVar3) {
            puVar8 = (uint *)(*(uint *)(param_1 + 0x84) & 0xfffffffc);
          }
        }
      }
    }
  }
  return puVar8;
}

