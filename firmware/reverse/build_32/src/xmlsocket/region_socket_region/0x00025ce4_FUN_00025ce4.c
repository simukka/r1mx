/* 0x00025ce4  FUN_00025ce4  size=2372 bytes */


undefined4 FUN_00025ce4(int param_1,undefined1 *param_2)

{
  bool bVar1;
  ushort uVar2;
  bool bVar3;
  ushort uVar5;
  int iVar4;
  int iVar6;
  undefined1 uVar10;
  undefined4 uVar7;
  int iVar8;
  short sVar9;
  byte bVar11;
  int iVar12;
  uint uVar13;
  undefined4 uVar14;
  ushort *puVar15;
  uint uVar16;
  int iVar17;
  uint uVar18;
  undefined2 auStack_38 [6];
  
  uVar13 = *(uint *)(param_1 + 0x38);
  iVar12 = *(int *)(param_1 + 0x34) * 0x430;
  puVar15 = (ushort *)(uVar13 * 600 + iVar12 + 0x108e6a0);
  bVar3 = false;
  uVar14 = 0;
  uVar16 = *(uint *)(param_2 + 0x18);
  if (6 < iRam00e107b4) {
    FUN_00443f20(0xd361e8,*(undefined4 *)(param_1 + 0x34),uVar13,*param_2,0,0,0);
  }
  if (*(int *)(param_2 + 0xc) == 0) {
    *(undefined4 *)(param_1 + 0x44) = 0;
    *(undefined4 *)(param_1 + 0x48) = 0;
  }
  else {
    *(undefined4 *)(param_1 + 0x44) = **(undefined4 **)(param_2 + 0xc);
    *(int *)(param_1 + 0x48) = **(int **)(param_2 + 0xc) + *(int *)(param_2 + 0x10);
  }
  *(undefined4 *)(param_1 + 0x4c) = *(undefined4 *)(param_2 + 0x14);
  *(undefined4 *)(param_1 + 0x50) = 0;
  *(undefined4 *)(param_1 + 0x54) = 0;
  *(undefined1 *)(param_1 + 0x58) = 0;
  *(undefined1 *)(param_1 + 0x59) = 0;
  *(undefined2 *)(param_1 + 0x5a) = 0;
  if ((*(int *)(param_2 + 0x1c) != 0) && (0xc < (short)puVar15[0x10b])) {
    uVar14 = 1;
    bVar3 = true;
  }
  FUN_000206bc(*(undefined4 *)(param_1 + 0x34),0x88,1);
  uVar18 = (uVar13 & 0xf) << 4 | 0xa0;
  FUN_0000a07c(*(undefined4 *)(iVar12 + 0x108ea20),uVar18);
  FUN_0000dc08();
  iVar6 = FUN_000206bc(*(undefined4 *)(param_1 + 0x34),0x88,1);
  if (iVar6 != 0) {
    FUN_0000a07c(*(undefined4 *)(iVar12 + 0x108ea20),uVar18);
    FUN_0000dc08();
  }
  FUN_0000a07c(*(undefined4 *)(iVar12 + 0x108ea0c),uVar14);
  FUN_0000a07c(*(undefined4 *)(iVar12 + 0x108ea18),uVar16 & 0xff);
  FUN_0000a07c(*(undefined4 *)(iVar12 + 0x108ea1c),uVar16 >> 8 & 0xff);
  do {
    uVar16 = FUN_0000a05c(*(undefined4 *)(iVar12 + 0x108ea28));
  } while ((uVar16 & 0x88) != 0);
  *(undefined4 *)(iVar12 + 0x108ea48) = 1;
  FUN_0000a07c(*(undefined4 *)(iVar12 + 0x108ea24),0xa0);
  uVar2 = *puVar15;
  uVar5 = uVar2 & 0x60;
  if (uVar5 == 0x20) {
    iVar6 = FUN_005accf4(iVar12 + 0x108e8f8,*(undefined4 *)(iVar12 + 0x108e9d8));
    if (iVar6 == -1) {
      *(undefined4 *)(param_1 + 0x54) = 1;
      goto LAB_00025e94;
    }
    *(char *)(param_1 + 0x59) = (char)*(undefined4 *)(iVar12 + 0x108e9f8);
    if (((*(byte *)(param_1 + 0x59) & 8) != 0) && ((*(byte *)(param_1 + 0x59) & 0x80) == 0))
    goto LAB_00025e68;
    uVar14 = 2;
  }
  else {
    if (uVar5 < 0x21) {
      bVar1 = (uVar2 & 0x60) == 0;
    }
    else {
      bVar1 = uVar5 == 0x40;
    }
    if (bVar1) {
      do {
        uVar10 = FUN_0000a05c(*(undefined4 *)(iVar12 + 0x108ea28));
        *(undefined1 *)(param_1 + 0x59) = uVar10;
        if ((*(byte *)(param_1 + 0x59) & 0x88) == 8) break;
        uVar10 = FUN_0000a05c(*(undefined4 *)(iVar12 + 0x108ea28));
        *(undefined1 *)(param_1 + 0x59) = uVar10;
      } while ((*(byte *)(param_1 + 0x59) & 0x88) != 8);
    }
LAB_00025e68:
    uVar10 = FUN_0000a05c(*(undefined4 *)(iVar12 + 0x108ea10));
    *(undefined1 *)(param_1 + 0x58) = uVar10;
    if (((*(byte *)(param_1 + 0x58) & 1) != 0) && ((*(byte *)(param_1 + 0x58) & 2) == 0)) {
      FUN_0000a1a4(*(undefined4 *)(iVar12 + 0x108ea04),param_2,6);
      if (bVar3) {
        iVar6 = *(int *)(param_1 + 0x34) * 0x430;
        iVar4 = iVar6 + 0x108e6a0;
        iVar17 = *(int *)(param_1 + 0x38) * 600 + iVar4;
        sVar9 = FUN_0000a05c(*(undefined4 *)(iVar6 + 0x108ea1c));
        *(short *)(param_1 + 0x5a) = sVar9 << 8;
        iVar8 = -1;
        sVar9 = FUN_0000a05c(*(undefined4 *)(iVar6 + 0x108ea18));
        *(short *)(param_1 + 0x5a) = *(short *)(param_1 + 0x5a) + sVar9;
        if ((*(int *)(param_1 + 0x48) == 0) && (*(short *)(param_1 + 0x5a) != 0)) {
          iVar6 = -1;
          *(undefined4 *)(param_1 + 0x54) = 8;
        }
        else {
          uVar16 = (uint)*(ushort *)(param_1 + 0x5a);
          uVar18 = *(int *)(param_1 + 0x48) - *(int *)(param_1 + 0x44);
          if (uVar16 < uVar18) {
            uVar18 = (uint)*(ushort *)(param_1 + 0x5a);
          }
          else {
            uVar16 = (uint)*(ushort *)(param_1 + 0x5a);
            *(undefined4 *)(param_1 + 0x48) = 0;
          }
          iVar17 = FUN_0002447c(*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x44),
                                uVar18,*(undefined4 *)(param_1 + 0x4c),
                                *(undefined4 *)(iVar17 + 0x220),*(undefined4 *)(iVar17 + 0x224),
                                uVar16);
          if (iVar17 == -1) {
LAB_00026450:
            uVar14 = FUN_0000a05c(*(undefined4 *)(iVar6 + 0x108ea08));
            uVar7 = FUN_0000a05c(*(undefined4 *)(iVar6 + 0x108ea2c));
            if (6 < iRam00e107b4) {
              FUN_00443f20(0xd36288,*(undefined4 *)(iVar6 + 0x108e9f8),uVar7,
                           *(undefined4 *)(iVar6 + 0x108e9fc),iVar8,uVar14,6);
            }
            FUN_0001fbe8(*(undefined4 *)(param_1 + 0x34));
          }
          else {
            bVar11 = FUN_0000a05c(*(undefined4 *)(iVar6 + 0x108ea40));
            if (*(int *)(param_1 + 0x38) == 0) {
              bVar11 = bVar11 | 0x26;
            }
            else {
              bVar11 = bVar11 | 0x46;
            }
            FUN_0000a07c(*(undefined4 *)(iVar6 + 0x108ea40),bVar11);
            *(undefined4 *)(iVar6 + 0x108ea48) = 1;
            *(undefined4 *)(iVar6 + 0x108ea4c) = 1;
            if (*(int *)(param_1 + 0x4c) == 1) {
              if (pcRam00e29370 != reset_vector) {
                (*pcRam00e29370)(1,*(undefined4 *)(param_1 + 0x44),uVar18);
              }
              FUN_0000a07c(*(undefined4 *)(iVar6 + 0x108ea3c),0);
              uVar14 = *(undefined4 *)(iVar6 + 0x108ea3c);
              uVar7 = 1;
            }
            else {
              if (pcRam00e29374 != reset_vector) {
                (*pcRam00e29374)(1,*(undefined4 *)(param_1 + 0x44),uVar18);
              }
              FUN_0000a07c(*(undefined4 *)(iVar6 + 0x108ea3c),8);
              uVar14 = *(undefined4 *)(iVar6 + 0x108ea3c);
              uVar7 = 9;
            }
            FUN_0000a07c(uVar14,uVar7);
            iVar8 = FUN_005accf4(iVar6 + 0x108e8f8,*(undefined4 *)(iVar6 + 0x108e9d8));
            if (iRam00e9c3b8 == 0x55) {
              FUN_00443f20(0xd362f0,1,2,3,4,5,6);
              FUN_0000daac(iVar4,0);
            }
            else {
              if (iRam00e9c3bc != 0x55) {
                if (((*(uint *)(iVar6 + 0x108e9fc) & 2) == 0) && (iVar8 != -1)) {
                  if (6 < iRam00e107b4) {
                    FUN_00443f20(0xd362d8,1,2,3,4,5,6);
                  }
                  iVar6 = 0;
                  *(uint *)(param_1 + 0x44) =
                       *(int *)(param_1 + 0x44) + (uint)*(ushort *)(param_1 + 0x5a);
                  goto LAB_00026388;
                }
                goto LAB_00026450;
              }
              FUN_00443f20(0xd36310,1,2,3,4,5,6);
              FUN_0000daac(iVar4,1);
            }
          }
          iVar6 = -1;
          *(undefined4 *)(param_1 + 0x54) = 0x1b;
        }
      }
      else {
        iVar6 = *(int *)(param_1 + 0x34) * 0x430;
        while( true ) {
          *(undefined4 *)(iVar6 + 0x108ea48) = 1;
          iVar8 = FUN_005accf4(iVar6 + 0x108e8f8,*(undefined4 *)(iVar6 + 0x108e9d8));
          if (iVar8 == -1) break;
          *(char *)(param_1 + 0x59) = (char)*(undefined4 *)(iVar6 + 0x108e9f8);
          uVar10 = FUN_0000a05c(*(undefined4 *)(iVar6 + 0x108ea10));
          *(undefined1 *)(param_1 + 0x58) = uVar10;
          if ((*(byte *)(param_1 + 0x59) & 8) == 0) {
            if (((((*(byte *)(param_1 + 0x58) & 1) == 0) || ((*(byte *)(param_1 + 0x58) & 2) == 0))
                || ((*(byte *)(param_1 + 0x59) & 0x40) == 0)) ||
               (iVar6 = 0, (*(byte *)(param_1 + 0x59) & 0x80) != 0)) {
              iVar6 = -1;
              *(undefined4 *)(param_1 + 0x54) = 7;
            }
            goto LAB_00026388;
          }
          if (*(int *)(param_1 + 0x4c) == 0) {
            iVar6 = -1;
            *(undefined4 *)(param_1 + 0x54) = 5;
            goto LAB_00026388;
          }
          if (((*(byte *)(param_1 + 0x58) & 1) != 0) || ((*(byte *)(param_1 + 0x59) & 0x80) != 0)) {
            iVar6 = -1;
            *(undefined4 *)(param_1 + 0x54) = 6;
            goto LAB_00026388;
          }
          iVar8 = *(int *)(param_1 + 0x34) * 0x430;
          sVar9 = FUN_0000a05c(*(undefined4 *)(iVar8 + 0x108ea1c));
          *(short *)(param_1 + 0x5a) = sVar9 << 8;
          sVar9 = FUN_0000a05c(*(undefined4 *)(iVar8 + 0x108ea18));
          *(short *)(param_1 + 0x5a) = *(short *)(param_1 + 0x5a) + sVar9;
          if ((*(int *)(param_1 + 0x48) == 0) && (*(short *)(param_1 + 0x5a) != 0)) {
            *(undefined4 *)(param_1 + 0x54) = 8;
LAB_0002640c:
            iVar6 = -1;
            goto LAB_00026388;
          }
          uVar16 = *(int *)(param_1 + 0x48) - *(int *)(param_1 + 0x44);
          if (*(ushort *)(param_1 + 0x5a) < uVar16) {
            uVar16 = (uint)*(ushort *)(param_1 + 0x5a);
            iVar4 = *(int *)(param_1 + 0x4c);
            iVar17 = 0;
            if (iVar4 != 1) goto LAB_00026048;
LAB_00026168:
            if ((*(byte *)(param_1 + 0x58) & 2) != 0) goto LAB_00026400;
            FUN_0000a1a4(*(undefined4 *)(iVar8 + 0x108ea04),*(undefined4 *)(param_1 + 0x44),
                         uVar16 >> 1);
            for (; iVar17 != 0; iVar17 = iVar17 + -2) {
              auStack_38[0] = 0;
              FUN_0000a1a4(*(undefined4 *)(iVar8 + 0x108ea04),auStack_38,1);
            }
          }
          else {
            *(undefined4 *)(param_1 + 0x48) = 0;
            iVar17 = *(ushort *)(param_1 + 0x5a) - uVar16;
            iVar4 = *(int *)(param_1 + 0x4c);
            if (iVar4 == 1) goto LAB_00026168;
LAB_00026048:
            if ((iVar4 != 2) || ((*(byte *)(param_1 + 0x58) & 2) == 0)) {
LAB_00026400:
              *(undefined4 *)(param_1 + 0x54) = 10;
              goto LAB_0002640c;
            }
            FUN_0000a0dc(*(undefined4 *)(iVar8 + 0x108ea04),*(undefined4 *)(param_1 + 0x44),
                         uVar16 >> 1);
            for (; (iVar17 != 0 &&
                   (FUN_0000a0dc(*(undefined4 *)(iVar8 + 0x108ea04),auStack_38,1), iVar17 != 2));
                iVar17 = iVar17 + -4) {
              FUN_0000a0dc(*(undefined4 *)(iVar8 + 0x108ea04),auStack_38,1);
            }
          }
          *(uint *)(param_1 + 0x44) = *(int *)(param_1 + 0x44) + (uint)*(ushort *)(param_1 + 0x5a);
          *(int *)(param_1 + 0x50) = *(int *)(param_1 + 0x50) + 1;
        }
        iVar6 = -1;
        *(undefined4 *)(param_1 + 0x54) = 4;
      }
LAB_00026388:
      if (iVar6 == 0) {
        if (6 < iRam00e107b4) {
          FUN_00443f20(0xd3624c,*(undefined4 *)(param_1 + 0x34),uVar13,
                       **(undefined4 **)(param_2 + 0xc),*(undefined4 *)(param_1 + 0x44),
                       *(undefined4 *)(param_1 + 0x50),*param_2);
        }
        if (*(int *)(param_2 + 0xc) != 0) {
          if (*(int *)(param_1 + 0x48) == 0) {
            **(int **)(param_2 + 0xc) = **(int **)(param_2 + 0xc) + *(int *)(param_2 + 0x10);
          }
          else {
            **(undefined4 **)(param_2 + 0xc) = *(undefined4 *)(param_1 + 0x44);
          }
        }
        return 0;
      }
      goto LAB_00025e94;
    }
    uVar14 = 3;
  }
  *(undefined4 *)(param_1 + 0x54) = uVar14;
LAB_00025e94:
  if (8 < iRam00e107b4) {
    uVar14 = FUN_0000a05c(*(undefined4 *)(iVar12 + 0x108ea20));
    uVar7 = FUN_0000a05c(*(undefined4 *)(iVar12 + 0x108ea08));
    FUN_00443f20(0xd36208,*(undefined4 *)(param_1 + 0x34),uVar13,
                 *(undefined4 *)(*(int *)(param_1 + 0x54) * 4 + 0xe10740),
                 *(undefined1 *)(param_1 + 0x59),uVar14,uVar7);
  }
  if (8 < iRam00e107b4) {
    FUN_00443f20(0xd361a8,**(undefined4 **)(param_2 + 0xc),*(undefined4 *)(param_1 + 0x44),
                 *(undefined4 *)(param_1 + 0x50),*param_2,*(undefined1 *)(param_1 + 0x58),
                 *(undefined2 *)(param_1 + 0x5a));
  }
  return 0xffffffff;
}

