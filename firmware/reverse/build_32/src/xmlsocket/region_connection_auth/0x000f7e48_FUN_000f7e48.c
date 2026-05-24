/* 0x000f7e48  FUN_000f7e48  size=2592 bytes */


/* WARNING: Removing unreachable block (ram,0x000f8210) */
/* WARNING: Removing unreachable block (ram,0x000f80a0) */
/* WARNING: Removing unreachable block (ram,0x000f85e4) */
/* WARNING: Removing unreachable block (ram,0x000f87e4) */
/* WARNING: Removing unreachable block (ram,0x000f88f8) */
/* WARNING: Removing unreachable block (ram,0x000f8884) */
/* WARNING: Removing unreachable block (ram,0x000f85f4) */
/* WARNING: Removing unreachable block (ram,0x000f8608) */
/* WARNING: Removing unreachable block (ram,0x000f860c) */
/* WARNING: Removing unreachable block (ram,0x000f8624) */
/* WARNING: Removing unreachable block (ram,0x000f8628) */
/* WARNING: Removing unreachable block (ram,0x000f8670) */
/* WARNING: Removing unreachable block (ram,0x000f8674) */
/* WARNING: Removing unreachable block (ram,0x000f87f4) */
/* WARNING: Removing unreachable block (ram,0x000f8808) */
/* WARNING: Removing unreachable block (ram,0x000f880c) */
/* WARNING: Removing unreachable block (ram,0x000f8824) */
/* WARNING: Removing unreachable block (ram,0x000f8828) */
/* WARNING: Removing unreachable block (ram,0x000f8870) */
/* WARNING: Removing unreachable block (ram,0x000f8874) */
/* WARNING: Heritage AFTER dead removal. Example location: s0xfffffee4 : 0x000f8114 */
/* WARNING: Removing unreachable block (ram,0x000f8568) */
/* WARNING: Removing unreachable block (ram,0x000f8548) */
/* WARNING: Removing unreachable block (ram,0x000f873c) */
/* WARNING: Removing unreachable block (ram,0x000f874c) */
/* WARNING: Removing unreachable block (ram,0x000f8750) */
/* WARNING: Removing unreachable block (ram,0x000f876c) */
/* WARNING: Removing unreachable block (ram,0x000f8770) */
/* WARNING: Removing unreachable block (ram,0x000f87b8) */
/* WARNING: Removing unreachable block (ram,0x000f87bc) */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

