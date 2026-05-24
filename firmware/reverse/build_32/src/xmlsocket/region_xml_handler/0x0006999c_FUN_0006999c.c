/* 0x0006999c  FUN_0006999c  size=1720 bytes */


/* WARNING: Removing unreachable block (ram,0x00069cb8) */
/* WARNING: Removing unreachable block (ram,0x00069ff0) */
/* WARNING: Removing unreachable block (ram,0x00069cd4) */
/* WARNING: Removing unreachable block (ram,0x0006a004) */
/* WARNING: Removing unreachable block (ram,0x00069ce8) */
/* WARNING: Removing unreachable block (ram,0x00069fb0) */
/* WARNING: Removing unreachable block (ram,0x00069fc8) */
/* WARNING: Removing unreachable block (ram,0x00069fcc) */
/* WARNING: Removing unreachable block (ram,0x00069cf4) */
/* WARNING: Removing unreachable block (ram,0x00069d00) */
/* WARNING: Removing unreachable block (ram,0x00069d14) */
/* WARNING: Removing unreachable block (ram,0x00069d18) */
/* WARNING: Removing unreachable block (ram,0x00069d2c) */
/* WARNING: Removing unreachable block (ram,0x00069d30) */
/* WARNING: Heritage AFTER dead removal. Example location: s0xffffff44 : 0x00069e40 */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

