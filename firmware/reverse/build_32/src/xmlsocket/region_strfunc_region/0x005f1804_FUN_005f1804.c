/* 0x005f1804  FUN_005f1804  size=2028 bytes */


/* WARNING: Removing unreachable block (ram,0x005f1de0) */
/* WARNING: Removing unreachable block (ram,0x005f1ecc) */
/* WARNING: Removing unreachable block (ram,0x005f201c) */
/* WARNING: Removing unreachable block (ram,0x005f1edc) */
/* WARNING: Removing unreachable block (ram,0x005f1ef0) */
/* WARNING: Removing unreachable block (ram,0x005f1ef4) */
/* WARNING: Removing unreachable block (ram,0x005f1f0c) */
/* WARNING: Removing unreachable block (ram,0x005f1f10) */
/* WARNING: Removing unreachable block (ram,0x005f1f58) */
/* WARNING: Removing unreachable block (ram,0x005f1f5c) */
/* WARNING: Removing unreachable block (ram,0x005f1e24) */
/* WARNING: Removing unreachable block (ram,0x005f1e34) */
/* WARNING: Removing unreachable block (ram,0x005f1e38) */
/* WARNING: Removing unreachable block (ram,0x005f1e54) */
/* WARNING: Removing unreachable block (ram,0x005f1e58) */
/* WARNING: Removing unreachable block (ram,0x005f1ea0) */
/* WARNING: Removing unreachable block (ram,0x005f1ea4) */

void FUN_005f1804(int param_1,int *param_2,uint param_3,undefined4 *param_4)

