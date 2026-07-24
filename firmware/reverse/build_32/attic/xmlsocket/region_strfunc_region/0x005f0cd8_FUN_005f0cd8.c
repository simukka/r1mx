/* 0x005f0cd8  FUN_005f0cd8  size=2328 bytes */


/* WARNING: Removing unreachable block (ram,0x005f10d4) */
/* WARNING: Removing unreachable block (ram,0x005f0d68) */
/* WARNING: Removing unreachable block (ram,0x005f128c) */
/* WARNING: Removing unreachable block (ram,0x005f1424) */
/* WARNING: Removing unreachable block (ram,0x005f14d0) */
/* WARNING: Removing unreachable block (ram,0x005f155c) */
/* WARNING: Removing unreachable block (ram,0x005f129c) */
/* WARNING: Removing unreachable block (ram,0x005f12b0) */
/* WARNING: Removing unreachable block (ram,0x005f12b4) */
/* WARNING: Removing unreachable block (ram,0x005f12cc) */
/* WARNING: Removing unreachable block (ram,0x005f12d0) */
/* WARNING: Removing unreachable block (ram,0x005f1318) */
/* WARNING: Removing unreachable block (ram,0x005f131c) */
/* WARNING: Removing unreachable block (ram,0x005f1434) */
/* WARNING: Removing unreachable block (ram,0x005f15f4) */
/* WARNING: Removing unreachable block (ram,0x005f1448) */
/* WARNING: Removing unreachable block (ram,0x005f1460) */
/* WARNING: Removing unreachable block (ram,0x005f1464) */
/* WARNING: Removing unreachable block (ram,0x005f14ac) */
/* WARNING: Removing unreachable block (ram,0x005f14b0) */
/* WARNING: Removing unreachable block (ram,0x005f11ec) */
/* WARNING: Heritage AFTER dead removal. Example location: s0xffffff24 : 0x005f0efc */
/* WARNING: Removing unreachable block (ram,0x005f120c) */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

undefined1 * FUN_005f0cd8(undefined1 *param_1,undefined1 *param_2,undefined4 ****param_3)

