/* 0x00024d5c  FUN_00024d5c  size=2720 bytes */


undefined4 FUN_00024d5c(int param_1,int param_2,int param_3,uint param_4,uint param_5)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  int iVar18;
  uint uStack_5c;
  uint uStack_58;
  uint uStack_54;
  uint uStack_50;
  
  iVar2 = *(int *)(param_1 + 0x34) * 0x430;
  iVar3 = (*(int *)(param_1 + 0x34) + *(int *)(param_1 + 0x38)) * 0x14;
  iVar15 = *(int *)(param_1 + 0x38) * 600 + iVar2 + 0x108e6a0;
  uStack_58 = 0;
  uStack_54 = 0;
  uStack_50 = 0;
  uVar5 = 0xffffffff;
  if (*(int *)(iVar2 + 0x108e9e4) != 0) {
    if (4 < iRam00e107b4) {
      FUN_00443f20(0xd360e0,*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),
                   ((int)(((int)param_5 >> 0x1f) - ((int)param_5 >> 0x1f ^ param_5)) >> 0x1f & 5U) +
                   0x72,param_2,param_3,param_4);
    }
    iVar6 = FUN_000239c8(*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38));
    uVar5 = 0xffffffff;
    if (iVar6 != -1) {
      if ((*(int *)(param_1 + 0x18) < param_2 + param_3) && (8 < iRam00e107b4)) {
        FUN_00443f20(0xd36130,param_2,param_3,*(int *)(param_1 + 0x18),0,0,0);
      }
      iVar6 = iVar2 + 0x108e964;
      iVar11 = 0;
      uVar16 = param_2 + *(int *)(param_1 + 0x3c);
      FUN_005accf4(iVar6,0xffffffff);
      bVar1 = 0 < param_3;
      while (iVar7 = iRam00d94c8c, bVar1) {
        uVar14 = 0;
        uVar13 = 0;
        uVar17 = uVar16;
        if (*(short *)(iVar15 + 0x208) == 0) {
          uVar13 = uVar16 & 0xff;
          uVar14 = uVar16 >> 0x18 & 0xf;
          uVar17 = uVar16 >> 8 & 0xffff;
          if (*(short *)(iVar15 + 0x206) == 0) {
            iVar12 = *(int *)(iVar3 + 0xe0bb2c) * *(int *)(iVar3 + 0xe0bb28);
            iVar12 = uVar16 - ((int)uVar16 / iVar12) * iVar12;
            uVar14 = iVar12 / *(int *)(iVar3 + 0xe0bb2c);
            uVar17 = (int)uVar16 / (*(int *)(iVar3 + 0xe0bb2c) * *(int *)(iVar3 + 0xe0bb28));
            uVar13 = (iVar12 - (iVar12 / *(int *)(iVar3 + 0xe0bb2c)) * *(int *)(iVar3 + 0xe0bb2c)) +
                     1;
          }
        }
        iVar12 = 0;
        iVar18 = 0;
        if (*(int *)(iVar2 + 0x108ea50) == 0) {
          if (*(short *)(iVar15 + 0x208) == 0) {
            iVar4 = param_3 - iVar11;
            if (0x100 < iVar4) {
              iVar4 = 0x100;
            }
          }
          else {
            iVar4 = param_3 - iVar11;
            if (0x10000 < iVar4) {
              iVar4 = 0x10000;
            }
          }
LAB_00024eec:
          if (*(short *)(iVar15 + 0x216) < 0x20) goto LAB_00024ef8;
LAB_00025088:
          if ((iRam00e107c8 == 0 || param_5 != 0) || ((param_4 & 0x1f) == 0)) {
            while (iVar8 = FUN_00024734(*(undefined4 *)(param_1 + 0x34),
                                        *(undefined4 *)(param_1 + 0x38),uVar17,uVar14,uVar13,param_4
                                        ,iVar4,param_5), iVar8 != 0) {
              if (((*(int *)(param_1 + 0x34) == 0) && (iRam00e9c3b8 == 0xaa)) ||
                 ((*(int *)(param_1 + 0x34) == 1 && (*(int *)(iVar7 + 4) == 0xaa)))) {
                uVar5 = 0xd36114;
                goto LAB_00025368;
              }
              iVar18 = iVar18 + 1;
              if (iRam00e107c4 < iVar18) {
                FUN_00020988(*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0x10,0,
                             0);
                iVar12 = iVar12 + 1;
                if (iRam00e107c4 < iVar12) goto LAB_00024f94;
                iVar18 = 0;
                while( true ) {
                  iVar18 = iVar18 + 1;
                  iVar8 = FUN_00020988(*(undefined4 *)(param_1 + 0x34),
                                       *(undefined4 *)(param_1 + 0x38),0x70,uVar17,uVar14);
                  if (iVar8 == 0) break;
                  if (iRam00e107c4 < iVar18) {
                    FUN_00442990(5);
                    goto LAB_00024f9c;
                  }
                }
                iVar18 = 0;
              }
            }
          }
          else {
            if (*(short *)(iVar15 + 0x208) == 0) {
              if (*(short *)(iVar15 + 0x206) == 0) {
                iVar7 = *(int *)(iVar3 + 0xe0bb2c) * *(int *)(iVar3 + 0xe0bb28);
                iVar7 = uVar16 - ((int)uVar16 / iVar7) * iVar7;
                uStack_5c = iVar7 / *(int *)(iVar3 + 0xe0bb2c);
                uVar10 = (int)uVar16 / (*(int *)(iVar3 + 0xe0bb2c) * *(int *)(iVar3 + 0xe0bb28));
                uVar9 = (iVar7 - (iVar7 / *(int *)(iVar3 + 0xe0bb2c)) * *(int *)(iVar3 + 0xe0bb2c))
                        + 1;
                if (*(int *)(iVar15 + 0x228) < iVar4) {
                  iVar7 = *(int *)(iVar3 + 0xe0bb2c) * *(int *)(iVar3 + 0xe0bb28);
                  iVar8 = (uVar16 + iVar4) - *(int *)(iVar15 + 0x228);
                  iVar8 = iVar8 - (iVar8 / iVar7) * iVar7;
                  uStack_58 = (int)((uVar16 + iVar4) - *(int *)(iVar15 + 0x228)) /
                              (*(int *)(iVar3 + 0xe0bb2c) * *(int *)(iVar3 + 0xe0bb28));
                  uStack_54 = iVar8 / *(int *)(iVar3 + 0xe0bb2c);
                  uStack_50 = (iVar8 - (iVar8 / *(int *)(iVar3 + 0xe0bb2c)) *
                                       *(int *)(iVar3 + 0xe0bb2c)) + 1;
                  if (*(int *)(iVar15 + 0x228) << 1 < iVar4) {
                    iVar8 = *(int *)(iVar15 + 0x228) + uVar16;
                    iVar7 = *(int *)(iVar3 + 0xe0bb2c) * *(int *)(iVar3 + 0xe0bb28);
                    iVar8 = iVar8 - (iVar8 / iVar7) * iVar7;
                    uVar14 = iVar8 / *(int *)(iVar3 + 0xe0bb2c);
                    uVar17 = (int)(*(int *)(iVar15 + 0x228) + uVar16) /
                             (*(int *)(iVar3 + 0xe0bb2c) * *(int *)(iVar3 + 0xe0bb28));
                    uVar13 = (iVar8 - (iVar8 / *(int *)(iVar3 + 0xe0bb2c)) *
                                      *(int *)(iVar3 + 0xe0bb2c)) + 1;
                  }
                }
              }
              else {
                uVar9 = uVar16 & 0xff;
                uStack_5c = uVar16 >> 0x18 & 0xf;
                uVar10 = uVar16 >> 8 & 0xffff;
                if (*(int *)(iVar15 + 0x228) < iVar4) {
                  iVar7 = uVar16 + iVar4;
                  uStack_50 = iVar7 - *(int *)(iVar15 + 0x228) & 0xff;
                  uStack_54 = (uint)(iVar7 - *(int *)(iVar15 + 0x228)) >> 0x18 & 0xf;
                  uStack_58 = (uint)(iVar7 - *(int *)(iVar15 + 0x228)) >> 8 & 0xffff;
                  if (*(int *)(iVar15 + 0x228) << 1 < iVar4) {
                    uVar13 = *(int *)(iVar15 + 0x228) + uVar16 & 0xff;
                    uVar14 = *(int *)(iVar15 + 0x228) + uVar16 >> 0x18 & 0xf;
                    uVar17 = *(int *)(iVar15 + 0x228) + uVar16 >> 8 & 0xffff;
                  }
                }
              }
            }
            else {
              uStack_5c = 0;
              uVar9 = 0;
              uVar10 = uVar16;
              if (*(int *)(iVar15 + 0x228) < iVar4) {
                uStack_58 = (uVar16 + iVar4) - *(int *)(iVar15 + 0x228);
                uStack_54 = 0;
                uStack_50 = 0;
                if (*(int *)(iVar15 + 0x228) << 1 < iVar4) {
                  uVar14 = 0;
                  uVar17 = *(int *)(iVar15 + 0x228) + uVar16;
                  uVar13 = 0;
                }
              }
            }
            while (iVar8 = FUN_00024734(*(undefined4 *)(param_1 + 0x34),
                                        *(undefined4 *)(param_1 + 0x38),uVar10,uStack_5c,uVar9,
                                        *(undefined4 *)(iVar15 + 0x22c),
                                        *(undefined4 *)(iVar15 + 0x228),param_5),
                  iVar7 = iRam00d94c8c, iVar8 != 0) {
              if (((*(int *)(param_1 + 0x34) == 0) && (iRam00e9c3b8 == 0xaa)) ||
                 ((*(int *)(param_1 + 0x34) == 1 && (iRam00e9c3bc == 0xaa)))) {
                uVar5 = 0xd36150;
                goto LAB_00025368;
              }
              iVar18 = iVar18 + 1;
              if (iRam00e107c4 < iVar18) {
                FUN_00020988(*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0x10,0,
                             0);
                iVar12 = iVar12 + 1;
                if (iRam00e107c4 < iVar12) goto LAB_00024f94;
                iVar7 = 0;
                while( true ) {
                  iVar7 = iVar7 + 1;
                  iVar18 = FUN_00020988(*(undefined4 *)(param_1 + 0x34),
                                        *(undefined4 *)(param_1 + 0x38),0x70,uVar17,uVar14);
                  if (iVar18 == 0) break;
                  if (iRam00e107c4 < iVar7) {
                    FUN_00442990(5);
                    goto LAB_00024f9c;
                  }
                }
                iVar18 = 0;
              }
            }
            if (*(int *)(iVar15 + 0x228) << 1 < iVar4) {
              while (iVar8 = FUN_00024734(*(undefined4 *)(param_1 + 0x34),
                                          *(undefined4 *)(param_1 + 0x38),uVar17,uVar14,uVar13,
                                          *(int *)(iVar3 + 0xe0bb30) * *(int *)(iVar15 + 0x228) +
                                          param_4,iVar4 + *(int *)(iVar15 + 0x228) * -2,param_5),
                    iVar8 != 0) {
                if (((*(int *)(param_1 + 0x34) == 0) && (iRam00e9c3b8 == 0xaa)) ||
                   ((*(int *)(param_1 + 0x34) == 1 && (*(int *)(iVar7 + 4) == 0xaa)))) {
                  uVar5 = 0xd36170;
                  goto LAB_00025368;
                }
                iVar18 = iVar18 + 1;
                if (iRam00e107c4 < iVar18) {
                  FUN_00020988(*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0x10,
                               0,0);
                  iVar12 = iVar12 + 1;
                  if (iRam00e107c4 < iVar12) goto LAB_00024f94;
                  iVar18 = 0;
                  while( true ) {
                    iVar18 = iVar18 + 1;
                    iVar8 = FUN_00020988(*(undefined4 *)(param_1 + 0x34),
                                         *(undefined4 *)(param_1 + 0x38),0x70,uVar17,uVar14);
                    if (iVar8 == 0) break;
                    if (iRam00e107c4 < iVar18) {
                      FUN_00442990(5);
                      goto LAB_00024f9c;
                    }
                  }
                  iVar18 = 0;
                }
              }
            }
            iVar7 = iRam00d94c8c;
            if (*(int *)(iVar15 + 0x228) < iVar4) {
              while (iVar8 = FUN_00024734(*(undefined4 *)(param_1 + 0x34),
                                          *(undefined4 *)(param_1 + 0x38),uStack_58,uStack_54,
                                          uStack_50,*(undefined4 *)(iVar15 + 0x230),
                                          *(undefined4 *)(iVar15 + 0x228),param_5), iVar8 != 0) {
                if (((*(int *)(param_1 + 0x34) == 0) && (iRam00e9c3b8 == 0xaa)) ||
                   ((*(int *)(param_1 + 0x34) == 1 && (*(int *)(iVar7 + 4) == 0xaa)))) {
                  uVar5 = 0xd3618c;
LAB_00025368:
                  FUN_00443f20(uVar5,1,2,3,4,5,6);
                  FUN_00442990(5);
                  goto LAB_00024f9c;
                }
                iVar18 = iVar18 + 1;
                if (iRam00e107c4 < iVar18) {
                  FUN_00020988(*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0x10,
                               0,0);
                  iVar12 = iVar12 + 1;
                  if (iRam00e107c4 < iVar12) goto LAB_00024f94;
                  iVar18 = 0;
                  while( true ) {
                    iVar18 = iVar18 + 1;
                    iVar8 = FUN_00020988(*(undefined4 *)(param_1 + 0x34),
                                         *(undefined4 *)(param_1 + 0x38),0x70,uVar17,uVar14);
                    if (iVar8 == 0) break;
                    if (iRam00e107c4 < iVar18) {
                      FUN_00442990(5);
                      goto LAB_00024f9c;
                    }
                  }
                  iVar18 = 0;
                }
              }
            }
            FUN_0036c8ac(*(undefined4 *)(iVar15 + 0x22c),param_4,
                         *(int *)(iVar3 + 0xe0bb30) * *(int *)(iVar15 + 0x228));
            if (*(int *)(iVar15 + 0x228) < iVar4) {
              FUN_0036c8ac(*(undefined4 *)(iVar15 + 0x230),
                           (iVar4 - *(int *)(iVar15 + 0x228)) * *(int *)(iVar3 + 0xe0bb30) + param_4
                           ,*(int *)(iVar3 + 0xe0bb30) * *(int *)(iVar15 + 0x228));
            }
          }
        }
        else {
          iVar4 = param_3 - iVar11;
          if (iVar4 < *(int *)(iVar2 + 0x108ea50)) goto LAB_00024eec;
          iVar4 = *(int *)(iVar2 + 0x108ea50);
          if (0x1f < *(short *)(iVar15 + 0x216)) goto LAB_00025088;
LAB_00024ef8:
          while (iVar7 = FUN_00021e90(*(undefined4 *)(param_1 + 0x34),
                                      *(undefined4 *)(param_1 + 0x38),uVar17,uVar14,uVar13,param_4,
                                      iVar4,param_5), iVar7 != 0) {
            iVar18 = iVar18 + 1;
            if (iRam00e107c4 < iVar18) {
              FUN_00020988(*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0x10,0,0)
              ;
              iVar12 = iVar12 + 1;
              if (iRam00e107c4 < iVar12) {
LAB_00024f94:
                FUN_00442990(5);
LAB_00024f9c:
                FUN_005ad104(iVar6);
                return 0xffffffff;
              }
              iVar7 = 0;
              while( true ) {
                iVar7 = iVar7 + 1;
                iVar18 = FUN_00020988(*(undefined4 *)(param_1 + 0x34),
                                      *(undefined4 *)(param_1 + 0x38),0x70,uVar17,uVar14);
                if (iVar18 == 0) break;
                if (iRam00e107c4 < iVar7) goto LAB_00024f94;
              }
              iVar18 = 0;
            }
          }
        }
        iVar11 = iVar11 + iVar4;
        bVar1 = iVar11 < param_3;
        param_4 = param_4 + *(int *)(param_1 + 0x1c) * iVar4;
        uVar16 = uVar16 + iVar4;
      }
      FUN_005ad104(iVar6);
      uVar5 = 0;
    }
  }
  return uVar5;
}

