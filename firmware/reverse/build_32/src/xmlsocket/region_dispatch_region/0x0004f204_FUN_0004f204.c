/* 0x0004f204  FUN_0004f204  size=6168 bytes */


/* WARNING: Removing unreachable block (ram,0x0004f6e8) */
/* WARNING: Removing unreachable block (ram,0x0004f708) */
/* WARNING: Removing unreachable block (ram,0x0004f71c) */
/* WARNING: Removing unreachable block (ram,0x0004f720) */
/* WARNING: Removing unreachable block (ram,0x0004f734) */
/* WARNING: Removing unreachable block (ram,0x0004f738) */
/* WARNING: Removing unreachable block (ram,0x0004fbb8) */
/* WARNING: Removing unreachable block (ram,0x0004fbd8) */
/* WARNING: Removing unreachable block (ram,0x0004fbec) */
/* WARNING: Removing unreachable block (ram,0x0004fbf0) */
/* WARNING: Removing unreachable block (ram,0x0004fc04) */
/* WARNING: Removing unreachable block (ram,0x0004fc08) */
/* WARNING: Removing unreachable block (ram,0x0004f8bc) */
/* WARNING: Removing unreachable block (ram,0x0004f8dc) */
/* WARNING: Removing unreachable block (ram,0x0004f8f0) */
/* WARNING: Removing unreachable block (ram,0x0004f8f4) */
/* WARNING: Removing unreachable block (ram,0x0004f908) */
/* WARNING: Removing unreachable block (ram,0x0004f90c) */
/* WARNING: Removing unreachable block (ram,0x0004f500) */
/* WARNING: Removing unreachable block (ram,0x0004f520) */
/* WARNING: Removing unreachable block (ram,0x0004f534) */
/* WARNING: Removing unreachable block (ram,0x0004f538) */
/* WARNING: Removing unreachable block (ram,0x0004f54c) */
/* WARNING: Removing unreachable block (ram,0x0004f550) */
/* WARNING: Removing unreachable block (ram,0x0004ff5c) */
/* WARNING: Removing unreachable block (ram,0x0004ff7c) */
/* WARNING: Removing unreachable block (ram,0x0004ff90) */
/* WARNING: Removing unreachable block (ram,0x0004ff94) */
/* WARNING: Removing unreachable block (ram,0x0004ffa8) */
/* WARNING: Removing unreachable block (ram,0x0004ffac) */
/* WARNING: Heritage AFTER dead removal. Example location: s0xfffffe94 : 0x0004f578 */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

undefined4 FUN_0004f204(int param_1)