{
  undefined4 ****ppppuVar1;
  uint uVar2;
  int iVar3;
  undefined1 *puVar4;
  undefined4 ****ppppuVar5;
  undefined1 *puVar6;
  uint uVar7;
  undefined1 auStack_e8 [8];
  undefined1 auStack_e0 [4];
  undefined4 ***apppuStack_dc [4];
  uint uStack_cc;
  uint uStack_c8;
  undefined1 auStack_b0 [4];
  undefined4 uStack_ac;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined1 *puStack_90;
  undefined4 uStack_8c;
  int iStack_58;
  undefined1 *puStack_44;
  uint uStack_38;
  int iStack_c;
  
  uStack_98 = 0x25710c;
  puStack_90 = auStack_e8;
  uStack_8c = 0x6014f8;
  uStack_94 = 0xe96512;
  FUN_003d1214(auStack_b0);
  uVar7 = *(uint *)(param_2 + 0x14);
  uStack_c8 = 0xf;
  apppuStack_dc[0] = (undefined4 ***)((uint)apppuStack_dc[0] & 0xffffff);
  uStack_cc = 0;
  if (auStack_e0 == param_2) {
    iStack_58 = -1;
    uStack_c8 = 0xf;
    uStack_cc = 0;
    if (-uVar7 != -1) {
      iStack_58 = -uVar7;
    }
    if (iStack_58 != 0) {
      uStack_ac = 0xffffffff;
      FUN_0039acb0((int)apppuStack_dc + uVar7,(int)apppuStack_dc + iStack_58 + uVar7,
                   -iStack_58 - uVar7);
      uStack_cc = uStack_cc - iStack_58;
      ppppuVar1 = apppuStack_dc;
      if (0xf < uStack_c8) {
        ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
      }
      *(undefined1 *)((int)ppppuVar1 + uStack_cc) = 0;
    }
  }
  else {
    uStack_ac = 0xffffffff;
    iVar3 = FUN_005f0030(auStack_e0,uVar7,0);
    if (iVar3 != 0) {
      ppppuVar1 = apppuStack_dc;
      if (0xf < uStack_c8) {
        ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
      }
      puVar4 = param_2 + 4;
      if (0xf < *(uint *)(param_2 + 0x18)) {
        puVar4 = *(undefined1 **)(param_2 + 4);
      }
      FUN_0039ac74(ppppuVar1,puVar4,uVar7);
      ppppuVar1 = apppuStack_dc;
      if (0xf < uStack_c8) {
        ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
      }
      uStack_cc = uVar7;
      *(undefined1 *)((int)ppppuVar1 + uVar7) = 0;
    }
  }
  uStack_38 = FUN_0039b0f0(param_3);
  ppppuVar1 = apppuStack_dc;
  if (0xf < uStack_c8) {
    ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
  }
  if (ppppuVar1 <= param_3) {
    ppppuVar1 = apppuStack_dc;
    if (0xf < uStack_c8) {
      ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
    }
    if (param_3 < (undefined4 ****)((int)ppppuVar1 + uStack_cc)) {
      ppppuVar1 = apppuStack_dc;
      if (0xf < uStack_c8) {
        ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
      }
      uVar7 = (int)param_3 - (int)ppppuVar1;
      if (uStack_cc < uVar7) {
        uStack_ac = 1;
        FUN_00250ea4(auStack_e0);
      }
      puStack_44 = auStack_e0;
      if (uStack_cc - uVar7 < uStack_38) {
        uStack_38 = uStack_cc - uVar7;
      }
      if (~uStack_cc <= uStack_38) {
        uStack_ac = 1;
        FUN_002513e0(puStack_44);
      }
      if (uStack_38 != 0) {
        uVar2 = uStack_cc + uStack_38;
        if (0xfffffffe < uVar2) {
          uStack_ac = 1;
          FUN_002513e0(puStack_44);
        }
        if (uStack_c8 < uVar2) {
          uStack_ac = 1;
          FUN_005e7bb8(puStack_44,uVar2,uStack_cc);
        }
        else if (uVar2 == 0) {
          ppppuVar1 = apppuStack_dc;
          if (0xf < uStack_c8) {
            ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
          }
          uStack_cc = 0;
          *(undefined1 *)ppppuVar1 = 0;
        }
        if (uVar2 != 0) {
          ppppuVar1 = apppuStack_dc;
          if (0xf < uStack_c8) {
            ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
          }
          ppppuVar5 = apppuStack_dc;
          if (0xf < uStack_c8) {
            ppppuVar5 = (undefined4 ****)apppuStack_dc[0];
          }
          FUN_0039ac74((undefined1 *)((int)ppppuVar1 + uStack_cc),
                       (undefined1 *)((int)ppppuVar5 + uVar7),uStack_38);
          ppppuVar1 = apppuStack_dc;
          if (0xf < uStack_c8) {
            ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
          }
          *(undefined1 *)((int)ppppuVar1 + uVar2) = 0;
          uStack_cc = uVar2;
        }
      }
      goto LAB_005f109c;
    }
  }
  if (~uStack_cc <= uStack_38) {
    uStack_ac = 1;
    FUN_002513e0(auStack_e0);
  }
  if (uStack_38 != 0) {
    uVar7 = uStack_cc + uStack_38;
    if (0xfffffffe < uVar7) {
      uStack_ac = 1;
      FUN_002513e0(auStack_e0);
    }
    if (uStack_c8 < uVar7) {
      uStack_ac = 1;
      FUN_005e7bb8(auStack_e0,uVar7,uStack_cc);
    }
    else if (uVar7 == 0) {
      ppppuVar1 = apppuStack_dc;
      if (0xf < uStack_c8) {
        ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
      }
      uStack_cc = 0;
      *(undefined1 *)ppppuVar1 = 0;
    }
    if (uVar7 != 0) {
      ppppuVar1 = apppuStack_dc;
      if (0xf < uStack_c8) {
        ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
      }
      FUN_0039ac74((undefined1 *)((int)ppppuVar1 + uStack_cc),param_3,uStack_38);
      ppppuVar1 = apppuStack_dc;
      if (0xf < uStack_c8) {
        ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
      }
      uStack_cc = uVar7;
      *(undefined1 *)((int)ppppuVar1 + uVar7) = 0;
    }
  }
LAB_005f109c:
  uVar7 = uStack_cc;
  param_1[4] = 0;
  *(undefined4 *)(param_1 + 0x14) = 0;
  *(undefined4 *)(param_1 + 0x18) = 0xf;
  if (param_1 == auStack_e0) {
    iStack_c = -1;
    if (*(int *)(param_1 + 0x14) - uStack_cc != -1) {
      iStack_c = *(int *)(param_1 + 0x14) - uStack_cc;
    }
    if (iStack_c != 0) {
      puVar4 = param_1 + 4;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        puVar4 = *(undefined1 **)(param_1 + 4);
      }
      puVar6 = param_1 + 4;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        puVar6 = *(undefined1 **)(param_1 + 4);
      }
      uStack_ac = 1;
      FUN_0039acb0(puVar4 + uStack_cc,puVar6 + iStack_c + uStack_cc,
                   (*(int *)(param_1 + 0x14) - uStack_cc) - iStack_c);
      iVar3 = *(int *)(param_1 + 0x14);
      puVar4 = param_1 + 4;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        puVar4 = *(undefined1 **)(param_1 + 4);
      }
      *(int *)(param_1 + 0x14) = iVar3 - iStack_c;
      puVar4[iVar3 - iStack_c] = 0;
    }
  }
  else {
    uStack_ac = 1;
    iVar3 = FUN_005f0030(param_1,uStack_cc,0);
    if (iVar3 != 0) {
      puVar4 = param_1 + 4;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        puVar4 = *(undefined1 **)(param_1 + 4);
      }
      ppppuVar1 = apppuStack_dc;
      if (0xf < uStack_c8) {
        ppppuVar1 = (undefined4 ****)apppuStack_dc[0];
      }
      FUN_0039ac74(puVar4,ppppuVar1,uVar7);
      puVar4 = param_1 + 4;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        puVar4 = *(undefined1 **)(param_1 + 4);
      }
      *(uint *)(param_1 + 0x14) = uVar7;
      puVar4[uVar7] = 0;
    }
  }
  FUN_005e75e4(auStack_e0,1,0);
  FUN_003d12b8(auStack_b0);
  return param_1;
}

