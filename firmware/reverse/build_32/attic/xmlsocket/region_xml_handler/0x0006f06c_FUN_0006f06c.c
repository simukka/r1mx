/* 0x0006f06c  FUN_0006f06c  size=3212 bytes */


undefined4 FUN_0006f06c(int param_1)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  undefined4 *****pppppuVar4;
  int iVar5;
  int iVar6;
  undefined1 *puVar7;
  undefined1 auStack_198 [8];
  undefined1 auStack_190 [16];
  undefined1 auStack_180 [16];
  undefined1 auStack_170 [8];
  uint uStack_168;
  undefined1 auStack_120 [4];
  undefined4 ****appppuStack_11c [4];
  uint uStack_10c;
  uint uStack_108;
  undefined1 auStack_100 [4];
  undefined4 ****appppuStack_fc [5];
  uint uStack_e8;
  undefined1 auStack_e0 [4];
  undefined4 uStack_dc;
  undefined4 uStack_c8;
  undefined4 uStack_c4;
  undefined1 *puStack_c0;
  undefined4 uStack_bc;
  undefined1 *puStack_b8;
  undefined1 *puStack_b4;
  int iStack_ac;
  int iStack_a8;
  int iStack_a4;
  int iStack_a0;
  undefined1 auStack_9c [4];
  undefined1 auStack_98 [4];
  undefined1 auStack_94 [4];
  undefined1 auStack_90 [4];
  undefined4 uStack_8c;
  int iStack_88;
  int iStack_84;
  int iStack_80;
  int iStack_7c;
  int iStack_74;
  int iStack_70;
  uint uStack_6c;
  uint uStack_68;
  uint uStack_64;
  uint uStack_60;
  uint uStack_5c;
  int iStack_58;
  undefined4 ****ppppuStack_54;
  int iStack_50;
  int iStack_4c;
  uint uStack_48;
  int iStack_44;
  int iStack_40;
  uint uStack_3c;
  uint uStack_38;
  uint uStack_34;
  int iStack_30;
  uint uStack_2c;
  uint uStack_28;
  int iStack_24;
  uint uStack_20;
  int iStack_1c;
  uint uStack_18;
  uint uStack_14;
  int iStack_10;
  uint uStack_c;
  
  puStack_b4 = &stack0xfffffe50;
  uStack_c8 = 0x25710c;
  puStack_c0 = auStack_198;
  uStack_c4 = 0xe96b40;
  uStack_bc = 0x7f2f0;
  puStack_b8 = (undefined1 *)register0x00000004;
  iStack_88 = param_1;
  FUN_003d1214(auStack_e0);
  iStack_7c = iStack_88 + 0xd8;
  uStack_dc = 0xffffffff;
  FUN_0005e784(3,0x200,6,0xd3e720,0x65dfd0,0x700,0xd52788,0x65dfe0);
  iStack_ac = iStack_88 + 0xdc;
  if (0xf < *(uint *)(iStack_7c + 0x18)) {
    iStack_ac = *(int *)(iStack_7c + 4);
  }
  iStack_a8 = iStack_7c + 4;
  if (0xf < *(uint *)(iStack_7c + 0x18)) {
    iStack_a8 = *(int *)(iStack_7c + 4);
  }
  iStack_a8 = iStack_a8 + *(int *)(iStack_7c + 0x14);
  iStack_a4 = iStack_7c + 4;
  if (0xf < *(uint *)(iStack_7c + 0x18)) {
    iStack_a4 = *(int *)(iStack_7c + 4);
  }
  iStack_74 = iStack_ac - iStack_a4;
  if (iStack_ac == 0) {
    iStack_74 = 0;
  }
  iVar6 = iStack_a8 - iStack_ac;
  if (iStack_a8 == 0) {
    iVar6 = 0;
  }
  uStack_dc = 0xffffffff;
  FUN_005f3808(iStack_7c,iStack_74,iVar6);
  iStack_a0 = iStack_7c + 4;
  if (0xf < *(uint *)(iStack_7c + 0x18)) {
    iStack_a0 = *(int *)(iStack_7c + 4);
  }
  iStack_a0 = iStack_a0 + iStack_74;
  iVar6 = iStack_88 + 0x88;
  if (0xf < *(uint *)(iStack_88 + 0x9c)) {
    iVar6 = *(int *)(iStack_88 + 0x88);
  }
  uStack_dc = 0xffffffff;
  iStack_84 = FUN_0044dea0(iVar6);
  if (iStack_84 == 0) {
    FUN_005ea3bc(auStack_100,0xd3f394);
    uStack_dc = 6;
    FUN_005f43dc(auStack_120,auStack_100,iStack_88 + 0x84);
    FUN_005e8e00(auStack_100);
    uStack_dc = 5;
    FUN_005f08cc(0xd3f3ac,auStack_120,6,0x65dfe0);
    FUN_0005eb3c(0xd3f3c8,0xd3f3e0,6,0x65dfe0);
    uStack_dc = 5;
    FUN_0005e784(0,3,6,0xd3e720,0x65dfd0,0x70c,0xd3f3e8,0x65dfe0);
    FUN_005e8e00(auStack_120);
    uStack_8c = 0xffffffff;
  }
  else {
    while( true ) {
      uStack_dc = 0xffffffff;
      iStack_80 = FUN_0044dd2c(iStack_84);
      if (iStack_80 == 0) break;
      uStack_dc = 0xffffffff;
      FUN_005f0cd8(auStack_120,iStack_88 + 0x84,0xd880c8);
      uStack_dc = 4;
      FUN_005f0cd8(auStack_100,auStack_120,iStack_80 + 4);
      FUN_005e8e00(auStack_120);
      pppppuVar4 = appppuStack_fc;
      if (0xf < uStack_e8) {
        pppppuVar4 = (undefined4 *****)appppuStack_fc[0];
      }
      uStack_dc = 3;
      iVar6 = FUN_0044df78(pppppuVar4,auStack_170);
      if (iVar6 == 0) {
        if ((uStack_168 & 0xf000) != 0x4000) {
          uStack_dc = 3;
          FUN_0005e784(3,0x200,6,0xd3e720,0x65dfd0,0x721,0xd3f360,0x65dfe0);
          goto LAB_0006f2e4;
        }
        iStack_70 = iStack_80 + 4;
        uStack_dc = 3;
        iVar6 = FUN_003c9eac(iStack_70,0xd3f414,auStack_198,auStack_9c,auStack_98,auStack_94,
                             auStack_90,auStack_180);
        if (iVar6 != 8) {
          FUN_0005e784(3,0x200,6,0xd3e720,0x65dfd0,0x72b,0xd3f434,0x65dfe0);
          goto LAB_0006f2e4;
        }
        uStack_dc = 3;
        FUN_005ea3bc(auStack_120,auStack_190);
        uStack_68 = uStack_10c;
        uStack_64 = FUN_0039b0f0(uRam00d94d4c);
        uVar3 = 0;
        if (uStack_68 != 0) {
          pppppuVar4 = appppuStack_11c;
          if (0xf < uStack_108) {
            pppppuVar4 = (undefined4 *****)appppuStack_11c[0];
          }
          uVar3 = uStack_64;
          if (uStack_68 < uStack_64) {
            uVar3 = uStack_68;
          }
          uVar3 = FUN_0039ac2c(pppppuVar4,uRam00d94d4c,uVar3);
        }
        if ((uVar3 == 0) && (uVar3 = (uint)(uStack_68 != uStack_64), uStack_68 < uStack_64)) {
          uVar3 = 0xffffffff;
        }
        uStack_6c = uVar3 == 0 ^ 1;
        FUN_005e8e00(auStack_120);
        if (uStack_6c != 0) {
          uStack_dc = 3;
          FUN_0005e784(3,0x200,6,0xd3e720,0x65dfd0,0x733,0xd3f450,0x65dfe0);
          goto LAB_0006f2e4;
        }
        uStack_dc = 3;
        FUN_005ea3bc(auStack_120,iStack_80 + 4);
        uStack_60 = FUN_0039b0f0(uRam00d94d50);
        iVar6 = 0;
        if (uStack_60 != 0) {
          if ((uStack_10c != 0) && (uStack_5c = uStack_10c, uStack_60 <= uStack_10c)) {
            uStack_5c = (uStack_10c - uStack_60) + 1;
            ppppuStack_54 = appppuStack_11c;
            if (0xf < uStack_108) {
              ppppuStack_54 = appppuStack_11c[0];
            }
            while (iStack_58 = FUN_0039abf8(ppppuStack_54,uRam00d3ca88,uStack_5c),
                  iStack_50 = iStack_58, iStack_58 != 0) {
              iVar6 = FUN_0039ac2c(iStack_58,uRam00d94d50,uStack_60);
              if (iVar6 == 0) {
                pppppuVar4 = appppuStack_11c;
                if (0xf < uStack_108) {
                  pppppuVar4 = (undefined4 *****)appppuStack_11c[0];
                }
                iVar6 = iStack_58 - (int)pppppuVar4;
                goto LAB_0006f790;
              }
              uStack_5c = (int)ppppuStack_54 + (uStack_5c - iStack_50) + -1;
              ppppuStack_54 = (undefined4 ****)(iStack_50 + 1);
            }
          }
          iVar6 = -1;
        }
LAB_0006f790:
        if (iVar6 != -1) {
          uStack_dc = 1;
          FUN_005f3808(auStack_120,iVar6,0xffffffff);
        }
        uStack_dc = 1;
        FUN_0005e784(3,0x200,6,0xd3e720,0x65dfd0,0x73e,0xd3f488,0x65dfe0);
        if (*(int *)(iStack_88 + 0xec) != 0) {
          iStack_4c = iStack_88 + 0xd8;
          uStack_48 = FUN_0039b0f0(uRam00d94d54);
          uVar3 = iStack_88 + 0xdc;
          if (0xf < *(uint *)(iStack_4c + 0x18)) {
            uVar3 = *(uint *)(iStack_4c + 4);
          }
          if (uRam00d94d54 < uVar3) {
LAB_0006fb5c:
            bVar1 = false;
          }
          else {
            iVar6 = iStack_4c + 4;
            if (0xf < *(uint *)(iStack_4c + 0x18)) {
              iVar6 = *(int *)(iStack_4c + 4);
            }
            bVar1 = true;
            if ((uint)(iVar6 + *(int *)(iStack_4c + 0x14)) <= uRam00d94d54) goto LAB_0006fb5c;
          }
          if (bVar1) {
            iStack_44 = iStack_4c;
            iStack_40 = iStack_4c;
            iVar6 = iStack_4c + 4;
            if (0xf < *(uint *)(iStack_4c + 0x18)) {
              iVar6 = *(int *)(iStack_4c + 4);
            }
            uStack_3c = 0xd7ce94 - iVar6;
            uStack_38 = uStack_48;
            if (*(uint *)(iStack_4c + 0x14) < uStack_3c) {
              uStack_dc = 1;
              FUN_00250ea4(iStack_4c);
            }
            uStack_34 = *(int *)(iStack_40 + 0x14) - uStack_3c;
            if (uStack_34 < uStack_48) {
              uStack_38 = uStack_34;
            }
            if (~*(uint *)(iStack_44 + 0x14) <= uStack_38) {
              uStack_dc = 1;
              FUN_002513e0(iStack_44);
            }
            if (uStack_38 != 0) {
              iStack_30 = iStack_44;
              uStack_34 = *(int *)(iStack_44 + 0x14) + uStack_38;
              uStack_2c = uStack_34;
              if (0xfffffffe < uStack_34) {
                uStack_dc = 1;
                FUN_002513e0(iStack_44);
              }
              if (*(uint *)(iStack_44 + 0x18) < uStack_34) {
                uStack_dc = 1;
                FUN_005e7bb8(iStack_44,uStack_34,*(undefined4 *)(iStack_44 + 0x14));
              }
              else if (uStack_2c == 0) {
                puVar7 = (undefined1 *)(iStack_30 + 4);
                if (0xf < *(uint *)(iStack_30 + 0x18)) {
                  puVar7 = *(undefined1 **)(iStack_30 + 4);
                }
                *(undefined4 *)(iStack_30 + 0x14) = 0;
                *puVar7 = 0;
              }
              if (uStack_2c != 0) {
                iVar6 = iStack_44 + 4;
                if (0xf < *(uint *)(iStack_44 + 0x18)) {
                  iVar6 = *(int *)(iStack_44 + 4);
                }
                iVar5 = iStack_40 + 4;
                if (0xf < *(uint *)(iStack_40 + 0x18)) {
                  iVar5 = *(int *)(iStack_40 + 4);
                }
                FUN_0039ac74(iVar6 + *(int *)(iStack_44 + 0x14),iVar5 + uStack_3c,uStack_38);
                uVar2 = *(uint *)(iStack_44 + 0x18);
                iVar6 = iStack_44;
                uVar3 = uStack_34;
LAB_0006f9f8:
                iVar5 = iVar6 + 4;
                if (0xf < uVar2) {
                  iVar5 = *(int *)(iVar6 + 4);
                }
                *(uint *)(iVar6 + 0x14) = uVar3;
                *(undefined1 *)(iVar5 + uVar3) = 0;
              }
            }
          }
          else {
            if (~*(uint *)(iStack_4c + 0x14) <= uStack_48) {
              uStack_dc = 1;
              FUN_002513e0(iStack_4c);
            }
            if (uStack_48 != 0) {
              iStack_24 = iStack_4c;
              uStack_28 = *(int *)(iStack_4c + 0x14) + uStack_48;
              uStack_20 = uStack_28;
              if (0xfffffffe < uStack_28) {
                uStack_dc = 1;
                FUN_002513e0(iStack_4c);
              }
              if (*(uint *)(iStack_4c + 0x18) < uStack_28) {
                uStack_dc = 1;
                FUN_005e7bb8(iStack_4c,uStack_28,*(undefined4 *)(iStack_4c + 0x14));
              }
              else if (uStack_20 == 0) {
                puVar7 = (undefined1 *)(iStack_24 + 4);
                if (0xf < *(uint *)(iStack_24 + 0x18)) {
                  puVar7 = *(undefined1 **)(iStack_24 + 4);
                }
                *(undefined4 *)(iStack_24 + 0x14) = 0;
                *puVar7 = 0;
              }
              if (uStack_20 != 0) {
                iVar6 = iStack_4c + 4;
                if (0xf < *(uint *)(iStack_4c + 0x18)) {
                  iVar6 = *(int *)(iStack_4c + 4);
                }
                FUN_0039ac74(iVar6 + *(int *)(iStack_4c + 0x14),uRam00d94d54,uStack_48);
                uVar2 = *(uint *)(iStack_4c + 0x18);
                iVar6 = iStack_4c;
                uVar3 = uStack_28;
                goto LAB_0006f9f8;
              }
            }
          }
        }
        iStack_1c = iStack_88 + 0xd8;
        uStack_14 = uStack_10c;
        uStack_18 = 0xffffffff;
        if (uStack_10c != 0xffffffff) {
          uStack_18 = uStack_10c;
        }
        if (~*(uint *)(iStack_88 + 0xec) <= uStack_18) {
          uStack_dc = 1;
          FUN_002513e0(iStack_1c);
        }
        if (uStack_18 != 0) {
          iStack_10 = iStack_1c;
          uStack_14 = *(int *)(iStack_1c + 0x14) + uStack_18;
          uStack_c = uStack_14;
          if (0xfffffffe < uStack_14) {
            uStack_dc = 1;
            FUN_002513e0(iStack_1c);
          }
          if (*(uint *)(iStack_1c + 0x18) < uStack_14) {
            uStack_dc = 1;
            FUN_005e7bb8(iStack_1c,uStack_14,*(undefined4 *)(iStack_1c + 0x14));
          }
          else if (uStack_c == 0) {
            puVar7 = (undefined1 *)(iStack_10 + 4);
            if (0xf < *(uint *)(iStack_10 + 0x18)) {
              puVar7 = *(undefined1 **)(iStack_10 + 4);
            }
            *(undefined4 *)(iStack_10 + 0x14) = 0;
            *puVar7 = 0;
          }
          if (uStack_c != 0) {
            iVar6 = iStack_1c + 4;
            if (0xf < *(uint *)(iStack_1c + 0x18)) {
              iVar6 = *(int *)(iStack_1c + 4);
            }
            pppppuVar4 = appppuStack_11c;
            if (0xf < uStack_108) {
              pppppuVar4 = (undefined4 *****)appppuStack_11c[0];
            }
            FUN_0039ac74(iVar6 + *(int *)(iStack_1c + 0x14),pppppuVar4,uStack_18);
            iVar6 = iStack_1c + 4;
            if (0xf < *(uint *)(iStack_1c + 0x18)) {
              iVar6 = *(int *)(iStack_1c + 4);
            }
            *(uint *)(iStack_1c + 0x14) = uStack_14;
            *(undefined1 *)(iVar6 + uStack_14) = 0;
          }
        }
        FUN_005e8e00(auStack_120);
        FUN_005e8e00(auStack_100);
      }
      else {
        FUN_0005e784(3,0x200,6,0xd3e720,0x65dfd0,0x719,0xd3f37c,0x65dfe0);
LAB_0006f2e4:
        FUN_005e8e00(auStack_100);
      }
    }
    uStack_dc = 0xffffffff;
    FUN_0044de3c(iStack_84);
    uStack_dc = 0xffffffff;
    FUN_0005e784(3,0x200,6,0xd3e720,0x65dfd0,0x746,0xd3f470,0x65dfe0);
    uStack_8c = 0;
  }
  FUN_003d12b8(auStack_e0);
  return uStack_8c;
}