{
  bool bVar1;
  undefined4 ****ppppuVar2;
  int iVar3;
  uint uVar4;
  undefined4 ****ppppuVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined1 auStack_578 [8];
  undefined1 auStack_570 [128];
  undefined4 **appuStack_4f0 [224];
  undefined1 auStack_170 [4];
  undefined4 ***apppuStack_16c [4];
  uint uStack_15c;
  uint uStack_158;
  undefined1 auStack_140 [4];
  undefined4 uStack_13c;
  undefined4 uStack_128;
  undefined4 uStack_124;
  undefined1 *puStack_120;
  undefined4 uStack_11c;
  undefined4 uStack_108;
  uint uStack_ec;
  int iStack_e0;
  uint uStack_d8;
  uint uStack_bc;
  int iStack_b0;
  uint uStack_a8;
  uint uStack_8c;
  int iStack_80;
  uint uStack_78;
  uint uStack_5c;
  int iStack_50;
  uint uStack_48;
  uint uStack_2c;
  int iStack_20;
  uint uStack_18;
  
  uStack_128 = 0x25710c;
  puStack_120 = auStack_578;
  uStack_11c = 0x5f340;
  uStack_124 = 0xe964d8;
  FUN_003d1214(auStack_140);
  uStack_108 = 0;
  uStack_13c = 1;
  uStack_158 = 0xf;
  uStack_15c = 0;
  apppuStack_16c[0] = (undefined4 ***)((uint)apppuStack_16c[0] & 0xffffff);
  FUN_00062068(auStack_170);
  iVar3 = param_1 + 0x4c;
  if (0xf < *(uint *)(param_1 + 0x60)) {
    iVar3 = *(int *)(param_1 + 0x4c);
  }
  uStack_13c = 1;
  iVar3 = FUN_0044f4cc(iVar3,0,0);
  if (iVar3 < 0) {
    uStack_13c = 1;
    FUN_00442914();
    uVar7 = 0xd3c598;
    uVar6 = 0x3d5;
  }
  else {
    uStack_13c = 1;
    iVar3 = FUN_0044e144(iVar3,auStack_570,0x400);
    if (iVar3 == 0x400) {
      ppppuVar2 = apppuStack_16c;
      if (0xf < uStack_158) {
        ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
      }
      iVar3 = FUN_0039b188(ppppuVar2,appuStack_4f0,0x20);
      if (iVar3 == 0) {
LAB_0004f5a0:
        uStack_108 = 1;
      }
      else {
        iVar3 = FUN_0039b188(appuStack_4f0,0xd3c5c8,0x20);
        if (iVar3 == 0) {
          uVar4 = FUN_0039b0f0(ppppuRam00d94ccc);
          ppppuVar2 = apppuStack_16c;
          if (0xf < uStack_158) {
            ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
          }
          if (ppppuRam00d94ccc < ppppuVar2) {
LAB_0004f5ac:
            bVar1 = false;
          }
          else {
            ppppuVar2 = apppuStack_16c;
            if (0xf < uStack_158) {
              ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
            }
            bVar1 = true;
            if ((undefined4 ****)((int)ppppuVar2 + uStack_15c) <= ppppuRam00d94ccc)
            goto LAB_0004f5ac;
          }
          if (bVar1) {
            ppppuVar2 = apppuStack_16c;
            if (0xf < uStack_158) {
              ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
            }
            uStack_d8 = 0xd3c5c8 - (int)ppppuVar2;
            if (uStack_15c < uStack_d8) {
              uStack_13c = 1;
              FUN_00250ea4(auStack_170);
            }
            uStack_ec = uStack_15c - uStack_d8;
            if (uVar4 < uStack_15c - uStack_d8) {
              uStack_ec = uVar4;
            }
            uStack_ec = uStack_d8 + uStack_ec;
            iStack_e0 = -1;
            if (uStack_15c < uStack_ec) {
              uStack_13c = 1;
              FUN_00250ea4(auStack_170);
            }
            if (uStack_15c - uStack_ec != -1) {
              iStack_e0 = uStack_15c - uStack_ec;
            }
            if (iStack_e0 != 0) {
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              ppppuVar5 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar5 = (undefined4 ****)apppuStack_16c[0];
              }
              uStack_13c = 1;
              FUN_0039acb0((undefined1 *)((int)ppppuVar2 + uStack_ec),
                           (undefined1 *)((int)ppppuVar5 + iStack_e0 + uStack_ec),
                           (uStack_15c - uStack_ec) - iStack_e0);
              uStack_15c = uStack_15c - iStack_e0;
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
            }
            if (uStack_15c < uStack_d8) {
              uStack_d8 = uStack_15c;
            }
            if (uStack_d8 != 0) {
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              uStack_13c = 1;
              FUN_0039acb0(ppppuVar2,(undefined1 *)((int)ppppuVar2 + uStack_d8),
                           uStack_15c - uStack_d8);
              uStack_15c = uStack_15c - uStack_d8;
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
            }
          }
          else {
            if (0xfffffffe < uVar4) {
              uStack_13c = 1;
              FUN_002513e0(auStack_170);
            }
            if (uStack_158 < uVar4) {
              uStack_13c = 1;
              FUN_005e7bb8(auStack_170,uVar4,uStack_15c);
            }
            else if (uVar4 == 0) {
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              uStack_15c = 0;
              *(undefined1 *)ppppuVar2 = 0;
            }
            if (uVar4 != 0) {
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              FUN_0039ac74(ppppuVar2,ppppuRam00d94ccc,uVar4);
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              uStack_15c = uVar4;
              *(undefined1 *)((int)ppppuVar2 + uVar4) = 0;
            }
          }
          uStack_13c = 1;
          iVar3 = FUN_0005fe9c(auStack_170);
          if (iVar3 == 0) goto LAB_0004f5a0;
          FUN_0005e784(0,3,0x11,0xd3c31c,0x65d154,0x3ee,0xd3c778);
        }
        else {
          ppppuVar2 = apppuStack_16c;
          if (0xf < uStack_158) {
            ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
          }
          iVar3 = FUN_0039b188(ppppuVar2,0xd3c5c8,0xe);
          if (iVar3 == 0) {
            uVar4 = FUN_0039b0f0(appuStack_4f0);
            ppppuVar2 = apppuStack_16c;
            if (0xf < uStack_158) {
              ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
            }
            if (appuStack_4f0 < ppppuVar2) {
LAB_0004f7b8:
              bVar1 = false;
            }
            else {
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              bVar1 = true;
              if ((undefined4 ****)((int)ppppuVar2 + uStack_15c) <= appuStack_4f0)
              goto LAB_0004f7b8;
            }
            if (bVar1) {
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              uStack_a8 = (int)appuStack_4f0 - (int)ppppuVar2;
              if (uStack_15c < uStack_a8) {
                uStack_13c = 1;
                FUN_00250ea4(auStack_170);
              }
              uStack_bc = uStack_15c - uStack_a8;
              if (uVar4 < uStack_15c - uStack_a8) {
                uStack_bc = uVar4;
              }
              uStack_bc = uStack_a8 + uStack_bc;
              iStack_b0 = -1;
              if (uStack_15c < uStack_bc) {
                uStack_13c = 1;
                FUN_00250ea4(auStack_170);
              }
              if (uStack_15c - uStack_bc != -1) {
                iStack_b0 = uStack_15c - uStack_bc;
              }
              if (iStack_b0 != 0) {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                ppppuVar5 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar5 = (undefined4 ****)apppuStack_16c[0];
                }
                uStack_13c = 1;
                FUN_0039acb0((undefined1 *)((int)ppppuVar2 + uStack_bc),
                             (undefined1 *)((int)ppppuVar5 + iStack_b0 + uStack_bc),
                             (uStack_15c - uStack_bc) - iStack_b0);
                uStack_15c = uStack_15c - iStack_b0;
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
              }
              if (uStack_15c < uStack_a8) {
                uStack_a8 = uStack_15c;
              }
              if (uStack_a8 != 0) {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                uStack_13c = 1;
                FUN_0039acb0(ppppuVar2,(undefined1 *)((int)ppppuVar2 + uStack_a8),
                             uStack_15c - uStack_a8);
                uStack_15c = uStack_15c - uStack_a8;
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
              }
            }
            else {
              if (0xfffffffe < uVar4) {
                uStack_13c = 1;
                FUN_002513e0(auStack_170);
              }
              if (uStack_158 < uVar4) {
                uStack_13c = 1;
                FUN_005e7bb8(auStack_170,uVar4,uStack_15c);
              }
              else if (uVar4 == 0) {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                uStack_15c = 0;
                *(undefined1 *)ppppuVar2 = 0;
              }
              if (uVar4 != 0) {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                FUN_0039ac74(ppppuVar2,appuStack_4f0,uVar4);
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                uStack_15c = uVar4;
                *(undefined1 *)((int)ppppuVar2 + uVar4) = 0;
              }
            }
            uStack_13c = 1;
            iVar3 = FUN_0005fe9c(auStack_170);
            if (iVar3 == 0) goto LAB_0004f5a0;
            FUN_0005e784(0,3,0x11,0xd3c31c,0x65d154,0x3f9,0xd3c778);
          }
          else {
            ppppuVar2 = apppuStack_16c;
            if (0xf < uStack_158) {
              ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
            }
            iVar3 = FUN_0039b188(ppppuVar2,0xd3c5d8,0x1b);
            if (iVar3 == 0) {
              uVar4 = FUN_0039b0f0(appuStack_4f0);
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              if (appuStack_4f0 < ppppuVar2) {
LAB_0004f98c:
                bVar1 = false;
              }
              else {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                bVar1 = true;
                if ((undefined4 ****)((int)ppppuVar2 + uStack_15c) <= appuStack_4f0)
                goto LAB_0004f98c;
              }
              if (bVar1) {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                uStack_78 = (int)appuStack_4f0 - (int)ppppuVar2;
                if (uStack_15c < uStack_78) {
                  uStack_13c = 1;
                  FUN_00250ea4(auStack_170);
                }
                uStack_8c = uStack_15c - uStack_78;
                if (uVar4 < uStack_15c - uStack_78) {
                  uStack_8c = uVar4;
                }
                uStack_8c = uStack_78 + uStack_8c;
                iStack_80 = -1;
                if (uStack_15c < uStack_8c) {
                  uStack_13c = 1;
                  FUN_00250ea4(auStack_170);
                }
                if (uStack_15c - uStack_8c != -1) {
                  iStack_80 = uStack_15c - uStack_8c;
                }
                if (iStack_80 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  ppppuVar5 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar5 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_13c = 1;
                  FUN_0039acb0((undefined1 *)((int)ppppuVar2 + uStack_8c),
                               (undefined1 *)((int)ppppuVar5 + iStack_80 + uStack_8c),
                               (uStack_15c - uStack_8c) - iStack_80);
                  uStack_15c = uStack_15c - iStack_80;
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
                }
                if (uStack_15c < uStack_78) {
                  uStack_78 = uStack_15c;
                }
                if (uStack_78 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_13c = 1;
                  FUN_0039acb0(ppppuVar2,(undefined1 *)((int)ppppuVar2 + uStack_78),
                               uStack_15c - uStack_78);
                  uStack_15c = uStack_15c - uStack_78;
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
                }
              }
              else {
                if (0xfffffffe < uVar4) {
                  uStack_13c = 1;
                  FUN_002513e0(auStack_170);
                }
                if (uStack_158 < uVar4) {
                  uStack_13c = 1;
                  FUN_005e7bb8(auStack_170,uVar4,uStack_15c);
                }
                else if (uVar4 == 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_15c = 0;
                  *(undefined1 *)ppppuVar2 = 0;
                }
                if (uVar4 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  FUN_0039ac74(ppppuVar2,appuStack_4f0,uVar4);
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_15c = uVar4;
                  *(undefined1 *)((int)ppppuVar2 + uVar4) = 0;
                }
              }
              uStack_13c = 1;
              iVar3 = FUN_0005fe9c(auStack_170);
              if (iVar3 == 0) goto LAB_0004f5a0;
              FUN_0005e784(0,3,0x11,0xd3c31c,0x65d154,0x404,0xd3c778);
            }
            else if (uStack_15c == 0) {
              uVar4 = FUN_0039b0f0(appuStack_4f0);
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              if (appuStack_4f0 < ppppuVar2) {
LAB_0004fc88:
                bVar1 = false;
              }
              else {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                bVar1 = true;
                if ((undefined4 ****)((int)ppppuVar2 + uStack_15c) <= appuStack_4f0)
                goto LAB_0004fc88;
              }
              if (bVar1) {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                uStack_48 = (int)appuStack_4f0 - (int)ppppuVar2;
                if (uStack_15c < uStack_48) {
                  uStack_13c = 1;
                  FUN_00250ea4(auStack_170);
                }
                uStack_5c = uStack_15c - uStack_48;
                if (uVar4 < uStack_15c - uStack_48) {
                  uStack_5c = uVar4;
                }
                uStack_5c = uStack_48 + uStack_5c;
                iStack_50 = -1;
                if (uStack_15c < uStack_5c) {
                  uStack_13c = 1;
                  FUN_00250ea4(auStack_170);
                }
                if (uStack_15c - uStack_5c != -1) {
                  iStack_50 = uStack_15c - uStack_5c;
                }
                if (iStack_50 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  ppppuVar5 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar5 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_13c = 1;
                  FUN_0039acb0((undefined1 *)((int)ppppuVar2 + uStack_5c),
                               (undefined1 *)((int)ppppuVar5 + iStack_50 + uStack_5c),
                               (uStack_15c - uStack_5c) - iStack_50);
                  uStack_15c = uStack_15c - iStack_50;
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
                }
                if (uStack_15c < uStack_48) {
                  uStack_48 = uStack_15c;
                }
                if (uStack_48 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_13c = 1;
                  FUN_0039acb0(ppppuVar2,(undefined1 *)((int)ppppuVar2 + uStack_48),
                               uStack_15c - uStack_48);
                  uStack_15c = uStack_15c - uStack_48;
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
                }
              }
              else {
                if (0xfffffffe < uVar4) {
                  uStack_13c = 1;
                  FUN_002513e0(auStack_170);
                }
                if (uStack_158 < uVar4) {
                  uStack_13c = 1;
                  FUN_005e7bb8(auStack_170,uVar4,uStack_15c);
                }
                else if (uVar4 == 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_15c = 0;
                  *(undefined1 *)ppppuVar2 = 0;
                }
                if (uVar4 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  FUN_0039ac74(ppppuVar2,appuStack_4f0,uVar4);
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_15c = uVar4;
                  *(undefined1 *)((int)ppppuVar2 + uVar4) = 0;
                }
              }
              uStack_13c = 1;
              iVar3 = FUN_0005fe9c(auStack_170);
              if (iVar3 == 0) goto LAB_0004f5a0;
              FUN_0005e784(0,3,0x11,0xd3c31c,0x65d154,0x40f,0xd3c778);
            }
            else {
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              iVar3 = FUN_0039b188(ppppuVar2,0xd3c5f4,0x21);
              if (iVar3 != 0) goto LAB_0004f30c;
              uVar4 = FUN_0039b0f0(appuStack_4f0);
              ppppuVar2 = apppuStack_16c;
              if (0xf < uStack_158) {
                ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
              }
              if (appuStack_4f0 < ppppuVar2) {
LAB_0005002c:
                bVar1 = false;
              }
              else {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                bVar1 = true;
                if ((undefined4 ****)((int)ppppuVar2 + uStack_15c) <= appuStack_4f0)
                goto LAB_0005002c;
              }
              if (bVar1) {
                ppppuVar2 = apppuStack_16c;
                if (0xf < uStack_158) {
                  ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                }
                uStack_18 = (int)appuStack_4f0 - (int)ppppuVar2;
                if (uStack_15c < uStack_18) {
                  uStack_13c = 1;
                  FUN_00250ea4(auStack_170);
                }
                uStack_2c = uStack_15c - uStack_18;
                if (uVar4 < uStack_15c - uStack_18) {
                  uStack_2c = uVar4;
                }
                uStack_2c = uStack_18 + uStack_2c;
                iStack_20 = -1;
                if (uStack_15c < uStack_2c) {
                  uStack_13c = 1;
                  FUN_00250ea4(auStack_170);
                }
                if (uStack_15c - uStack_2c != -1) {
                  iStack_20 = uStack_15c - uStack_2c;
                }
                if (iStack_20 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  ppppuVar5 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar5 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_13c = 1;
                  FUN_0039acb0((undefined1 *)((int)ppppuVar2 + uStack_2c),
                               (undefined1 *)((int)ppppuVar5 + iStack_20 + uStack_2c),
                               (uStack_15c - uStack_2c) - iStack_20);
                  uStack_15c = uStack_15c - iStack_20;
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
                }
                if (uStack_15c < uStack_18) {
                  uStack_18 = uStack_15c;
                }
                if (uStack_18 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_13c = 1;
                  FUN_0039acb0(ppppuVar2,(undefined1 *)((int)ppppuVar2 + uStack_18),
                               uStack_15c - uStack_18);
                  uStack_15c = uStack_15c - uStack_18;
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  *(undefined1 *)((int)ppppuVar2 + uStack_15c) = 0;
                }
              }
              else {
                if (0xfffffffe < uVar4) {
                  uStack_13c = 1;
                  FUN_002513e0(auStack_170);
                }
                if (uStack_158 < uVar4) {
                  uStack_13c = 1;
                  FUN_005e7bb8(auStack_170,uVar4,uStack_15c);
                }
                else if (uVar4 == 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_15c = 0;
                  *(undefined1 *)ppppuVar2 = 0;
                }
                if (uVar4 != 0) {
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  FUN_0039ac74(ppppuVar2,appuStack_4f0,uVar4);
                  ppppuVar2 = apppuStack_16c;
                  if (0xf < uStack_158) {
                    ppppuVar2 = (undefined4 ****)apppuStack_16c[0];
                  }
                  uStack_15c = uVar4;
                  *(undefined1 *)((int)ppppuVar2 + uVar4) = 0;
                }
              }
              uStack_13c = 1;
              iVar3 = FUN_0005fe9c(auStack_170);
              if (iVar3 == 0) goto LAB_0004f5a0;
              FUN_0005e784(0,3,0x11,0xd3c31c,0x65d154,0x41a,0xd3c778);
            }
          }
        }
        uStack_108 = 1;
      }
      goto LAB_0004f30c;
    }
    FUN_00442914();
    uVar7 = 0xd3c574;
    uVar6 = 0x3de;
  }
  FUN_0005e784(0,3,0x11,0xd3c31c,0x65d154,uVar6,uVar7,0x65d154);
LAB_0004f30c:
  FUN_005e75e4(auStack_170,1,0);
  FUN_003d12b8(auStack_140);
  return uStack_108;
}

