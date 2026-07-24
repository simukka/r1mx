/* 0x0011ebc4  FUN_0011ebc4  size=5656 bytes */


/* WARNING: Removing unreachable block (ram,0x0011fb20) */
/* WARNING: Removing unreachable block (ram,0x0011f790) */
/* WARNING: Removing unreachable block (ram,0x0011f5e8) */
/* WARNING: Removing unreachable block (ram,0x0011f08c) */
/* WARNING: Removing unreachable block (ram,0x0011f058) */
/* WARNING: Removing unreachable block (ram,0x0011f810) */
/* WARNING: Removing unreachable block (ram,0x001200e8) */
/* WARNING: Removing unreachable block (ram,0x0011f4d8) */
/* WARNING: Removing unreachable block (ram,0x0012032c) */
/* WARNING: Removing unreachable block (ram,0x00120134) */
/* WARNING: Heritage AFTER dead removal. Example location: s0xfffffdd4 : 0x001202c0 */
/* WARNING: Removing unreachable block (ram,0x00120298) */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

void FUN_0011ebc4(int *param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  undefined4 ****ppppuVar7;
  undefined4 ****ppppuVar8;
  int iVar9;
  int *piVar10;
  uint uVar11;
  undefined1 auStack_238 [8];
  int iStack_230;
  undefined4 ***apppuStack_22c [4];
  uint uStack_21c;
  uint uStack_218;
  undefined1 auStack_210 [4];
  undefined4 ***apppuStack_20c [4];
  uint uStack_1fc;
  uint uStack_1f8;
  undefined4 uStack_1f0;
  undefined4 ***apppuStack_1ec [4];
  uint uStack_1dc;
  uint uStack_1d8;
  undefined4 *puStack_1c0;
  int iStack_1bc;
  undefined1 auStack_1b0 [4];
  int *piStack_1ac;
  undefined1 auStack_1a0 [32];
  undefined1 auStack_180 [4];
  undefined4 ***apppuStack_17c [4];
  uint uStack_16c;
  uint uStack_168;
  undefined1 auStack_160 [4];
  undefined4 uStack_15c;
  undefined4 uStack_148;
  undefined4 uStack_144;
  undefined1 *puStack_140;
  undefined4 uStack_13c;
  uint uStack_120;
  undefined4 *puStack_11c;
  uint uStack_110;
  undefined4 *puStack_10c;
  uint uStack_fc;
  uint uStack_dc;
  uint uStack_cc;
  uint uStack_b4;
  int iStack_94;
  int iStack_88;
  uint uStack_84;
  undefined4 *puStack_74;
  uint uStack_68;
  uint uStack_1c;
  
  uStack_148 = 0x25710c;
  puStack_140 = auStack_238;
  uStack_144 = 0xe98f31;
  uStack_13c = 0x12f93c;
  FUN_003d1214(auStack_160);
  uVar4 = uRam00ea0654;
  if (*(char *)((int)param_1 + 0x75) == '\0') {
    iVar9 = *(int *)(param_2 + 4);
    if (uRam00ea0658 < 0x10) {
      puStack_11c = &uRam00ea0644;
    }
    else {
      puStack_11c = uRam00ea0644;
    }
    uStack_120 = *(uint *)(iVar9 + 0x14);
    if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
      uStack_120 = *(uint *)(iVar9 + 0x14);
    }
    uVar2 = 0;
    if (uStack_120 != 0) {
      iVar3 = iVar9 + 4;
      if (0xf < *(uint *)(iVar9 + 0x18)) {
        iVar3 = *(int *)(iVar9 + 4);
      }
      uVar2 = uRam00ea0654;
      if (uStack_120 < uRam00ea0654) {
        uVar2 = uStack_120;
      }
      uVar2 = FUN_0039ac2c(iVar3,puStack_11c,uVar2);
    }
    if ((uVar2 == 0) && (uVar2 = (uint)(uStack_120 != uVar4), uStack_120 < uVar4)) {
      uVar2 = 0xffffffff;
    }
    if ((uVar2 != 0) && (param_1[0x20] != 2)) {
      uStack_15c = 0xffffffff;
      FUN_001157fc(param_1,param_2);
      goto LAB_0011ed28;
    }
  }
  uVar4 = uRam00ea0638;
  iVar9 = *(int *)(param_2 + 4);
  if (uRam00ea063c < 0x10) {
    puStack_10c = &uRam00ea0628;
  }
  else {
    puStack_10c = uRam00ea0628;
  }
  uStack_110 = *(uint *)(iVar9 + 0x14);
  if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
    uStack_110 = *(uint *)(iVar9 + 0x14);
  }
  uVar2 = 0;
  if (uStack_110 != 0) {
    iVar3 = iVar9 + 4;
    if (0xf < *(uint *)(iVar9 + 0x18)) {
      iVar3 = *(int *)(iVar9 + 4);
    }
    uVar2 = uRam00ea0638;
    if (uStack_110 < uRam00ea0638) {
      uVar2 = uStack_110;
    }
    uVar2 = FUN_0039ac2c(iVar3,puStack_10c,uVar2);
  }
  uVar11 = uRam00ea06c4;
  if ((uVar2 == 0) && (uVar2 = (uint)(uStack_110 != uVar4), uStack_110 < uVar4)) {
    uVar2 = 0xffffffff;
  }
  if (uVar2 == 0) {
    iVar9 = *(int *)(param_2 + 8);
    uStack_15c = 0xffffffff;
    FUN_005ea3bc(&uStack_1f0,0xd4bbc0);
    piVar10 = param_1 + 0x26;
    uStack_fc = 0xffffffff;
    if (*(uint *)(iVar9 + 0x14) != 0xffffffff) {
      uStack_fc = *(uint *)(iVar9 + 0x14);
    }
    if (~uStack_1dc <= uStack_fc) {
      uStack_15c = 0xc;
      FUN_002513e0(&uStack_1f0);
    }
    if (uStack_fc != 0) {
      uVar4 = uStack_1dc + uStack_fc;
      if (0xfffffffe < uVar4) {
        uStack_15c = 0xc;
        FUN_002513e0(&uStack_1f0);
      }
      if (uStack_1d8 < uVar4) {
        uStack_15c = 0xc;
        FUN_005e7bb8(&uStack_1f0,uVar4,uStack_1dc);
      }
      else if (uVar4 == 0) {
        ppppuVar7 = apppuStack_1ec;
        if (0xf < uStack_1d8) {
          ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
        }
        uStack_1dc = 0;
        *(undefined1 *)ppppuVar7 = 0;
      }
      if (uVar4 != 0) {
        ppppuVar7 = apppuStack_1ec;
        if (0xf < uStack_1d8) {
          ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
        }
        iVar3 = iVar9 + 4;
        if (0xf < *(uint *)(iVar9 + 0x18)) {
          iVar3 = *(int *)(iVar9 + 4);
        }
        FUN_0039ac74((undefined1 *)((int)ppppuVar7 + uStack_1dc),iVar3,uStack_fc);
        ppppuVar7 = apppuStack_1ec;
        if (0xf < uStack_1d8) {
          ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
        }
        uStack_1dc = uVar4;
        *(undefined1 *)((int)ppppuVar7 + uVar4) = 0;
      }
    }
    uStack_15c = 0xc;
    FUN_005f4290(auStack_210,&uStack_1f0);
    FUN_005e8e00(&uStack_1f0);
    uStack_15c = 0xb;
    FUN_005f0cd8(&iStack_230,auStack_210,0xd4b690);
    if (piVar10 == &iStack_230) {
      uStack_15c = 10;
      FUN_005f3808(piVar10,uStack_21c,0xffffffff);
      FUN_005f3808(piVar10,0,0);
    }
    else {
      uStack_15c = 10;
      iVar9 = FUN_005f0030(piVar10,uStack_21c,0);
      if (iVar9 != 0) {
        piVar10 = param_1 + 0x27;
        if (0xf < (uint)param_1[0x2c]) {
          piVar10 = (int *)param_1[0x27];
        }
        ppppuVar7 = apppuStack_22c;
        if (0xf < uStack_218) {
          ppppuVar7 = (undefined4 ****)apppuStack_22c[0];
        }
        FUN_0039ac74(piVar10,ppppuVar7,uStack_21c);
        piVar10 = param_1 + 0x27;
        if (0xf < (uint)param_1[0x2c]) {
          piVar10 = (int *)param_1[0x27];
        }
        param_1[0x2b] = uStack_21c;
        *(undefined1 *)((int)piVar10 + uStack_21c) = 0;
      }
    }
    FUN_005e8e00(&iStack_230);
    FUN_005e8e00(auStack_210);
    uStack_15c = 0xffffffff;
    (**(code **)(*param_1 + 0xc))(param_1,param_1 + 0x26);
  }
  else {
    iVar9 = *(int *)(param_2 + 4);
    puVar6 = &uRam00ea06b4;
    if (0xf < uRam00ea06c8) {
      puVar6 = uRam00ea06b4;
    }
    uStack_dc = *(uint *)(iVar9 + 0x14);
    if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
      uStack_dc = *(uint *)(iVar9 + 0x14);
    }
    uVar4 = 0;
    if (uStack_dc != 0) {
      iVar3 = iVar9 + 4;
      if (0xf < *(uint *)(iVar9 + 0x18)) {
        iVar3 = *(int *)(iVar9 + 4);
      }
      uVar4 = uRam00ea06c4;
      if (uStack_dc < uRam00ea06c4) {
        uVar4 = uStack_dc;
      }
      uVar4 = FUN_0039ac2c(iVar3,puVar6,uVar4);
    }
    uVar1 = uRam00ea06a8;
    uVar2 = uRam00e9f544;
    if ((uVar4 == 0) && (uVar4 = (uint)(uStack_dc != uVar11), uStack_dc < uVar11)) {
      uVar4 = 0xffffffff;
    }
    if (uVar4 != 0) {
      iVar9 = *(int *)(param_2 + 4);
      puVar6 = &uRam00ea0698;
      if (0xf < uRam00ea06ac) {
        puVar6 = uRam00ea0698;
      }
      uStack_b4 = *(uint *)(iVar9 + 0x14);
      if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
        uStack_b4 = *(uint *)(iVar9 + 0x14);
      }
      uVar4 = 0;
      if (uStack_b4 != 0) {
        iVar3 = iVar9 + 4;
        if (0xf < *(uint *)(iVar9 + 0x18)) {
          iVar3 = *(int *)(iVar9 + 4);
        }
        uVar4 = uRam00ea06a8;
        if (uStack_b4 < uRam00ea06a8) {
          uVar4 = uStack_b4;
        }
        uVar4 = FUN_0039ac2c(iVar3,puVar6,uVar4);
      }
      uVar2 = uRam00ea0654;
      if ((uVar4 == 0) && (uVar4 = (uint)(uStack_b4 != uVar1), uStack_b4 < uVar1)) {
        uVar4 = 0xffffffff;
      }
      if (uVar4 == 0) {
        iVar9 = *(int *)(param_2 + 8);
        uVar11 = *(uint *)(iVar9 + 0x14);
        uVar2 = FUN_0039b0f0(uRam00d95178);
        uVar4 = 0;
        if (uVar11 != 0) {
          iVar3 = iVar9 + 4;
          if (0xf < *(uint *)(iVar9 + 0x18)) {
            iVar3 = *(int *)(iVar9 + 4);
          }
          uVar4 = uVar2;
          if (uVar11 < uVar2) {
            uVar4 = uVar11;
          }
          uVar4 = FUN_0039ac2c(iVar3,uRam00d95178,uVar4);
        }
        if ((uVar4 == 0) && (uVar4 = (uint)(uVar11 != uVar2), uVar11 < uVar2)) {
          uVar4 = 0xffffffff;
        }
        if (uVar4 == 0) {
          uStack_1d8 = 0xf;
          uStack_1dc = 0;
          apppuStack_1ec[0] = (undefined4 ***)((uint)apppuStack_1ec[0] & 0xffffff);
          uStack_15c = 9;
          iVar9 = FUN_0005e890();
          puStack_1c0 = (undefined4 *)0x0;
          iStack_1bc = iVar9;
          if (*(int *)(iVar9 + 0x70) != 0) {
            uStack_15c = 9;
            FUN_001d9204(*(int *)(iVar9 + 0x70),0xffffffff);
          }
          puStack_1c0 = (undefined4 *)**(undefined4 **)(iVar9 + 0x4c);
          uStack_15c = 8;
          FUN_00115394(param_1);
          while (puStack_1c0 != *(undefined4 **)(iStack_1bc + 0x4c)) {
            uStack_15c = 8;
            uVar5 = FUN_0005e890();
            FUN_005f4290(auStack_210,puStack_1c0 + 2);
            uStack_15c = 7;
            FUN_005e817c(auStack_1b0,uVar5,auStack_210);
            FUN_005e8e00(auStack_210);
            uStack_15c = 6;
            iVar9 = FUN_0011c098(param_1,auStack_1b0);
            if (iVar9 != 0) {
              FUN_005ea3bc(auStack_210,0xddda54);
              piVar10 = piStack_1ac;
              iStack_94 = -1;
              if (piStack_1ac != (int *)0x0) {
                uStack_15c = 5;
                iStack_88 = -1;
                FUN_005f0cd8(auStack_1a0,0xea06e8,0xdb8b44);
                uStack_15c = 4;
                FUN_005f4290(auStack_180,auStack_1a0);
                uStack_84 = 0xffffffff;
                if (uStack_1fc != 0xffffffff) {
                  uStack_84 = uStack_1fc;
                }
                if (~uStack_16c <= uStack_84) {
                  uStack_15c = 3;
                  FUN_002513e0(auStack_180);
                }
                if (uStack_84 != 0) {
                  uVar4 = uStack_16c + uStack_84;
                  if (0xfffffffe < uVar4) {
                    uStack_15c = 3;
                    FUN_002513e0(auStack_180);
                  }
                  if (uStack_168 < uVar4) {
                    uStack_15c = 3;
                    FUN_005e7bb8(auStack_180,uVar4,uStack_16c);
                  }
                  else if (uVar4 == 0) {
                    ppppuVar7 = apppuStack_17c;
                    if (0xf < uStack_168) {
                      ppppuVar7 = (undefined4 ****)apppuStack_17c[0];
                    }
                    uStack_16c = 0;
                    *(undefined1 *)ppppuVar7 = 0;
                  }
                  if (uVar4 != 0) {
                    ppppuVar7 = apppuStack_17c;
                    if (0xf < uStack_168) {
                      ppppuVar7 = (undefined4 ****)apppuStack_17c[0];
                    }
                    ppppuVar8 = apppuStack_20c;
                    if (0xf < uStack_1f8) {
                      ppppuVar8 = (undefined4 ****)apppuStack_20c[0];
                    }
                    FUN_0039ac74((undefined1 *)((int)ppppuVar7 + uStack_16c),ppppuVar8,uStack_84);
                    ppppuVar7 = apppuStack_17c;
                    if (0xf < uStack_168) {
                      ppppuVar7 = (undefined4 ****)apppuStack_17c[0];
                    }
                    uStack_16c = uVar4;
                    *(undefined1 *)((int)ppppuVar7 + uVar4) = 0;
                  }
                }
                uStack_15c = 3;
                FUN_005f4290(&iStack_230,auStack_180);
                FUN_005e8e00(auStack_180);
                FUN_005e8e00(auStack_1a0);
                iVar9 = -1;
                if (piVar10[5] != 0) {
                  uStack_15c = 2;
                  iVar9 = FUN_001d9204(piVar10[5],0xffffffff);
                }
                if (iVar9 == 0) {
                  uVar4 = 0xdeadbeef;
                  if (uStack_21c != 0) {
                    iVar9 = (uStack_21c >> 4) + 1;
                    uVar2 = 0;
                    do {
                      ppppuVar7 = (undefined4 ****)apppuStack_22c[0];
                      if (uStack_218 < 0x10) {
                        ppppuVar7 = apppuStack_22c;
                      }
                      uVar11 = uVar2 + iVar9;
                      uVar4 = uVar4 + *(byte *)((int)ppppuVar7 + uVar2);
                      uVar2 = uVar11;
                    } while (uVar11 <= uStack_21c - iVar9);
                  }
                  uVar4 = uVar4 & piVar10[0x21];
                  if ((uint)piVar10[0x22] <= uVar4) {
                    uVar4 = (uVar4 - ((uint)piVar10[0x21] >> 1)) - 1;
                  }
                  for (puStack_74 = *(undefined4 **)(piVar10[0x1e] + uVar4 * 4); uVar2 = uStack_21c,
                      puStack_74 != *(undefined4 **)(piVar10[0x1e] + (uVar4 + 1) * 4);
                      puStack_74 = (undefined4 *)*puStack_74) {
                    ppppuVar7 = apppuStack_22c;
                    if (0xf < uStack_218) {
                      ppppuVar7 = (undefined4 ****)apppuStack_22c[0];
                    }
                    uStack_68 = puStack_74[7];
                    if ((uint)puStack_74[7] < (uint)puStack_74[7]) {
                      uStack_68 = puStack_74[7];
                    }
                    uVar11 = 0;
                    if (uStack_68 != 0) {
                      puVar6 = puStack_74 + 3;
                      if (0xf < (uint)puStack_74[8]) {
                        puVar6 = (undefined4 *)puStack_74[3];
                      }
                      uVar11 = uStack_21c;
                      if (uStack_68 < uStack_21c) {
                        uVar11 = uStack_68;
                      }
                      uVar11 = FUN_0039ac2c(puVar6,ppppuVar7,uVar11);
                    }
                    uVar1 = uStack_21c;
                    if ((uVar11 == 0) && (uVar11 = (uint)(uStack_68 != uVar2), uStack_68 < uVar2)) {
                      uVar11 = 0xffffffff;
                    }
                    if (-1 < (int)uVar11) {
                      puVar6 = puStack_74 + 3;
                      if (0xf < (uint)puStack_74[8]) {
                        puVar6 = (undefined4 *)puStack_74[3];
                      }
                      uVar2 = puStack_74[7];
                      uVar4 = 0;
                      if (uStack_21c != 0) {
                        ppppuVar7 = apppuStack_22c;
                        if (0xf < uStack_218) {
                          ppppuVar7 = (undefined4 ****)apppuStack_22c[0];
                        }
                        uVar4 = uVar2;
                        if (uStack_21c < uVar2) {
                          uVar4 = uStack_21c;
                        }
                        uVar4 = FUN_0039ac2c(ppppuVar7,puVar6,uVar4);
                      }
                      if ((uVar4 == 0) && (uVar4 = (uint)(uVar1 != uVar2), uVar1 < uVar2)) {
                        uVar4 = 0xffffffff;
                      }
                      if ((int)uVar4 < 0) {
                        puStack_74 = (undefined4 *)piVar10[0x1b];
                      }
                      goto LAB_00120100;
                    }
                  }
                  puStack_74 = (undefined4 *)piVar10[0x1b];
LAB_00120100:
                  if (puStack_74 != (undefined4 *)piVar10[0x1b]) {
                    uVar4 = puStack_74[0xe];
                    if (&uStack_1f0 == puStack_74 + 9) {
                      uStack_15c = 2;
                      FUN_005f3808(&uStack_1f0,uVar4,0xffffffff);
                      FUN_005f3808(&uStack_1f0,0,0);
                    }
                    else {
                      uStack_15c = 2;
                      iVar9 = FUN_005f0030(&uStack_1f0,uVar4,0);
                      if (iVar9 != 0) {
                        ppppuVar7 = apppuStack_1ec;
                        if (0xf < uStack_1d8) {
                          ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
                        }
                        puVar6 = puStack_74 + 10;
                        if (0xf < (uint)puStack_74[0xf]) {
                          puVar6 = (undefined4 *)puStack_74[10];
                        }
                        FUN_0039ac74(ppppuVar7,puVar6,uVar4);
                        ppppuVar7 = apppuStack_1ec;
                        if (0xf < uStack_1d8) {
                          ppppuVar7 = (undefined4 ****)apppuStack_1ec[0];
                        }
                        *(undefined1 *)((int)ppppuVar7 + uVar4) = 0;
                        uStack_1dc = uVar4;
                      }
                    }
                    iStack_88 = 0;
                  }
                  if (piVar10[5] != 0) {
                    uStack_15c = 2;
                    FUN_001d92bc();
                  }
                }
                FUN_005e8e00(&iStack_230);
                iStack_94 = iStack_88;
              }
              FUN_005e8e00(auStack_210);
              if (iStack_94 != 0) {
                iVar9 = -1;
                if ((piStack_1ac != (int *)0x0) && ((code *)piStack_1ac[0x13] != reset_vector)) {
                  uStack_15c = 6;
                  iVar9 = (*(code *)piStack_1ac[0x13])
                                    (piStack_1ac + 10,piStack_1ac[0x12],param_1 + 0x26);
                }
                if (iVar9 == 0) {
                  uStack_15c = 6;
                  (**(code **)(*param_1 + 8))(param_1,param_1 + 0x26);
                  FUN_005f3808(param_1 + 0x26,0,0xffffffff);
                }
              }
            }
            piVar10 = piStack_1ac;
            puStack_1c0 = (undefined4 *)*puStack_1c0;
            if (piStack_1ac != (int *)0x0) {
              iVar9 = -1;
              if (piStack_1ac[3] != 0) {
                uStack_15c = 8;
                iVar9 = FUN_001d9204(piStack_1ac[3],0xffffffff);
              }
              if ((iVar9 == 0) && (*piVar10 = *piVar10 + -1, piVar10[3] != 0)) {
                uStack_15c = 8;
                FUN_001d92bc();
              }
            }
          }
          uStack_15c = 8;
          FUN_00115000(param_1);
          if (*(int *)(iStack_1bc + 0x70) != 0) {
            uStack_15c = 9;
            FUN_001d92bc();
          }
          FUN_005e8e00(&uStack_1f0);
        }
        else {
          uStack_15c = 0xffffffff;
          uVar5 = FUN_0005e890();
          FUN_005e817c(auStack_1b0,uVar5,*(undefined4 *)(param_2 + 8));
          uStack_15c = 1;
          iVar9 = FUN_0011c098(param_1,auStack_1b0);
          if (iVar9 != 0) {
            FUN_00115394(param_1);
            iVar9 = -1;
            if ((piStack_1ac != (int *)0x0) && ((code *)piStack_1ac[0x13] != reset_vector)) {
              uStack_15c = 1;
              iVar9 = (*(code *)piStack_1ac[0x13])
                                (piStack_1ac + 10,piStack_1ac[0x12],param_1 + 0x26);
            }
            if (iVar9 == 0) {
              uStack_15c = 1;
              (**(code **)(*param_1 + 8))(param_1,param_1 + 0x26);
              FUN_005f3808(param_1 + 0x26,0,0xffffffff);
            }
            uStack_15c = 1;
            FUN_00115000(param_1);
          }
          if (piStack_1ac != (int *)0x0) {
            iVar9 = -1;
            if (piStack_1ac[3] != 0) {
              uStack_15c = 0xffffffff;
              iVar9 = FUN_001d9204(piStack_1ac[3],0xffffffff);
            }
            if ((iVar9 == 0) && (*piStack_1ac = *piStack_1ac + -1, piStack_1ac[3] != 0)) {
              uStack_15c = 0xffffffff;
              FUN_001d92bc();
            }
          }
        }
      }
      else {
        iVar9 = *(int *)(param_2 + 4);
        puVar6 = &uRam00ea0644;
        if (0xf < uRam00ea0658) {
          puVar6 = uRam00ea0644;
        }
        uStack_1c = *(uint *)(iVar9 + 0x14);
        if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
          uStack_1c = *(uint *)(iVar9 + 0x14);
        }
        uVar4 = 0;
        if (uStack_1c != 0) {
          iVar3 = iVar9 + 4;
          if (0xf < *(uint *)(iVar9 + 0x18)) {
            iVar3 = *(int *)(iVar9 + 4);
          }
          uVar4 = uRam00ea0654;
          if (uStack_1c < uRam00ea0654) {
            uVar4 = uStack_1c;
          }
          uVar4 = FUN_0039ac2c(iVar3,puVar6,uVar4);
        }
        if ((uVar4 == 0) && (uVar4 = (uint)(uStack_1c != uVar2), uStack_1c < uVar2)) {
          uVar4 = 0xffffffff;
        }
        if (uVar4 == 0) {
          iVar9 = *(int *)(param_2 + 8);
          uVar11 = *(uint *)(iVar9 + 0x14);
          uVar2 = FUN_0039b0f0(uRam00d9517c);
          uVar4 = 0;
          if (uVar11 != 0) {
            iVar3 = iVar9 + 4;
            if (0xf < *(uint *)(iVar9 + 0x18)) {
              iVar3 = *(int *)(iVar9 + 4);
            }
            uVar4 = uVar2;
            if (uVar11 < uVar2) {
              uVar4 = uVar11;
            }
            uVar4 = FUN_0039ac2c(iVar3,uRam00d9517c,uVar4);
          }
          if ((uVar4 == 0) && (uVar4 = (uint)(uVar11 != uVar2), uVar11 < uVar2)) {
            uVar4 = 0xffffffff;
          }
          *(bool *)(param_1 + 0x1e) = uVar4 == 0;
        }
        else {
          piVar10 = param_1 + 0x10;
          if (0xf < (uint)param_1[0x15]) {
            piVar10 = (int *)param_1[0x10];
          }
          uStack_15c = 0xffffffff;
          FUN_0005e784(0,3,8,0xd4b744,0x662588,0x218,0xd4bbcc,piVar10);
        }
      }
