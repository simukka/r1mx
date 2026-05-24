/* 0x003950ac  FUN_003950ac  size=1256 bytes */


undefined4 FUN_003950ac(undefined4 param_1,uint param_2,int param_3,uint param_4)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  uint uVar7;
  uint *puVar8;
  int *piVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  undefined4 uVar18;
  longlong lVar19;
  undefined4 uStack_54;
  int iStack_50;
  int iStack_4c;
  undefined8 uStack_48;
  
  iVar3 = FUN_003938b0(uRam00e9c470);
  uStack_48._0_4_ = 0;
  uStack_48._4_4_ = 0;
  uVar13 = param_3 * uRam0108b7b4;
  FUN_00394068(iVar3,param_2,&uStack_54);
  iVar4 = (*pcRam01110ae0)(uStack_54,iVar3 + (param_2 >> (uRam0108b7bc & 0x3f)) * 4);
  lVar19 = CONCAT44(uStack_48._0_4_,uStack_48._4_4_);
  if (uVar13 != 0) {
    uVar18 = uStack_54;
    for (uVar17 = param_2; uStack_48 = lVar19, uVar17 < param_2 + uVar13;
        uVar17 = uVar17 + uRam0108b7b4) {
      uStack_54 = uVar18;
      FUN_00394068(iVar3,uVar17,&uStack_54);
      iVar5 = (*pcRam01110b20)(uStack_54);
      if (iVar5 != 0) {
        puVar6 = (undefined4 *)FUN_00442914();
        *puVar6 = 0x550007;
        return 0xffffffff;
      }
      iVar5 = (*pcRam01110ae8)(uStack_54);
      if (iVar5 == 0) {
        puVar6 = (undefined4 *)FUN_00442914();
        *puVar6 = 0x55000f;
        return 0xffffffff;
      }
      if (pcRam01110b30 != reset_vector) {
        iVar5 = (*pcRam01110b30)(uStack_54);
        if (iVar5 != 0) {
          puVar6 = (undefined4 *)FUN_00442914();
          *puVar6 = 0x55000d;
          return 0xffffffff;
        }
      }
      iVar5 = (*pcRam01110ae4)(uStack_54);
      if (iVar5 == 0) {
        puVar6 = (undefined4 *)FUN_00442914();
        *puVar6 = 0x550003;
        return 0xffffffff;
      }
      iVar5 = (*pcRam01110ae0)(uStack_54,iVar3 + (uVar17 >> (uRam0108b7bc & 0x3f)) * 4);
      if (iVar5 != iVar4) {
        puVar6 = (undefined4 *)FUN_00442914();
        *puVar6 = 0x55000b;
        return 0xffffffff;
      }
      if (pcRam01110aec != reset_vector) {
        uVar7 = (*pcRam01110aec)(uStack_54);
        if (uRam0108b7b4 < uVar7) {
          iStack_50 = 0xe272a8;
          FUN_005accf4(uRam00e272b4,0xffffffff);
          FUN_00394388(uRam00e9c470,uVar17);
          FUN_005ad104(*(undefined4 *)(iStack_50 + 0xc));
        }
      }
      lVar19 = (*pcRam01110af0)(uStack_54);
      if ((uStack_48 !=
           CONCAT44((int)((ulonglong)lVar19 >> 0x20) - (uint)((uint)lVar19 < uRam0108b7b4),
                    (uint)lVar19 - uRam0108b7b4)) && (uVar17 != param_2)) {
        puVar6 = (undefined4 *)FUN_00442914();
        *puVar6 = 0x55000a;
        return 0xffffffff;
      }
      uVar18 = uStack_54;
    }
    iStack_4c = 0xe272a8;
    FUN_005accf4(uRam00e272b8,0xffffffff);
    piVar2 = piRam00e272ac;
    uVar15 = *(uint *)(iStack_4c + 8);
    uVar17 = 0;
    uVar7 = 0;
    if (*piRam00e272ac != 0) {
      iVar4 = uVar15 + 1;
      piVar9 = piRam00e272ac;
      do {
        piVar9 = piVar9 + 1;
        iVar4 = iVar4 + -1;
        if (*piVar9 == 0) break;
      } while (iVar4 != 0);
      uVar7 = (uRam00e272b0 - iVar4) + 1;
    }
    if (uVar7 < uVar15) {
      puVar8 = (uint *)FUN_0045b974(uVar15 * 0xc);
      piVar2[uVar7] = (int)puVar8;
      if (puVar8 != (uint *)0x0) {
        FUN_0039acec(puVar8,0,uRam00e272b0 * 0xc);
        uVar7 = param_2;
        do {
          if (uVar13 == 0) {
            FUN_005ad104(uRam00e272b8);
            return 0;
          }
          uStack_54 = uVar18;
          FUN_00394068(iVar3,uVar7,&uStack_54);
          uVar15 = 0;
          uVar11 = uVar13;
          while ((uVar11 != 1 && (uVar15 = uVar15 + 1, (int)uVar15 < 0x1f))) {
            uVar11 = uVar13 >> (uVar15 & 0x3f);
          }
          uVar11 = 0;
          uVar12 = uVar7;
          while (((uVar12 & 1) == 0 && (uVar11 = uVar11 + 1, (int)uVar11 < 0x1f))) {
            uVar12 = uVar7 >> (uVar11 & 0x3f);
          }
          if ((int)uVar11 < (int)uVar15) {
            uVar15 = uVar11;
          }
          uVar15 = uVar15 - 10;
          bVar1 = false;
          uVar18 = uStack_54;
          while (!bVar1) {
            *puVar8 = uVar7;
            uVar11 = 1 << (uVar15 & 0x3f);
            if ((uVar11 & uRam0108b784) != 0) {
              if ((param_4 & 1) != 0) {
LAB_00395488:
                uVar12 = uVar11 * 0x400;
                *puVar8 = uVar7;
                puVar8[2] = param_4 & 1;
                uVar17 = uVar17 + 1;
                puVar8[1] = uVar12;
                puVar8 = puVar8 + 3;
                uVar14 = 0;
                uVar16 = uVar7;
                uStack_54 = uVar18;
                if (uVar12 != 0) {
                  do {
                    FUN_00394068(iVar3,uVar16,&uStack_54);
                    uVar10 = uRam0108b7b8;
                    if (uVar12 < uRam0108b7b8) {
                      uVar10 = uVar12;
                    }
                    (*pcRam01110b24)(uStack_54,uVar10,1,uRam00e272a8);
                    uVar14 = uVar14 + uRam0108b7b8;
                    uVar16 = uVar16 + uRam0108b7b8;
                  } while (uVar14 < uVar12);
                }
                uVar7 = uVar7 + uVar12;
                uVar13 = uVar13 + uVar11 * -0x400;
                bVar1 = true;
                uVar18 = uStack_54;
                goto LAB_00395528;
              }
              iVar4 = (*pcRam01110b18)(uVar18,uVar7,uVar11 << 10);
              if (iVar4 == 0) goto LAB_00395488;
              goto LAB_00395538;
            }
            uVar15 = uVar15 - 1;
LAB_00395528:
            if (uRam00e272b0 <= uVar17) {
LAB_00395538:
              puVar6 = (undefined4 *)FUN_00442914();
              *puVar6 = 0x550009;
              goto LAB_00395560;
            }
          }
        } while( true );
      }
    }
LAB_00395560:
    FUN_005ad104(uRam00e272b8);
    FUN_00394ef4(param_1,param_2,param_4);
  }
  return 0xffffffff;
}