undefined4 FUN_000f7e48(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined4 ****ppppuVar3;
  int *piVar4;
  undefined4 ****ppppuVar5;
  int *piVar6;
  undefined1 auStack_138 [8];
  int iStack_130;
  undefined4 ***pppuStack_12c;
  int iStack_120;
  undefined4 ***apppuStack_11c [4];
  uint uStack_10c;
  uint uStack_108;
  int iStack_100;
  undefined4 ***apppuStack_fc [4];
  uint uStack_ec;
  uint uStack_e8;
  int iStack_d0;
  undefined4 ***pppuStack_cc;
  int iStack_c0;
  undefined4 ***pppuStack_bc;
  undefined1 auStack_b0 [4];
  undefined4 uStack_ac;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined1 *puStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_78;
  uint uStack_64;
  int iStack_44;
  int iStack_c;
  
  uStack_98 = 0x25710c;
  puStack_90 = auStack_138;
  uStack_94 = 0xe9861c;
  uStack_8c = 0x1083e0;
  FUN_003d1214(auStack_b0);
  uStack_ac = 0xffffffff;
  iVar2 = FUN_0035980c(0);
  uStack_78 = 0;
  if (iVar2 == 0) {
    pppuStack_12c = ppppuRam00661874;
    iStack_130 = iRam00661870;
    FUN_005ea3bc(&iStack_100,0xd76720);
    uStack_64 = 0xffffffff;
    if (*(uint *)(param_1 + 0x38) != 0xffffffff) {
      uStack_64 = *(uint *)(param_1 + 0x38);
    }
    if (~uStack_ec <= uStack_64) {
      uStack_ac = 3;
      FUN_002513e0(&iStack_100);
    }
    if (uStack_64 != 0) {
      uVar1 = uStack_ec + uStack_64;
      if (0xfffffffe < uVar1) {
        uStack_ac = 3;
        FUN_002513e0(&iStack_100);
      }
      if (uStack_e8 < uVar1) {
        uStack_ac = 3;
        FUN_005e7bb8(&iStack_100,uVar1,uStack_ec);
      }
      else if (uVar1 == 0) {
        ppppuVar3 = apppuStack_fc;
        if (0xf < uStack_e8) {
          ppppuVar3 = (undefined4 ****)apppuStack_fc[0];
        }
        uStack_ec = 0;
        *(undefined1 *)ppppuVar3 = 0;
      }
      if (uVar1 != 0) {
        ppppuVar3 = apppuStack_fc;
        if (0xf < uStack_e8) {
          ppppuVar3 = (undefined4 ****)apppuStack_fc[0];
        }
        iVar2 = param_1 + 0x28;
        if (0xf < *(uint *)(param_1 + 0x3c)) {
          iVar2 = *(int *)(param_1 + 0x28);
        }
        FUN_0039ac74((undefined1 *)((int)ppppuVar3 + uStack_ec),iVar2,uStack_64);
        ppppuVar3 = apppuStack_fc;
        if (0xf < uStack_e8) {
          ppppuVar3 = (undefined4 ****)apppuStack_fc[0];
        }
        uStack_ec = uVar1;
        *(undefined1 *)((int)ppppuVar3 + uVar1) = 0;
      }
    }
    uVar1 = uStack_ec;
    apppuStack_11c[0] = (undefined4 ***)((uint)apppuStack_11c[0] & 0xffffff);
    uStack_10c = 0;
    uStack_108 = 0xf;
    if (&iStack_120 == &iStack_100) {
      iStack_44 = -1;
      uStack_108 = 0xf;
      uStack_10c = 0;
      if (-uStack_ec != -1) {
        iStack_44 = -uStack_ec;
      }
      if (iStack_44 != 0) {
        uStack_ac = 3;
        FUN_0039acb0((int)apppuStack_11c + uStack_ec,(int)apppuStack_11c + iStack_44 + uStack_ec,
                     -iStack_44 - uStack_ec);
        uStack_10c = uStack_10c - iStack_44;
        ppppuVar3 = apppuStack_11c;
        if (0xf < uStack_108) {
          ppppuVar3 = (undefined4 ****)apppuStack_11c[0];
        }
        *(undefined1 *)((int)ppppuVar3 + uStack_10c) = 0;
      }
    }
    else {
      if (0xfffffffe < uStack_ec) {
        uStack_ac = 3;
        FUN_002513e0(&iStack_120);
      }
      if (uStack_108 < uVar1) {
        uStack_ac = 3;
        FUN_005e7bb8(&iStack_120,uVar1,uStack_10c);
      }
      else if (uVar1 == 0) {
        ppppuVar3 = apppuStack_11c;
        if (0xf < uStack_108) {
          ppppuVar3 = (undefined4 ****)apppuStack_11c[0];
        }
        uStack_10c = 0;
        *(undefined1 *)ppppuVar3 = 0;
      }
      if (uVar1 != 0) {
        ppppuVar3 = apppuStack_11c;
        if (0xf < uStack_108) {
          ppppuVar3 = (undefined4 ****)apppuStack_11c[0];
        }
        ppppuVar5 = apppuStack_fc;
        if (0xf < uStack_e8) {
          ppppuVar5 = (undefined4 ****)apppuStack_fc[0];
        }
        FUN_0039ac74(ppppuVar3,ppppuVar5,uVar1);
        ppppuVar3 = apppuStack_11c;
        if (0xf < uStack_108) {
          ppppuVar3 = (undefined4 ****)apppuStack_11c[0];
        }
        uStack_10c = uVar1;
        *(undefined1 *)((int)ppppuVar3 + uVar1) = 0;
      }
    }
    if (0xf < uStack_e8) {
      FUN_00245c34(apppuStack_fc[0]);
    }
    iStack_100 = iStack_130;
    uStack_ac = 2;
    apppuStack_fc[0] = pppuStack_12c;
    uStack_e8 = 0xf;
    uStack_ec = 0;
    piVar4 = (int *)FUN_00248640(0x2c);
    uVar1 = uStack_10c;
    pppuStack_bc = apppuStack_fc[0];
    pppuStack_cc = apppuStack_fc[0];
    iStack_c0 = iStack_100;
    iStack_d0 = iStack_100;
    *piVar4 = param_1;
    piVar6 = piVar4 + 4;
    piVar4[1] = iStack_100;
    piVar4[2] = (int)apppuStack_fc[0];
    piVar4[9] = 0;
    piVar4[10] = 0xf;
    *(undefined1 *)(piVar4 + 5) = 0;
    piVar4[3] = 0;
    if (piVar6 == &iStack_120) {
    }
    else {
      if (0xfffffffe < uStack_10c) {
        uStack_ac = 1;
        FUN_002513e0(piVar6);
      }
      if ((uint)piVar4[10] < uVar1) {
        uStack_ac = 1;
        FUN_005e7bb8(piVar6,uVar1,piVar4[9]);
      }
      else if (uVar1 == 0) {
        piVar6 = piVar4 + 5;
        if (0xf < (uint)piVar4[10]) {
          piVar6 = (int *)piVar4[5];
        }
        piVar4[9] = 0;
        *(undefined1 *)piVar6 = 0;
      }
      if (uVar1 != 0) {
        piVar6 = piVar4 + 5;
        if (0xf < (uint)piVar4[10]) {
          piVar6 = (int *)piVar4[5];
        }
        ppppuVar3 = apppuStack_11c;
        if (0xf < uStack_108) {
          ppppuVar3 = (undefined4 ****)apppuStack_11c[0];
        }
        FUN_0039ac74(piVar6,ppppuVar3,uVar1);
        piVar6 = piVar4 + 5;
        if (0xf < (uint)piVar4[10]) {
          piVar6 = (int *)piVar4[5];
        }
        piVar4[9] = uVar1;
        *(undefined1 *)((int)piVar6 + uVar1) = 0;
      }
    }
    piVar6 = piVar4 + 5;
    if (0xf < (uint)piVar4[10]) {
      piVar6 = (int *)piVar4[5];
    }
    uStack_ac = 2;
    iVar2 = FUN_001d9580(piVar6,0x4b,0x4000,0x61fe1c);
    if (0xf < uStack_108) {
      FUN_00245c34(apppuStack_11c[0]);
    }
    apppuStack_11c[0] = (undefined4 ***)((uint)apppuStack_11c[0] & 0xffffff);
    uStack_108 = 0xf;
    uStack_10c = 0;
    *(int *)(param_1 + 0x70) = iVar2;
    if (iVar2 == 0) {
      iVar2 = param_1 + 0x28;
      if (0xf < *(uint *)(param_1 + 0x3c)) {
        iVar2 = *(int *)(param_1 + 0x28);
      }
      uStack_ac = 0xffffffff;
      FUN_0005e784(0,3,0x1f,0xd49df8,0x661860,0x36b,0xd4a03c,iVar2);
    }
    else {
      *(undefined1 *)(param_1 + 0x60) = 1;
      *(undefined1 *)(param_1 + 0x6c) = 1;
    }
    uStack_ac = 0xffffffff;
    FUN_001d9a58(500);
    uStack_78 = FUN_000f63f0(param_1,8,0);
  }
  else {
    iStack_c = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iStack_c = *(int *)(param_1 + 0x28);
    }
    uStack_ac = 0xffffffff;
    FUN_00442920();
    FUN_0005e784(0,3,0x1f,0xd49df8,0x661860,0x378,0xd4a010,iStack_c);
  }
  FUN_003d12b8(auStack_b0);
  return uStack_78;
}