LAB_0011ed28:
      FUN_003d12b8(auStack_160);
      return;
    }
    iVar9 = *(int *)(param_2 + 8);
    puVar6 = &uRam00e9f534;
    if (0xf < uRam00e9f548) {
      puVar6 = uRam00e9f534;
    }
    uStack_cc = *(uint *)(iVar9 + 0x14);
    if (*(uint *)(iVar9 + 0x14) < *(uint *)(iVar9 + 0x14)) {
      uStack_cc = *(uint *)(iVar9 + 0x14);
    }
    uVar4 = 0;
    if (uStack_cc != 0) {
      iVar3 = iVar9 + 4;
      if (0xf < *(uint *)(iVar9 + 0x18)) {
        iVar3 = *(int *)(iVar9 + 4);
      }
      uVar4 = uRam00e9f544;
      if (uStack_cc < uRam00e9f544) {
        uVar4 = uStack_cc;
      }
      uVar4 = FUN_0039ac2c(iVar3,puVar6,uVar4);
    }
    if ((uVar4 == 0) && (uVar4 = (uint)(uStack_cc != uVar2), uStack_cc < uVar2)) {
      uVar4 = 0xffffffff;
    }
    if (uVar4 == 0) {
      if (param_1[0x21] != 2) goto LAB_0011ed28;
      uStack_15c = 0xffffffff;
      uVar5 = FUN_0005e8a8();
      FUN_000b382c(uVar5,param_1 + 0x26);
      (**(code **)(*param_1 + 0xc))(param_1,param_1 + 0x26);
    }
    else {
      uStack_15c = 0xffffffff;
      FUN_0011d16c(param_1,param_1 + 0x26,*(undefined4 *)(param_2 + 8));
      (**(code **)(*param_1 + 0xc))(param_1,param_1 + 0x26);
    }
  }
  FUN_005f3808(param_1 + 0x26,0,0xffffffff);
  FUN_003d12b8(auStack_160);
  return;
}