undefined4 FUN_0006999c(int param_1,undefined4 param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  undefined4 ***pppuVar5;
  undefined4 ***pppuVar6;
  bool bVar8;
  undefined4 uVar7;
  uint uVar9;
  undefined1 auStack_c8 [8];
  undefined1 auStack_c0 [4];
  undefined4 **appuStack_bc [4];
  uint uStack_ac;
  uint uStack_a8;
  undefined1 auStack_a0 [4];
  undefined4 uStack_9c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined1 *puStack_80;
  undefined4 uStack_7c;
  uint uStack_1c;
  
  uStack_88 = 0x25710c;
  puStack_80 = auStack_c8;
  uStack_84 = 0xe969fa;
  uStack_7c = 0x79f38;
  FUN_003d1214(auStack_a0);
  FUN_005e8e80(auStack_c0);
  uVar9 = *(uint *)(param_1 + 0x58);
  uVar2 = FUN_0039b0f0(uRam00d94d2c);
  uVar3 = 0;
  if (uVar9 != 0) {
    iVar4 = param_1 + 0x48;
    if (0xf < *(uint *)(param_1 + 0x5c)) {
      iVar4 = *(int *)(param_1 + 0x48);
    }
    uVar3 = uVar2;
    if (uVar9 < uVar2) {
      uVar3 = uVar9;
    }
    uVar3 = FUN_0039ac2c(iVar4,uRam00d94d2c,uVar3);
  }
  if ((uVar3 == 0) && (uVar3 = (uint)(uVar9 != uVar2), uVar9 < uVar2)) {
    uVar3 = 0xffffffff;
  }
  if (uVar3 != 0) {
    uVar2 = *(uint *)(param_1 + 0x58);
    uVar9 = FUN_0039b0f0(uRam00d94d30);
    uVar3 = 0;
    if (uVar2 != 0) {
      iVar4 = param_1 + 0x48;
      if (0xf < *(uint *)(param_1 + 0x5c)) {
        iVar4 = *(int *)(param_1 + 0x48);
      }
      uVar3 = uVar9;
      if (uVar2 < uVar9) {
        uVar3 = uVar2;
      }
      uVar3 = FUN_0039ac2c(iVar4,uRam00d94d30,uVar3);
    }
    if ((uVar3 == 0) && (uVar3 = (uint)(uVar2 != uVar9), uVar2 < uVar9)) {
      uVar3 = 0xffffffff;
    }
    if (uVar3 != 0) {
      FUN_005e8e00(auStack_c0);
      uVar7 = 1;
      goto LAB_00069f64;
    }
  }
  uVar7 = uRam00e10a88;
  if (*(int *)(param_1 + 0x98) == 0) {
    FUN_005e8e00(auStack_c0);
    uVar7 = 3;
    goto LAB_00069f64;
  }
  uVar9 = *(uint *)(param_1 + 0x58);
  uVar2 = FUN_0039b0f0(uRam00e10a88);
  uVar3 = 0;
  if (uVar9 != 0) {
    iVar4 = param_1 + 0x48;
    if (0xf < *(uint *)(param_1 + 0x5c)) {
      iVar4 = *(int *)(param_1 + 0x48);
    }
    uVar3 = uVar2;
    if (uVar9 < uVar2) {
      uVar3 = uVar9;
    }
    uVar3 = FUN_0039ac2c(iVar4,uVar7,uVar3);
  }
  if ((uVar3 == 0) && (uVar3 = (uint)(uVar9 != uVar2), uVar9 < uVar2)) {
    uVar3 = 0xffffffff;
  }
  uVar3 = uVar3 == 0 ^ 1;
  iVar4 = param_1 + 0x28;
  if (0xf < *(uint *)(param_1 + 0x3c)) {
    iVar4 = *(int *)(param_1 + 0x28);
  }
  iVar1 = uVar3 * 0x94;
  uStack_9c = 1;
  iVar4 = FUN_005f0668(*(undefined4 *)(iVar1 + 0xe10a7c),auStack_c0,6,iVar4);
  if (iVar4 == -1) {
    pppuVar6 = *(undefined4 ****)(iVar1 + 0xe10a9c);
    uVar2 = FUN_0039b0f0(pppuVar6);
    if (uStack_a8 < 0x10) {
      if (pppuVar6 < appuStack_bc) goto LAB_00069f98;
LAB_00069c18:
      pppuVar5 = appuStack_bc;
      if (0xf < uStack_a8) {
        pppuVar5 = (undefined4 ***)appuStack_bc[0];
      }
      bVar8 = true;
      if ((undefined4 ***)((int)pppuVar5 + uStack_ac) <= pppuVar6) goto LAB_00069f98;
    }
    else {
      if (appuStack_bc[0] <= pppuVar6) goto LAB_00069c18;
LAB_00069f98:
      bVar8 = false;
    }
    if (bVar8) {
      pppuVar5 = appuStack_bc;
      if (0xf < uStack_a8) {
        pppuVar5 = (undefined4 ***)appuStack_bc[0];
      }
      uVar9 = (int)pppuVar6 - (int)pppuVar5;
      if (uStack_ac < uVar9) {
        uStack_9c = 1;
        FUN_00250ea4(auStack_c0);
      }
      uStack_1c = uStack_ac - uVar9;
      if (uVar2 < uStack_ac - uVar9) {
        uStack_1c = uVar2;
      }
      uStack_9c = 1;
      FUN_005f3808(auStack_c0,uVar9 + uStack_1c,0xffffffff);
      FUN_005f3808(auStack_c0,0,uVar9);
    }
    else {
      uStack_9c = 1;
      iVar4 = FUN_005f0030(auStack_c0,uVar2,0);
      if (iVar4 != 0) {
        pppuVar5 = appuStack_bc;
        if (0xf < uStack_a8) {
          pppuVar5 = (undefined4 ***)appuStack_bc[0];
        }
        FUN_0039ac74(pppuVar5,pppuVar6,uVar2);
        pppuVar6 = appuStack_bc;
        if (0xf < uStack_a8) {
          pppuVar6 = (undefined4 ***)appuStack_bc[0];
        }
        uStack_ac = uVar2;
        *(undefined1 *)((int)pppuVar6 + uVar2) = 0;
      }
    }
  }
  uStack_9c = 1;
  FUN_005ea15c(param_2,param_1 + 0x84,0,0xffffffff);
  uVar7 = *(undefined4 *)(uVar3 * 0x94 + 0xe10aa8);
  uVar2 = FUN_0039b0f0(uVar7);
  uVar3 = 0;
  if (uStack_ac != 0) {
    pppuVar6 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar6 = (undefined4 ***)appuStack_bc[0];
    }
    uVar3 = uVar2;
    if (uStack_ac < uVar2) {
      uVar3 = uStack_ac;
    }
    uVar3 = FUN_0039ac2c(pppuVar6,uVar7,uVar3);
  }
  if ((uVar3 == 0) && (uVar3 = (uint)(uStack_ac != uVar2), uStack_ac < uVar2)) {
    uVar3 = 0xffffffff;
  }
  if (uVar3 != 0) {
    FUN_005e8e00(auStack_c0);
    FUN_003d12b8(auStack_a0);
    return 0;
  }
  FUN_005e8e00(auStack_c0);
  uVar7 = 2;
LAB_00069f64:
  FUN_003d12b8(auStack_a0);
  return uVar7;
}