{
  bool bVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 ***pppuVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  byte in_cr0;
  byte in_cr1;
  byte unaff_cr2;
  byte unaff_cr3;
  byte unaff_cr4;
  byte in_cr5;
  byte in_cr6;
  byte in_cr7;
  undefined1 auStack_128 [8];
  undefined4 uStack_120;
  undefined4 uStack_11c;
  undefined4 uStack_118;
  undefined4 uStack_114;
  undefined4 uStack_110;
  undefined4 **appuStack_10c [4];
  int iStack_fc;
  uint uStack_f8;
  undefined1 auStack_e0 [4];
  undefined1 auStack_dc [4];
  undefined4 uStack_d8;
  undefined4 uStack_c4;
  undefined4 uStack_c0;
  undefined1 *puStack_bc;
  undefined4 uStack_b8;
  undefined1 *puStack_b4;
  undefined1 *puStack_b0;
  int iStack_a8;
  undefined4 *puStack_a4;
  uint uStack_a0;
  undefined4 *puStack_9c;
  uint uStack_98;
  undefined4 *puStack_94;
  undefined4 *puStack_90;
  undefined4 *puStack_8c;
  undefined4 *puStack_88;
  int iStack_84;
  undefined4 uStack_7c;
  undefined4 *puStack_78;
  undefined4 uStack_74;
  int iStack_6c;
  int iStack_68;
  undefined4 *puStack_64;
  int iStack_60;
  undefined4 *puStack_5c;
  uint uStack_4c;
  
  puStack_b0 = &stack0xfffffed0;
  puStack_a4 = (undefined4 *)*param_2;
  uStack_4c = (uint)(in_cr0 & 0xf) << 0x1c | (uint)(in_cr1 & 0xf) << 0x18 |
              (uint)(unaff_cr2 & 0xf) << 0x14 | (uint)(unaff_cr3 & 0xf) << 0x10 |
              (uint)(unaff_cr4 & 0xf) << 0xc | (uint)(in_cr5 & 0xf) << 8 | (uint)(in_cr6 & 0xf) << 4
              | (uint)(in_cr7 & 0xf);
  uStack_b8 = 0x601fdc;
  puStack_bc = auStack_128;
  uStack_c4 = 0x25710c;
  uStack_c0 = 0xe9656c;
  puStack_b4 = (undefined1 *)register0x00000004;
  iStack_a8 = param_1;
  uStack_a0 = param_3;
  puStack_9c = param_4;
  FUN_003d1214(auStack_dc);
  uStack_120 = *puStack_9c;
  uStack_114 = puStack_9c[3];
  uStack_118 = puStack_9c[2];
  uStack_11c = puStack_9c[1];
  uStack_98 = 0;
  if (*(int *)(iStack_a8 + 4) != 0) {
    uStack_98 = *(int *)(iStack_a8 + 0xc) - *(int *)(iStack_a8 + 4) >> 4;
  }
  if (uStack_a0 == 0) goto LAB_005f1aec;
  if (*(int *)(iStack_a8 + 4) == 0) {
    if (uStack_a0 < 0x10000000) goto LAB_005f193c;
LAB_005f1b78:
    uStack_d8 = 0xffffffff;
    FUN_005ea3bc(&uStack_110,0xd3d538);
    puStack_94 = (undefined4 *)FUN_00245cd8(0x20);
    puStack_88 = puStack_94 + 1;
    *puStack_94 = 0xe08170;
    puStack_94[6] = 0;
    *(undefined1 *)(puStack_94 + 2) = 0;
    iStack_84 = iStack_fc;
    puStack_94[7] = 0xf;
    puStack_90 = puStack_94;
    puStack_8c = puStack_94;
    if (puStack_88 == &uStack_110) {
      uStack_7c = 0;
      uStack_74 = 0;
      puStack_78 = puStack_88;
    }
    else {
      uStack_d8 = 1;
      iVar3 = FUN_005f0030(puStack_88,iStack_fc,0);
      if (iVar3 != 0) {
        puVar5 = puStack_88 + 1;
        if (0xf < (uint)puStack_88[6]) {
          puVar5 = (undefined4 *)puStack_88[1];
        }
        pppuVar6 = appuStack_10c;
        if (0xf < uStack_f8) {
          pppuVar6 = (undefined4 ***)appuStack_10c[0];
        }
        FUN_0039ac74(puVar5,pppuVar6,iStack_84);
        puVar5 = puStack_88 + 1;
        if (0xf < (uint)puStack_88[6]) {
          puVar5 = (undefined4 *)puStack_88[1];
        }
        puStack_88[5] = iStack_84;
        *(undefined1 *)((int)puVar5 + iStack_84) = 0;
      }
    }
    *puStack_90 = 0xe081b8;
    FUN_005e75e4(&uStack_110,1,0);
    uStack_d8 = 0xffffffff;
    FUN_00247c78(puStack_94,0xe08788,0x5f7a14);
  }
  else {
    if (0xfffffffU - (*(int *)(iStack_a8 + 8) - *(int *)(iStack_a8 + 4) >> 4) < uStack_a0)
    goto LAB_005f1b78;
LAB_005f193c:
    iVar3 = 0;
    if (*(int *)(iStack_a8 + 4) != 0) {
      iVar3 = *(int *)(iStack_a8 + 8) - *(int *)(iStack_a8 + 4) >> 4;
    }
    if (uStack_98 < iVar3 + uStack_a0) {
      bVar1 = 0xfffffff - (uStack_98 >> 1) < uStack_98;
      uStack_98 = (uStack_98 >> 1) + uStack_98;
      if (bVar1) {
        uStack_98 = 0;
      }
      iVar3 = 0;
      if (*(int *)(iStack_a8 + 4) != 0) {
        iVar3 = *(int *)(iStack_a8 + 8) - *(int *)(iStack_a8 + 4) >> 4;
      }
      if (uStack_98 < iVar3 + uStack_a0) {
        iVar3 = 0;
        if (*(int *)(iStack_a8 + 4) != 0) {
          iVar3 = *(int *)(iStack_a8 + 8) - *(int *)(iStack_a8 + 4) >> 4;
        }
        uStack_98 = iVar3 + uStack_a0;
      }
      uStack_d8 = 0xffffffff;
      iStack_6c = FUN_00248640(uStack_98 << 4);
      iStack_68 = FUN_005f1708(*(undefined4 *)(iStack_a8 + 4),puStack_a4,iStack_6c,iStack_a8,
                               auStack_e0);
      FUN_005f1618(iStack_68,uStack_a0,&uStack_120,iStack_a8,auStack_e0);
      FUN_005f1708(puStack_a4,*(undefined4 *)(iStack_a8 + 8),uStack_a0 * 0x10 + iStack_68,iStack_a8,
                   auStack_e0);
      iVar3 = 0;
      if (*(int *)(iStack_a8 + 4) != 0) {
        iVar3 = *(int *)(iStack_a8 + 8) - *(int *)(iStack_a8 + 4) >> 4;
      }
      iVar7 = *(int *)(iStack_a8 + 4);
      uStack_a0 = uStack_a0 + iVar3;
      if (iVar7 != 0) {
        for (; iVar7 != *(int *)(iStack_a8 + 8); iVar7 = iVar7 + 0x10) {
        }
        FUN_00245c34(*(undefined4 *)(iStack_a8 + 4));
      }
      *(int *)(iStack_a8 + 4) = iStack_6c;
      *(uint *)(iStack_a8 + 0xc) = uStack_98 * 0x10 + iStack_6c;
      *(uint *)(iStack_a8 + 8) = uStack_a0 * 0x10 + iStack_6c;
      goto LAB_005f1aec;
    }
  }
  puStack_64 = *(undefined4 **)(iStack_a8 + 8);
  if ((uint)((int)puStack_64 - (int)puStack_a4 >> 4) < uStack_a0) {
    iStack_60 = uStack_a0 * 0x10;
    FUN_005f1708(puStack_a4,puStack_64,puStack_a4 + uStack_a0 * 4,iStack_a8,auStack_e0);
    FUN_005f1618(*(int *)(iStack_a8 + 8),
                 uStack_a0 - (*(int *)(iStack_a8 + 8) - (int)puStack_a4 >> 4),&uStack_120,iStack_a8,
                 auStack_e0);
    iVar3 = *(int *)(iStack_a8 + 8) + iStack_60;
    *(int *)(iStack_a8 + 8) = iVar3;
    for (puVar5 = puStack_a4; puVar5 != (undefined4 *)(iVar3 - iStack_60); puVar5 = puVar5 + 4) {
      *puVar5 = uStack_120;
      puVar5[1] = uStack_11c;
      puVar5[2] = uStack_118;
      puVar5[3] = uStack_114;
    }
  }
  else {
    puStack_5c = puStack_64 + uStack_a0 * -4;
    uVar4 = FUN_005f1708(puStack_5c,puStack_64,puStack_64,iStack_a8,auStack_e0);
    *(undefined4 *)(iStack_a8 + 8) = uVar4;
    puVar5 = puStack_64;
    puVar2 = puStack_5c;
    while (puStack_a4 != puVar2) {
      uVar4 = puVar2[-3];
      uVar8 = puVar2[-2];
      uVar9 = puVar2[-1];
      puVar5[-4] = puVar2[-4];
      puVar5[-3] = uVar4;
      puVar5[-2] = uVar8;
      puVar5[-1] = uVar9;
      puVar5 = puVar5 + -4;
      puVar2 = puVar2 + -4;
    }
    for (puVar5 = puStack_a4; puVar5 != puStack_a4 + uStack_a0 * 4; puVar5 = puVar5 + 4) {
      *puVar5 = uStack_120;
      puVar5[1] = uStack_11c;
      puVar5[2] = uStack_118;
      puVar5[3] = uStack_114;
    }
  }
LAB_005f1aec:
  FUN_003d12b8(auStack_dc);
  return;
}

