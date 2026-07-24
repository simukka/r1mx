/* 0x00129a80  FUN_00129a80  size=8216 bytes */


/* WARNING: Removing unreachable block (ram,0x0012b8f0) */
/* WARNING: Removing unreachable block (ram,0x0012a480) */
/* WARNING: Removing unreachable block (ram,0x0012a844) */
/* WARNING: Removing unreachable block (ram,0x0012a9d0) */
/* WARNING: Removing unreachable block (ram,0x0012a9bc) */
/* WARNING: Removing unreachable block (ram,0x0012b590) */
/* WARNING: Removing unreachable block (ram,0x0012b9b4) */
/* WARNING: Heritage AFTER dead removal. Example location: s0xfffffd84 : 0x0012b084 */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

undefined4 FUN_00129a80(int param_1)

{
  bool bVar1;
  undefined1 uVar2;
  uint uVar3;
  undefined4 ****ppppuVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  undefined4 ****ppppuVar12;
  undefined4 *puVar13;
  int *piVar14;
  undefined8 uVar15;
  undefined1 auStack_2d8 [8];
  int *apiStack_2d0 [4];
  int *apiStack_2c0 [4];
  undefined1 auStack_2b0 [4];
  int *piStack_2ac;
  undefined1 auStack_2a0 [32];
  undefined1 auStack_280 [4];
  undefined4 ***apppuStack_27c [4];
  uint uStack_26c;
  uint uStack_268;
  undefined1 auStack_260 [32];
  undefined1 auStack_240 [4];
  undefined4 ***apppuStack_23c [4];
  uint uStack_22c;
  uint uStack_228;
  undefined8 uStack_220;
  undefined1 auStack_210 [28];
  undefined1 auStack_1f4 [36];
  undefined1 auStack_1d0 [4];
  undefined4 ***apppuStack_1cc [4];
  uint uStack_1bc;
  uint uStack_1b8;
  undefined1 auStack_1b0 [16];
  undefined1 auStack_1a0 [4];
  undefined4 uStack_19c;
  undefined4 uStack_188;
  undefined4 uStack_184;
  undefined1 *puStack_180;
  undefined4 uStack_17c;
  undefined4 uStack_168;
  uint uStack_15c;
  uint uStack_138;
  uint uStack_124;
  int iStack_118;
  uint uStack_110;
  uint uStack_100;
  uint uStack_ec;
  uint uStack_d0;
  uint uStack_c0;
  uint uStack_a4;
  uint uStack_94;
  int iStack_88;
  uint uStack_80;
  int iStack_74;
  uint uStack_68;
  uint uStack_58;
  uint uStack_30;
  uint uStack_20;
  int iStack_14;
  
  uStack_188 = 0x25710c;
  puStack_180 = auStack_2d8;
  uStack_184 = 0xe99480;
  uStack_17c = 0x13a340;
  FUN_003d1214(auStack_1a0);
  piVar14 = *(int **)(param_1 + 0x38);
  uStack_168 = 0;
  if (piVar14 != (int *)0x0) {
    bVar1 = 0xf < uRam00ea09d8;
    *(int **)(param_1 + 0x30) = piVar14;
    puVar13 = &uRam00ea09c4;
    if (bVar1) {
      puVar13 = uRam00ea09c4;
    }
    uStack_19c = 0xffffffff;
    apiStack_2d0[0] = piVar14;
    apiStack_2c0[0] = piVar14;
    FUN_002264b0(apiStack_2d0,param_1 + 0x30,puVar13);
    FUN_00225e78(apiStack_2c0,apiStack_2d0);
    if ((apiStack_2c0[0] == (int *)0x0) ||
       (iVar5 = (**(code **)(*apiStack_2c0[0] + 0x2c))(), iVar5 == 0)) {
      iVar5 = 0;
    }
    else {
      iVar5 = (**(code **)(*apiStack_2c0[0] + 0x2c))();
    }
    while (iVar5 != 0) {
      uStack_19c = 0xffffffff;
      uVar6 = FUN_0005e890();
      FUN_005e817c(auStack_2b0,uVar6,*(int *)(param_1 + 0x3c) + 0x30);
      puVar13 = &uRam00ea09c4;
      if (0xf < uRam00ea09d8) {
        puVar13 = uRam00ea09c4;
      }
      uStack_19c = 0x1e;
      FUN_0005e784(3,4,0xb,0xd4bc0c,0x6627d0,0x379,0xd4bea4,puVar13);
      uVar9 = uRam00ea0830;
      puVar13 = &uRam00ea0820;
      if (0xf < uRam00ea0834) {
        puVar13 = uRam00ea0820;
      }
      uStack_15c = *(uint *)(iVar5 + 0x34);
      if (*(uint *)(iVar5 + 0x34) < *(uint *)(iVar5 + 0x34)) {
        uStack_15c = *(uint *)(iVar5 + 0x34);
      }
      uVar7 = 0;
      if (uStack_15c != 0) {
        iVar8 = iVar5 + 0x24;
        if (0xf < *(uint *)(iVar5 + 0x38)) {
          iVar8 = *(int *)(iVar5 + 0x24);
        }
        uVar7 = uRam00ea0830;
        if (uStack_15c < uRam00ea0830) {
          uVar7 = uStack_15c;
        }
        uVar7 = FUN_0039ac2c(iVar8,puVar13,uVar7);
      }
      uVar3 = uRam00e9f3d8;
      if ((uVar7 == 0) && (uVar7 = (uint)(uStack_15c != uVar9), uStack_15c < uVar9)) {
        uVar7 = 0xffffffff;
      }
      if (uVar7 == 0) {
        uStack_19c = 0x1e;
        FUN_005ea3bc(auStack_2a0,0xd3c1d0);
        piVar14 = piStack_2ac;
        if (piStack_2ac != (int *)0x0) {
          uStack_19c = 0x1d;
          FUN_005f4290(auStack_240,0xea09c0);
          uStack_138 = FUN_0039b0f0(ppppuRam00d951b8);
          ppppuVar4 = apppuStack_23c;
          if (0xf < uStack_228) {
            ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
          }
          if (ppppuRam00d951b8 < ppppuVar4) {
LAB_0012a8a0:
            bVar1 = false;
          }
          else {
            ppppuVar4 = apppuStack_23c;
            if (0xf < uStack_228) {
              ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
            }
            bVar1 = true;
            if ((undefined4 ****)((int)ppppuVar4 + uStack_22c) <= ppppuRam00d951b8)
            goto LAB_0012a8a0;
          }
          if (bVar1) {
            ppppuVar4 = apppuStack_23c;
            if (0xf < uStack_228) {
              ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
            }
            uVar9 = 0xdb8b44 - (int)ppppuVar4;
            if (uStack_22c < uVar9) {
              uStack_19c = 0x1c;
              FUN_00250ea4(auStack_240);
            }
            if (uStack_22c - uVar9 < uStack_138) {
              uStack_138 = uStack_22c - uVar9;
            }
            if (~uStack_22c <= uStack_138) {
              uStack_19c = 0x1c;
              FUN_002513e0(auStack_240);
            }
            if (uStack_138 != 0) {
              uVar7 = uStack_22c + uStack_138;
              uStack_19c = 0x1c;
              iVar8 = FUN_005f0030(auStack_240,uVar7,0);
              if (iVar8 != 0) {
                ppppuVar4 = apppuStack_23c;
                if (0xf < uStack_228) {
                  ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
                }
                ppppuVar12 = apppuStack_23c;
                if (0xf < uStack_228) {
                  ppppuVar12 = (undefined4 ****)apppuStack_23c[0];
                }
                FUN_0039ac74((int)ppppuVar4 + uStack_22c,(int)ppppuVar12 + uVar9,uStack_138);
                ppppuVar4 = apppuStack_23c;
                if (0xf < uStack_228) {
                  ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
                }
                *(undefined1 *)((int)ppppuVar4 + uVar7) = 0;
                uStack_22c = uVar7;
              }
            }
          }
          else {
            if (~uStack_22c <= uStack_138) {
              uStack_19c = 0x1c;
              FUN_002513e0(auStack_240);
            }
            if (uStack_138 != 0) {
              uVar9 = uStack_22c + uStack_138;
              uStack_19c = 0x1c;
              iVar8 = FUN_005f0030(auStack_240,uVar9,0);
              if (iVar8 != 0) {
                ppppuVar4 = apppuStack_23c;
                if (0xf < uStack_228) {
                  ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
                }
                FUN_0039ac74((int)ppppuVar4 + uStack_22c,ppppuRam00d951b8,uStack_138);
                ppppuVar4 = apppuStack_23c;
                if (0xf < uStack_228) {
                  ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
                }
                uStack_22c = uVar9;
                *(undefined1 *)((int)ppppuVar4 + uVar9) = 0;
              }
            }
          }
          uStack_19c = 0x1c;
          FUN_005f4290(auStack_260,auStack_240);
          FUN_005e8e00(auStack_240);
          uStack_19c = 0x1b;
          FUN_005f4290(auStack_240,auStack_260);
          uStack_124 = 0xffffffff;
          if (*(uint *)(iVar5 + 0x34) != 0xffffffff) {
            uStack_124 = *(uint *)(iVar5 + 0x34);
          }
          if (~uStack_22c <= uStack_124) {
            uStack_19c = 0x1a;
            FUN_002513e0(auStack_240);
          }
          if (uStack_124 != 0) {
            uVar9 = uStack_22c + uStack_124;
            uStack_19c = 0x1a;
            iVar8 = FUN_005f0030(auStack_240,uVar9,0);
            if (iVar8 != 0) {
              ppppuVar4 = apppuStack_23c;
              if (0xf < uStack_228) {
                ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
              }
              iVar8 = iVar5 + 0x24;
              if (0xf < *(uint *)(iVar5 + 0x38)) {
                iVar8 = *(int *)(iVar5 + 0x24);
              }
              FUN_0039ac74((int)ppppuVar4 + uStack_22c,iVar8,uStack_124);
              ppppuVar4 = apppuStack_23c;
              if (0xf < uStack_228) {
                ppppuVar4 = (undefined4 ****)apppuStack_23c[0];
              }
              uStack_22c = uVar9;
              *(undefined1 *)((int)ppppuVar4 + uVar9) = 0;
            }
          }
          uStack_19c = 0x1a;
          FUN_005f4290(auStack_280,auStack_240);
          FUN_005e8e00(auStack_240);
          FUN_005e8e00(auStack_260);
          iVar8 = -1;
          if (piVar14[5] != 0) {
            uStack_19c = 0x19;
            iVar8 = FUN_001d9204(piVar14[5],0xffffffff);
          }
          if (iVar8 == 0) {
            iStack_118 = FUN_00616f40(piVar14 + 0x19,auStack_280);
            if (iStack_118 == piVar14[0x1b]) {
              FUN_005e8e80(auStack_240);
              uStack_19c = 0x18;
              FUN_005f4290(auStack_210,auStack_280);
              uStack_19c = 0x17;
              FUN_005f4290(auStack_1f4,auStack_240);
              uStack_19c = 0x16;
              uVar15 = FUN_0061a308(piVar14 + 0x19,auStack_210);
              iStack_118 = (int)((ulonglong)uVar15 >> 0x20);
              uStack_220 = uVar15;
              FUN_005e8e00(auStack_1f4);
              FUN_005e8e00(auStack_210);
              FUN_005e8e00(auStack_240);
            }
            uStack_19c = 0x19;
            FUN_005ea15c(iStack_118 + 0x24,auStack_2a0,0,0xffffffff);
            FUN_00616f40(piVar14 + 0x19,auStack_280);
            if (piVar14[5] != 0) {
              uStack_19c = 0x19;
              FUN_001d92bc();
            }
          }
          FUN_005e8e00(auStack_280);
        }
        FUN_005e8e00(auStack_2a0);
        uStack_168 = 1;
        *(undefined1 *)((int)piStack_2ac + 6) = 1;
      }
      else {
        puVar13 = &uRam00e9f3c8;
        if (0xf < uRam00e9f3dc) {
          puVar13 = uRam00e9f3c8;
        }
        uStack_110 = *(uint *)(iVar5 + 0x34);
        if (*(uint *)(iVar5 + 0x34) < *(uint *)(iVar5 + 0x34)) {
          uStack_110 = *(uint *)(iVar5 + 0x34);
        }
        uVar9 = 0;
        if (uStack_110 != 0) {
          iVar8 = iVar5 + 0x24;
          if (0xf < *(uint *)(iVar5 + 0x38)) {
            iVar8 = *(int *)(iVar5 + 0x24);
          }
          uVar9 = uRam00e9f3d8;
          if (uStack_110 < uRam00e9f3d8) {
            uVar9 = uStack_110;
          }
          uVar9 = FUN_0039ac2c(iVar8,puVar13,uVar9);
        }
        uVar7 = uRam00ea07f8;
        if ((uVar9 == 0) && (uVar9 = (uint)(uStack_110 != uVar3), uStack_110 < uVar3)) {
          uVar9 = 0xffffffff;
        }
        if (uVar9 != 0) {
          puVar13 = &uRam00ea07e8;
          if (0xf < uRam00ea07fc) {
            puVar13 = uRam00ea07e8;
          }
          uStack_100 = *(uint *)(iVar5 + 0x34);
          if (*(uint *)(iVar5 + 0x34) < *(uint *)(iVar5 + 0x34)) {
            uStack_100 = *(uint *)(iVar5 + 0x34);
          }
          uVar9 = 0;
          if (uStack_100 != 0) {
            iVar8 = iVar5 + 0x24;
            if (0xf < *(uint *)(iVar5 + 0x38)) {
              iVar8 = *(int *)(iVar5 + 0x24);
            }
            uVar9 = uRam00ea07f8;
            if (uStack_100 < uRam00ea07f8) {
              uVar9 = uStack_100;
            }
            uVar9 = FUN_0039ac2c(iVar8,puVar13,uVar9);
          }
          uVar3 = uRam00ea0814;
          if ((uVar9 == 0) && (uVar9 = (uint)(uStack_100 != uVar7), uStack_100 < uVar7)) {
            uVar9 = 0xffffffff;
          }
          if (uVar9 != 0) {
            puVar13 = &uRam00ea0804;
            if (0xf < uRam00ea0818) {
              puVar13 = uRam00ea0804;
            }
            uStack_80 = *(uint *)(iVar5 + 0x34);
            if (*(uint *)(iVar5 + 0x34) < *(uint *)(iVar5 + 0x34)) {
              uStack_80 = *(uint *)(iVar5 + 0x34);
            }
            uVar9 = 0;
            if (uStack_80 != 0) {
              iVar8 = iVar5 + 0x24;
              if (0xf < *(uint *)(iVar5 + 0x38)) {
                iVar8 = *(int *)(iVar5 + 0x24);
              }
              uVar9 = uRam00ea0814;
              if (uStack_80 < uRam00ea0814) {
                uVar9 = uStack_80;
              }
              uVar9 = FUN_0039ac2c(iVar8,puVar13,uVar9);
            }
            if ((uVar9 == 0) && (uVar9 = (uint)(uStack_80 != uVar3), uStack_80 < uVar3)) {
              uVar9 = 0xffffffff;
            }
            if (uVar9 == 0) {
              uStack_19c = 0x1e;
              FUN_00190738(auStack_1b0);
              iVar8 = *(int *)(iVar5 + 0x94);
              iStack_74 = 0;
              uVar9 = uRam00ea0964;
              if (iVar8 == iVar5 + 0x44) {
                iVar8 = 0;
              }
              while (uRam00ea0964 = uVar9, iVar8 != 0) {
                puVar13 = &uRam00ea0954;
                if (0xf < uRam00ea0968) {
                  puVar13 = uRam00ea0954;
                }
                uStack_68 = *(uint *)(iVar8 + 0x28);
                if (*(uint *)(iVar8 + 0x28) < *(uint *)(iVar8 + 0x28)) {
                  uStack_68 = *(uint *)(iVar8 + 0x28);
                }
                uVar7 = 0;
                if (uStack_68 != 0) {
                  iVar10 = iVar8 + 0x18;
                  if (0xf < *(uint *)(iVar8 + 0x2c)) {
                    iVar10 = *(int *)(iVar8 + 0x18);
                  }
                  uVar7 = uVar9;
                  if (uStack_68 < uVar9) {
                    uVar7 = uStack_68;
                  }
                  uVar7 = FUN_0039ac2c(iVar10,puVar13,uVar7);
                }
                if ((uVar7 == 0) && (uVar7 = (uint)(uStack_68 != uVar9), uStack_68 < uVar9)) {
                  uVar7 = 0xffffffff;
                }
                if (uVar7 == 0) {
                  iVar10 = iVar8 + 0x34;
                  if (0xf < *(uint *)(iVar8 + 0x48)) {
                    iVar10 = *(int *)(iVar8 + 0x34);
                  }
                  uStack_19c = 9;
                  iStack_74 = FUN_001907e4(auStack_1b0,iVar10);
                  uVar9 = *(uint *)(iVar8 + 0x48);
                  *(byte *)((int)piStack_2ac + 5) = (byte)iStack_74 ^ 1;
                  iVar10 = iVar8 + 0x34;
                  if (0xf < uVar9) {
                    iVar10 = *(int *)(iVar8 + 0x34);
                  }
                  uStack_19c = 9;
                  FUN_0005e784(3,0x80,0xb,0xd4bc0c,0x6627d0,0x3a4,0xd4beb0,iVar10);
                }
                else {
                  iVar10 = iRam00d951c0 + 4;
                  if (0xf < *(uint *)(iRam00d951c0 + 0x18)) {
                    iVar10 = *(int *)(iRam00d951c0 + 4);
                  }
                  uVar9 = *(uint *)(iRam00d951c0 + 0x14);
                  uStack_58 = *(uint *)(iVar8 + 0x28);
                  if (*(uint *)(iVar8 + 0x28) < *(uint *)(iVar8 + 0x28)) {
                    uStack_58 = *(uint *)(iVar8 + 0x28);
                  }
                  uVar7 = 0;
                  if (uStack_58 != 0) {
                    iVar11 = iVar8 + 0x18;
                    if (0xf < *(uint *)(iVar8 + 0x2c)) {
                      iVar11 = *(int *)(iVar8 + 0x18);
                    }
                    uVar7 = uVar9;
                    if (uStack_58 < uVar9) {
                      uVar7 = uStack_58;
                    }
                    uVar7 = FUN_0039ac2c(iVar11,iVar10,uVar7);
                  }
                  if ((uVar7 == 0) && (uVar7 = (uint)(uStack_58 != uVar9), uStack_58 < uVar9)) {
                    uVar7 = 0xffffffff;
                  }
                  if (uVar7 == 0) {
                    iVar10 = iVar8 + 0x18;
                    if (0xf < *(uint *)(iVar8 + 0x2c)) {
                      iVar10 = *(int *)(iVar8 + 0x18);
                    }
                    uStack_19c = 9;
                    FUN_0005e784(3,0x80,0xb,0xd4bc0c,0x6627d0,0x3aa,0xd4bec0,iVar10);
                    if (iStack_74 != 0) {
                      uVar2 = *(undefined1 *)(param_1 + 2);
                      *(undefined1 *)(param_1 + 5) = 1;
                      *(int *)(param_1 + 0x44) = iVar8;
                      *(undefined1 *)(param_1 + 2) = 0;
                      FUN_00128b90(param_1);
                      *(undefined1 *)(param_1 + 2) = uVar2;
                    }
                  }
                }
                uStack_19c = 9;
                iVar8 = FUN_00225d68(iVar8);
                uVar9 = uRam00ea0964;
              }
              uStack_19c = 0x1e;
              uStack_168 = 1;
              FUN_00190774(auStack_1b0);
            }
            else {
              uStack_19c = 0x1e;
              FUN_005ea3bc(auStack_1d0,0xd3c1d0);
              piVar14 = piStack_2ac;
              if (piStack_2ac != (int *)0x0) {
                uStack_19c = 8;
                FUN_005f4290(auStack_280,0xea09c0);
                uStack_30 = FUN_0039b0f0(ppppuRam00d951b8);
                ppppuVar4 = apppuStack_27c;
                if (0xf < uStack_268) {
                  ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                }
                if (ppppuRam00d951b8 < ppppuVar4) {
LAB_0012b4ac:
                  bVar1 = false;
                }
                else {
                  ppppuVar4 = apppuStack_27c;
                  if (0xf < uStack_268) {
                    ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                  }
                  bVar1 = true;
                  if ((undefined4 ****)((int)ppppuVar4 + uStack_26c) <= ppppuRam00d951b8)
                  goto LAB_0012b4ac;
                }
                if (bVar1) {
                  ppppuVar4 = apppuStack_27c;
                  if (0xf < uStack_268) {
                    ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                  }
                  uVar9 = 0xdb8b44 - (int)ppppuVar4;
                  if (uStack_26c < uVar9) {
                    uStack_19c = 7;
                    FUN_00250ea4(auStack_280);
                  }
                  if (uStack_26c - uVar9 < uStack_30) {
                    uStack_30 = uStack_26c - uVar9;
                  }
                  if (~uStack_26c <= uStack_30) {
                    uStack_19c = 7;
                    FUN_002513e0(auStack_280);
                  }
                  if (uStack_30 != 0) {
                    uVar7 = uStack_26c + uStack_30;
                    uStack_19c = 7;
                    iVar8 = FUN_005f0030(auStack_280,uVar7,0);
                    if (iVar8 != 0) {
                      ppppuVar4 = apppuStack_27c;
                      if (0xf < uStack_268) {
                        ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                      }
                      ppppuVar12 = apppuStack_27c;
                      if (0xf < uStack_268) {
                        ppppuVar12 = (undefined4 ****)apppuStack_27c[0];
                      }
                      FUN_0039ac74((int)ppppuVar4 + uStack_26c,(int)ppppuVar12 + uVar9,uStack_30);
                      ppppuVar4 = apppuStack_27c;
                      if (0xf < uStack_268) {
                        ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                      }
                      *(undefined1 *)((int)ppppuVar4 + uVar7) = 0;
                      uStack_26c = uVar7;
                    }
                  }
                }
                else {
                  if (~uStack_26c <= uStack_30) {
                    uStack_19c = 7;
                    FUN_002513e0(auStack_280);
                  }
                  if (uStack_30 != 0) {
                    uVar9 = uStack_26c + uStack_30;
                    uStack_19c = 7;
                    iVar8 = FUN_005f0030(auStack_280,uVar9,0);
                    if (iVar8 != 0) {
                      ppppuVar4 = apppuStack_27c;
                      if (0xf < uStack_268) {
                        ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                      }
                      FUN_0039ac74((int)ppppuVar4 + uStack_26c,ppppuRam00d951b8,uStack_30);
                      ppppuVar4 = apppuStack_27c;
                      if (0xf < uStack_268) {
                        ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                      }
                      uStack_26c = uVar9;
                      *(undefined1 *)((int)ppppuVar4 + uVar9) = 0;
                    }
                  }
                }
                uStack_19c = 7;
                FUN_005f4290(auStack_260,auStack_280);
                FUN_005e8e00(auStack_280);
                uStack_19c = 6;
                FUN_005f4290(auStack_280,auStack_260);
                uStack_20 = 0xffffffff;
                if (*(uint *)(iVar5 + 0x34) != 0xffffffff) {
                  uStack_20 = *(uint *)(iVar5 + 0x34);
                }
                if (~uStack_26c <= uStack_20) {
                  uStack_19c = 5;
                  FUN_002513e0(auStack_280);
                }
                if (uStack_20 != 0) {
                  uVar9 = uStack_26c + uStack_20;
                  uStack_19c = 5;
                  iVar8 = FUN_005f0030(auStack_280,uVar9,0);
                  if (iVar8 != 0) {
                    ppppuVar4 = apppuStack_27c;
                    if (0xf < uStack_268) {
                      ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                    }
                    iVar8 = iVar5 + 0x24;
                    if (0xf < *(uint *)(iVar5 + 0x38)) {
                      iVar8 = *(int *)(iVar5 + 0x24);
                    }
                    FUN_0039ac74((int)ppppuVar4 + uStack_26c,iVar8,uStack_20);
                    ppppuVar4 = apppuStack_27c;
                    if (0xf < uStack_268) {
                      ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                    }
                    uStack_26c = uVar9;
                    *(undefined1 *)((int)ppppuVar4 + uVar9) = 0;
                  }
                }
                uStack_19c = 5;
                FUN_005f4290(auStack_240,auStack_280);
                FUN_005e8e00(auStack_280);
                FUN_005e8e00(auStack_260);
                iVar8 = -1;
                if (piVar14[5] != 0) {
                  uStack_19c = 4;
                  iVar8 = FUN_001d9204(piVar14[5],0xffffffff);
                }
                if (iVar8 == 0) {
                  iStack_14 = FUN_00616f40(piVar14 + 0x19,auStack_240);
                  if (iStack_14 == piVar14[0x1b]) {
                    FUN_005e8e80(auStack_260);
                    uStack_19c = 3;
                    FUN_005f4290(auStack_210,auStack_240);
                    uStack_19c = 2;
                    FUN_005f4290(auStack_1f4,auStack_260);
                    uStack_19c = 1;
                    uVar15 = FUN_0061a308(piVar14 + 0x19,auStack_210);
                    iStack_14 = (int)((ulonglong)uVar15 >> 0x20);
                    uStack_220 = uVar15;
                    FUN_005e8e00(auStack_1f4);
                    FUN_005e8e00(auStack_210);
                    FUN_005e8e00(auStack_260);
                  }
                  uStack_19c = 4;
                  FUN_005ea15c(iStack_14 + 0x24,auStack_1d0,0,0xffffffff);
                  FUN_00616f40(piVar14 + 0x19,auStack_240);
                  if (piVar14[5] != 0) {
                    uStack_19c = 4;
                    FUN_001d92bc();
                  }
                }
                FUN_005e8e00(auStack_240);
              }
              FUN_005e8e00(auStack_1d0);
              uStack_168 = 1;
            }
            goto LAB_0012a2b8;
          }
        }
        uVar9 = uRam00ea0948;
        iVar8 = *(int *)(iVar5 + 0x94);
        if (iVar8 == iVar5 + 0x44) {
          iVar8 = 0;
        }
        if (iVar8 != 0) {
          puVar13 = &uRam00ea0938;
          if (0xf < uRam00ea094c) {
            puVar13 = uRam00ea0938;
          }
          uStack_ec = *(uint *)(iVar8 + 0x28);
          if (*(uint *)(iVar8 + 0x28) < *(uint *)(iVar8 + 0x28)) {
            uStack_ec = *(uint *)(iVar8 + 0x28);
          }
          uVar7 = 0;
          if (uStack_ec != 0) {
            iVar10 = iVar8 + 0x18;
            if (0xf < *(uint *)(iVar8 + 0x2c)) {
              iVar10 = *(int *)(iVar8 + 0x18);
            }
            uVar7 = uRam00ea0948;
            if (uStack_ec < uRam00ea0948) {
              uVar7 = uStack_ec;
            }
            uVar7 = FUN_0039ac2c(iVar10,puVar13,uVar7);
          }
          if ((uVar7 == 0) && (uVar7 = (uint)(uStack_ec != uVar9), uStack_ec < uVar9)) {
            uVar7 = 0xffffffff;
          }
          if (uVar7 == 0) {
            uStack_19c = 0x1e;
            FUN_005f4290(auStack_280,iVar5 + 0x20);
            uStack_d0 = FUN_0039b0f0(ppppuRam00d951bc);
            ppppuVar4 = apppuStack_27c;
            if (0xf < uStack_268) {
              ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
            }
            if (ppppuRam00d951bc < ppppuVar4) {
LAB_0012b034:
              bVar1 = false;
            }
            else {
              ppppuVar4 = apppuStack_27c;
              if (0xf < uStack_268) {
                ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
              }
              bVar1 = true;
              if ((undefined4 ****)((int)ppppuVar4 + uStack_26c) <= ppppuRam00d951bc)
              goto LAB_0012b034;
            }
            if (bVar1) {
              ppppuVar4 = apppuStack_27c;
              if (0xf < uStack_268) {
                ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
              }
              uVar9 = 0xd5abe4 - (int)ppppuVar4;
              if (uStack_26c < uVar9) {
                uStack_19c = 0x15;
                FUN_00250ea4(auStack_280);
              }
              if (uStack_26c - uVar9 < uStack_d0) {
                uStack_d0 = uStack_26c - uVar9;
              }
              if (~uStack_26c <= uStack_d0) {
                uStack_19c = 0x15;
                FUN_002513e0(auStack_280);
              }
              if (uStack_d0 != 0) {
                uVar7 = uStack_26c + uStack_d0;
                uStack_19c = 0x15;
                iVar10 = FUN_005f0030(auStack_280,uVar7,0);
                if (iVar10 != 0) {
                  ppppuVar4 = apppuStack_27c;
                  if (0xf < uStack_268) {
                    ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                  }
                  ppppuVar12 = apppuStack_27c;
                  if (0xf < uStack_268) {
                    ppppuVar12 = (undefined4 ****)apppuStack_27c[0];
                  }
                  FUN_0039ac74((int)ppppuVar4 + uStack_26c,(int)ppppuVar12 + uVar9,uStack_d0);
                  ppppuVar4 = apppuStack_27c;
                  if (0xf < uStack_268) {
                    ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                  }
                  *(undefined1 *)((int)ppppuVar4 + uVar7) = 0;
                  uStack_26c = uVar7;
                }
              }
            }
            else {
              if (~uStack_26c <= uStack_d0) {
                uStack_19c = 0x15;
                FUN_002513e0(auStack_280);
              }
              if (uStack_d0 != 0) {
                uVar9 = uStack_26c + uStack_d0;
                uStack_19c = 0x15;
                iVar10 = FUN_005f0030(auStack_280,uVar9,0);
                if (iVar10 != 0) {
                  ppppuVar4 = apppuStack_27c;
                  if (0xf < uStack_268) {
                    ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                  }
                  FUN_0039ac74((int)ppppuVar4 + uStack_26c,ppppuRam00d951bc,uStack_d0);
                  ppppuVar4 = apppuStack_27c;
                  if (0xf < uStack_268) {
                    ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                  }
                  uStack_26c = uVar9;
                  *(undefined1 *)((int)ppppuVar4 + uVar9) = 0;
                }
              }
            }
            uStack_19c = 0x15;
            FUN_005f4290(auStack_260,auStack_280);
            FUN_005e8e00(auStack_280);
            uStack_19c = 0x14;
            FUN_005f4290(auStack_280,auStack_260);
            uStack_c0 = 0xffffffff;
            if (*(uint *)(iVar8 + 0x44) != 0xffffffff) {
              uStack_c0 = *(uint *)(iVar8 + 0x44);
            }
            if (~uStack_26c <= uStack_c0) {
              uStack_19c = 0x13;
              FUN_002513e0(auStack_280);
            }
            if (uStack_c0 != 0) {
              uVar9 = uStack_26c + uStack_c0;
              uStack_19c = 0x13;
              iVar10 = FUN_005f0030(auStack_280,uVar9,0);
              if (iVar10 != 0) {
                ppppuVar4 = apppuStack_27c;
                if (0xf < uStack_268) {
                  ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                }
                iVar10 = iVar8 + 0x34;
                if (0xf < *(uint *)(iVar8 + 0x48)) {
                  iVar10 = *(int *)(iVar8 + 0x34);
                }
                FUN_0039ac74((int)ppppuVar4 + uStack_26c,iVar10,uStack_c0);
                ppppuVar4 = apppuStack_27c;
                if (0xf < uStack_268) {
                  ppppuVar4 = (undefined4 ****)apppuStack_27c[0];
                }
                uStack_26c = uVar9;
                *(undefined1 *)((int)ppppuVar4 + uVar9) = 0;
              }
            }
            uStack_19c = 0x13;
            FUN_005f4290(auStack_240,auStack_280);
            FUN_005e8e00(auStack_280);
            FUN_005e8e00(auStack_260);
            uStack_19c = 0x12;
            FUN_005ea3bc(auStack_260,0xd3c1d0);
            piVar14 = piStack_2ac;
            if (piStack_2ac != (int *)0x0) {
              uStack_19c = 0x11;
              FUN_005f4290(auStack_1d0,0xea09c0);
              uStack_a4 = FUN_0039b0f0(ppppuRam00d951b8);
              ppppuVar4 = apppuStack_1cc;
              if (0xf < uStack_1b8) {
                ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
              }
              if (ppppuRam00d951b8 < ppppuVar4) {
LAB_0012acd8:
                bVar1 = false;
              }
              else {
                ppppuVar4 = apppuStack_1cc;
                if (0xf < uStack_1b8) {
                  ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
                }
                bVar1 = true;
                if ((undefined4 ****)((int)ppppuVar4 + uStack_1bc) <= ppppuRam00d951b8)
                goto LAB_0012acd8;
              }
              if (bVar1) {
                ppppuVar4 = apppuStack_1cc;
                if (0xf < uStack_1b8) {
                  ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
                }
                uVar9 = 0xdb8b44 - (int)ppppuVar4;
                if (uStack_1bc < uVar9) {
                  uStack_19c = 0x10;
                  FUN_00250ea4(auStack_1d0);
                }
                if (uStack_1bc - uVar9 < uStack_a4) {
                  uStack_a4 = uStack_1bc - uVar9;
                }
                if (~uStack_1bc <= uStack_a4) {
                  uStack_19c = 0x10;
                  FUN_002513e0(auStack_1d0);
                }
                if (uStack_a4 != 0) {
                  uVar7 = uStack_1bc + uStack_a4;
                  uStack_19c = 0x10;
                  iVar8 = FUN_005f0030(auStack_1d0,uVar7,0);
                  if (iVar8 != 0) {
                    ppppuVar4 = apppuStack_1cc;
                    if (0xf < uStack_1b8) {
                      ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
                    }
                    ppppuVar12 = apppuStack_1cc;
                    if (0xf < uStack_1b8) {
                      ppppuVar12 = (undefined4 ****)apppuStack_1cc[0];
                    }
                    FUN_0039ac74((int)ppppuVar4 + uStack_1bc,(int)ppppuVar12 + uVar9,uStack_a4);
                    ppppuVar4 = apppuStack_1cc;
                    if (0xf < uStack_1b8) {
                      ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
                    }
                    *(undefined1 *)((int)ppppuVar4 + uVar7) = 0;
                    uStack_1bc = uVar7;
                  }
                }
              }
              else {
                if (~uStack_1bc <= uStack_a4) {
                  uStack_19c = 0x10;
                  FUN_002513e0(auStack_1d0);
                }
                if (uStack_a4 != 0) {
                  uVar9 = uStack_1bc + uStack_a4;
                  uStack_19c = 0x10;
                  iVar8 = FUN_005f0030(auStack_1d0,uVar9,0);
                  if (iVar8 != 0) {
                    ppppuVar4 = apppuStack_1cc;
                    if (0xf < uStack_1b8) {
                      ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
                    }
                    FUN_0039ac74((int)ppppuVar4 + uStack_1bc,ppppuRam00d951b8,uStack_a4);
                    ppppuVar4 = apppuStack_1cc;
                    if (0xf < uStack_1b8) {
                      ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
                    }
                    uStack_1bc = uVar9;
                    *(undefined1 *)((int)ppppuVar4 + uVar9) = 0;
                  }
                }
              }
              uStack_19c = 0x10;
              FUN_005f4290(auStack_2a0,auStack_1d0);
              FUN_005e8e00(auStack_1d0);
              uStack_19c = 0xf;
              FUN_005f4290(auStack_1d0,auStack_2a0);
              uStack_94 = 0xffffffff;
              if (uStack_22c != 0xffffffff) {
                uStack_94 = uStack_22c;
              }
              if (~uStack_1bc <= uStack_94) {
                uStack_19c = 0xe;
                FUN_002513e0(auStack_1d0);
              }
              if (uStack_94 != 0) {
                uVar9 = uStack_1bc + uStack_94;
                uStack_19c = 0xe;
                iVar8 = FUN_005f0030(auStack_1d0,uVar9,0);
                if (iVar8 != 0) {
                  ppppuVar4 = apppuStack_1cc;
                  if (0xf < uStack_1b8) {
                    ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
                  }
                  ppppuVar12 = apppuStack_23c;
                  if (0xf < uStack_228) {
                    ppppuVar12 = (undefined4 ****)apppuStack_23c[0];
                  }
                  FUN_0039ac74((int)ppppuVar4 + uStack_1bc,ppppuVar12,uStack_94);
                  ppppuVar4 = apppuStack_1cc;
                  if (0xf < uStack_1b8) {
                    ppppuVar4 = (undefined4 ****)apppuStack_1cc[0];
                  }
                  uStack_1bc = uVar9;
                  *(undefined1 *)((int)ppppuVar4 + uVar9) = 0;
                }
              }
              uStack_19c = 0xe;
              FUN_005f4290(auStack_280,auStack_1d0);
              FUN_005e8e00(auStack_1d0);
              FUN_005e8e00(auStack_2a0);
              iVar8 = -1;
              if (piVar14[5] != 0) {
                uStack_19c = 0xd;
                iVar8 = FUN_001d9204(piVar14[5],0xffffffff);
              }
              if (iVar8 == 0) {
                iStack_88 = FUN_00616f40(piVar14 + 0x19,auStack_280);
                if (iStack_88 == piVar14[0x1b]) {
                  FUN_005e8e80(auStack_1d0);
                  uStack_19c = 0xc;
                  FUN_005f4290(auStack_210,auStack_280);
                  uStack_19c = 0xb;
                  FUN_005f4290(auStack_1f4,auStack_1d0);
                  uStack_19c = 10;
                  uVar15 = FUN_0061a308(piVar14 + 0x19,auStack_210);
                  iStack_88 = (int)((ulonglong)uVar15 >> 0x20);
                  uStack_220 = uVar15;
                  FUN_005e8e00(auStack_1f4);
                  FUN_005e8e00(auStack_210);
                  FUN_005e8e00(auStack_1d0);
                }
                uStack_19c = 0xd;
                FUN_005ea15c(iStack_88 + 0x24,auStack_260,0,0xffffffff);
                FUN_00616f40(piVar14 + 0x19,auStack_280);
                if (piVar14[5] != 0) {
                  uStack_19c = 0xd;
                  FUN_001d92bc();
                }
              }
              FUN_005e8e00(auStack_280);
            }
            FUN_005e8e00(auStack_260);
            uStack_168 = 1;
            iVar8 = iVar5 + 0x24;
            if (0xf < *(uint *)(iVar5 + 0x38)) {
              iVar8 = *(int *)(iVar5 + 0x24);
            }
            uStack_19c = 0x12;
            FUN_0005e784(3,0x140,0xb,0xd4bc0c,0x6627d0,0x390,0xd4beb0,iVar8);
            FUN_005e8e00(auStack_240);
          }
        }
      }
LAB_0012a2b8:
      piVar14 = piStack_2ac;
      if (piStack_2ac != (int *)0x0) {
        iVar8 = -1;
        if (piStack_2ac[3] != 0) {
          uStack_19c = 0xffffffff;
          iVar8 = FUN_001d9204(piStack_2ac[3],0xffffffff);
        }
        if ((iVar8 == 0) && (*piVar14 = *piVar14 + -1, piVar14[3] != 0)) {
          uStack_19c = 0xffffffff;
          FUN_001d92bc();
        }
      }
      uStack_19c = 0xffffffff;
      iVar5 = FUN_00225120(iVar5);
    }
  }
  FUN_003d12b8(auStack_1a0);
  return uStack_168;
}

