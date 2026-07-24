/* 0x00124fc8  FUN_00124fc8  size=3696 bytes */


/* WARNING: Restarted to delay deadcode elimination for space: stack */

int FUN_00124fc8(undefined4 param_1,int *param_2)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  char ****ppppcVar4;
  undefined4 ****ppppuVar5;
  undefined4 uVar6;
  undefined1 *puVar7;
  undefined1 *puVar8;
  char ****ppppcVar9;
  undefined1 auStack_238 [8];
  undefined1 auStack_230 [4];
  int *piStack_22c;
  undefined1 auStack_220 [4];
  char ***apppcStack_21c [4];
  int iStack_20c;
  uint uStack_208;
  undefined1 auStack_200 [32];
  undefined1 auStack_1e0 [4];
  undefined4 ***apppuStack_1dc [4];
  uint uStack_1cc;
  uint uStack_1c8;
  undefined1 auStack_1c0 [32];
  undefined1 auStack_1a0 [4];
  undefined4 ***apppuStack_19c [4];
  uint uStack_18c;
  uint uStack_188;
  undefined1 auStack_180 [88];
  uint uStack_128;
  undefined1 auStack_f0 [4];
  int iStack_ec;
  undefined4 uStack_d8;
  undefined4 uStack_d4;
  undefined1 *puStack_d0;
  undefined4 uStack_cc;
  int iStack_ac;
  int iStack_a8;
  char ***pppcStack_a4;
  char ***pppcStack_a0;
  undefined1 uStack_9c;
  undefined1 uStack_9b;
  char ***pppcStack_98;
  int iStack_94;
  undefined4 uStack_90;
  int *piStack_8c;
  int iStack_88;
  int iStack_84;
  int *piStack_80;
  int iStack_7c;
  int iStack_78;
  uint uStack_74;
  undefined1 *puStack_70;
  undefined1 *puStack_6c;
  uint uStack_68;
  uint uStack_64;
  uint uStack_60;
  uint uStack_5c;
  int iStack_54;
  uint uStack_50;
  uint uStack_4c;
  int *piStack_48;
  int iStack_44;
  int iStack_40;
  uint uStack_3c;
  undefined1 *puStack_38;
  undefined1 *puStack_34;
  uint uStack_30;
  uint uStack_2c;
  uint uStack_28;
  uint uStack_24;
  int iStack_20;
  uint uStack_1c;
  uint uStack_18;
  int *piStack_c;
  
  uStack_d8 = 0x25710c;
  iStack_88 = -1;
  puStack_d0 = auStack_238;
  uStack_cc = 0x135318;
  uStack_d4 = 0xe9926e;
  uStack_90 = param_1;
  piStack_8c = param_2;
  FUN_003d1214(auStack_f0);
  iStack_ec = iStack_88;
  uVar6 = FUN_0005e890();
  FUN_005e817c(auStack_230,uVar6,uStack_90);
  iStack_84 = *piStack_8c;
  FUN_005e8e80(auStack_220);
  FUN_005e8e80(auStack_200);
  iVar3 = -1;
  if (piStack_22c != (int *)0x0) {
    iStack_ec = 0xd;
    piStack_80 = piStack_22c;
    iStack_78 = -1;
    FUN_005f4290(auStack_1a0,0xea09a4);
    uStack_74 = FUN_0039b0f0(ppppuRam00d95188);
    ppppuVar5 = apppuStack_19c;
    if (0xf < uStack_188) {
      ppppuVar5 = (undefined4 ****)apppuStack_19c[0];
    }
    if (ppppuRam00d95188 < ppppuVar5) {
LAB_00125278:
      bVar1 = false;
    }
    else {
      ppppuVar5 = apppuStack_19c;
      if (0xf < uStack_188) {
        ppppuVar5 = (undefined4 ****)apppuStack_19c[0];
      }
      bVar1 = true;
      if ((undefined4 ****)((int)ppppuVar5 + uStack_18c) <= ppppuRam00d95188) goto LAB_00125278;
    }
    if (bVar1) {
      puStack_70 = auStack_1a0;
      ppppuVar5 = apppuStack_19c;
      if (0xf < uStack_188) {
        ppppuVar5 = (undefined4 ****)apppuStack_19c[0];
      }
      uStack_68 = 0xdb8b44 - (int)ppppuVar5;
      puStack_6c = puStack_70;
      uStack_64 = uStack_74;
      if (uStack_18c < uStack_68) {
        iStack_ec = 0xc;
        FUN_00250ea4(puStack_70);
      }
      uStack_60 = *(int *)(puStack_6c + 0x14) - uStack_68;
      if (uStack_60 < uStack_74) {
        uStack_64 = uStack_60;
      }
      if (~*(uint *)(puStack_70 + 0x14) <= uStack_64) {
        iStack_ec = 0xc;
        FUN_002513e0(puStack_70);
      }
      puVar7 = puStack_70;
      if (uStack_64 != 0) {
        uStack_60 = *(int *)(puStack_70 + 0x14) + uStack_64;
        iStack_ec = 0xc;
        iVar3 = FUN_005f0030(puStack_70,uStack_60,0);
        puVar7 = puStack_70;
        if (iVar3 != 0) {
          puVar7 = puStack_70 + 4;
          if (0xf < *(uint *)(puStack_70 + 0x18)) {
            puVar7 = *(undefined1 **)(puStack_70 + 4);
          }
          puVar8 = puStack_6c + 4;
          if (0xf < *(uint *)(puStack_6c + 0x18)) {
            puVar8 = *(undefined1 **)(puStack_6c + 4);
          }
          FUN_0039ac74(puVar7 + *(int *)(puStack_70 + 0x14),puVar8 + uStack_68,uStack_64);
          uVar2 = uStack_60;
          puVar7 = puStack_70 + 4;
          if (0xf < *(uint *)(puStack_70 + 0x18)) {
            puVar7 = *(undefined1 **)(puStack_70 + 4);
          }
          *(uint *)(puStack_70 + 0x14) = uStack_60;
          puVar7[uVar2] = 0;
          puVar7 = puStack_70;
        }
      }
    }
    else {
      if (~uStack_18c <= uStack_74) {
        iStack_ec = 0xc;
        FUN_002513e0(auStack_1a0);
      }
      if (uStack_74 != 0) {
        uStack_5c = uStack_18c + uStack_74;
        iStack_ec = 0xc;
        iVar3 = FUN_005f0030(auStack_1a0,uStack_5c,0);
        if (iVar3 != 0) {
          ppppuVar5 = apppuStack_19c;
          if (0xf < uStack_188) {
            ppppuVar5 = (undefined4 ****)apppuStack_19c[0];
          }
          FUN_0039ac74((int)ppppuVar5 + uStack_18c,ppppuRam00d95188,uStack_74);
          ppppuVar5 = apppuStack_19c;
          if (0xf < uStack_188) {
            ppppuVar5 = (undefined4 ****)apppuStack_19c[0];
          }
          uStack_18c = uStack_5c;
          *(undefined1 *)((int)ppppuVar5 + uStack_5c) = 0;
        }
      }
      puVar7 = auStack_1a0;
    }
    iStack_ec = 0xc;
    FUN_005f4290(auStack_1c0,puVar7);
    FUN_005e8e00(auStack_1a0);
    iStack_ec = 0xb;
    iStack_54 = 0xea0870;
    FUN_005f4290(auStack_1a0,auStack_1c0);
    uStack_4c = *(uint *)(iStack_54 + 0x14);
    uStack_50 = 0xffffffff;
    if (uStack_4c != 0xffffffff) {
      uStack_50 = uStack_4c;
    }
    if (~uStack_18c <= uStack_50) {
      iStack_ec = 10;
      FUN_002513e0(auStack_1a0);
    }
    if (uStack_50 != 0) {
      uStack_4c = uStack_18c + uStack_50;
      iStack_ec = 10;
      iVar3 = FUN_005f0030(auStack_1a0,uStack_4c,0);
      if (iVar3 != 0) {
        ppppuVar5 = apppuStack_19c;
        if (0xf < uStack_188) {
          ppppuVar5 = (undefined4 ****)apppuStack_19c[0];
        }
        iVar3 = iStack_54 + 4;
        if (0xf < *(uint *)(iStack_54 + 0x18)) {
          iVar3 = *(int *)(iStack_54 + 4);
        }
        FUN_0039ac74((int)ppppuVar5 + uStack_18c,iVar3,uStack_50);
        ppppuVar5 = apppuStack_19c;
        if (0xf < uStack_188) {
          ppppuVar5 = (undefined4 ****)apppuStack_19c[0];
        }
        uStack_18c = uStack_4c;
        *(undefined1 *)((int)ppppuVar5 + uStack_4c) = 0;
      }
    }
    iStack_ec = 10;
    FUN_005f4290(auStack_1e0,auStack_1a0);
    FUN_005e8e00(auStack_1a0);
    FUN_005e8e00(auStack_1c0);
    iVar3 = -1;
    if (piStack_80[5] != 0) {
      iStack_ec = 9;
      iVar3 = FUN_001d9204(piStack_80[5],0xffffffff);
    }
    if (iVar3 == 0) {
      iVar3 = FUN_00616f40(piStack_80 + 0x19,auStack_1e0);
      if (iVar3 != piStack_80[0x1b]) {
        iStack_ec = 9;
        FUN_005ea15c(auStack_220,iVar3 + 0x24,0,0xffffffff);
        iStack_78 = 0;
      }
      iStack_7c = iStack_78;
      if (piStack_80[5] != 0) {
        iStack_ec = 9;
        FUN_001d92bc();
        iStack_7c = iStack_78;
      }
    }
    else {
      iStack_7c = -1;
    }
    FUN_005e8e00(auStack_1e0);
    iVar3 = iStack_7c;
  }
  if (iVar3 == 0) {
    iStack_ec = 0xd;
    FUN_005ea3bc(auStack_1a0,0xd4bc7c);
    iStack_ec = 8;
    FUN_005ea15c(auStack_200,auStack_1a0,0,0xffffffff);
    FUN_005e8e00(auStack_1a0);
    ppppcVar9 = apppcStack_21c;
    if (0xf < uStack_208) {
      ppppcVar9 = (char ****)apppcStack_21c[0];
    }
    ppppcVar4 = (char ****)((int)ppppcVar9 + iStack_20c);
    for (; ppppcVar9 != ppppcVar4; ppppcVar9 = (char ****)((int)ppppcVar9 + 1)) {
      if (*(char *)ppppcVar9 == ',') {
        *(char *)ppppcVar9 = ' ';
      }
    }
    iStack_ec = 0xd;
    FUN_0061593c(auStack_180,auStack_220,1);
    iStack_ec = 7;
    uVar6 = FUN_00604b30(auStack_180,&iStack_ac);
    FUN_00604b30(uVar6,&iStack_a8);
    if ((iStack_ac < iStack_a8) &&
       ((iStack_84 < iStack_ac || (iStack_88 = 0, iStack_a8 < iStack_84)))) {
      iStack_88 = -1;
    }
  }
  else {
    iVar3 = -1;
    if (piStack_22c != (int *)0x0) {
      iStack_ec = 0xd;
      piStack_48 = piStack_22c;
      iStack_40 = -1;
      FUN_005f4290(auStack_1e0,0xea09a4);
      uStack_3c = FUN_0039b0f0(ppppuRam00d95188);
      ppppuVar5 = apppuStack_1dc;
      if (0xf < uStack_1c8) {
        ppppuVar5 = (undefined4 ****)apppuStack_1dc[0];
      }
      if (ppppuRam00d95188 < ppppuVar5) {
LAB_00125a80:
        bVar1 = false;
      }
      else {
        ppppuVar5 = apppuStack_1dc;
        if (0xf < uStack_1c8) {
          ppppuVar5 = (undefined4 ****)apppuStack_1dc[0];
        }
        bVar1 = true;
        if ((undefined4 ****)((int)ppppuVar5 + uStack_1cc) <= ppppuRam00d95188) goto LAB_00125a80;
      }
      if (bVar1) {
        puStack_38 = auStack_1e0;
        ppppuVar5 = apppuStack_1dc;
        if (0xf < uStack_1c8) {
          ppppuVar5 = (undefined4 ****)apppuStack_1dc[0];
        }
        uStack_30 = 0xdb8b44 - (int)ppppuVar5;
        puStack_34 = puStack_38;
        uStack_2c = uStack_3c;
        if (uStack_1cc < uStack_30) {
          iStack_ec = 6;
          FUN_00250ea4(puStack_38);
        }
        uStack_28 = *(int *)(puStack_34 + 0x14) - uStack_30;
        if (uStack_28 < uStack_3c) {
          uStack_2c = uStack_28;
        }
        if (~*(uint *)(puStack_38 + 0x14) <= uStack_2c) {
          iStack_ec = 6;
          FUN_002513e0(puStack_38);
        }
        puVar7 = puStack_38;
        if (uStack_2c != 0) {
          uStack_28 = *(int *)(puStack_38 + 0x14) + uStack_2c;
          iStack_ec = 6;
          iVar3 = FUN_005f0030(puStack_38,uStack_28,0);
          puVar7 = puStack_38;
          if (iVar3 != 0) {
            puVar7 = puStack_38 + 4;
            if (0xf < *(uint *)(puStack_38 + 0x18)) {
              puVar7 = *(undefined1 **)(puStack_38 + 4);
            }
            puVar8 = puStack_34 + 4;
            if (0xf < *(uint *)(puStack_34 + 0x18)) {
              puVar8 = *(undefined1 **)(puStack_34 + 4);
            }
            FUN_0039ac74(puVar7 + *(int *)(puStack_38 + 0x14),puVar8 + uStack_30,uStack_2c);
            uVar2 = uStack_28;
            puVar7 = puStack_38 + 4;
            if (0xf < *(uint *)(puStack_38 + 0x18)) {
              puVar7 = *(undefined1 **)(puStack_38 + 4);
            }
            *(uint *)(puStack_38 + 0x14) = uStack_28;
            puVar7[uVar2] = 0;
            puVar7 = puStack_38;
          }
        }
      }
      else {
        if (~uStack_1cc <= uStack_3c) {
          iStack_ec = 6;
          FUN_002513e0(auStack_1e0);
        }
        if (uStack_3c != 0) {
          uStack_24 = uStack_1cc + uStack_3c;
          iStack_ec = 6;
          iVar3 = FUN_005f0030(auStack_1e0,uStack_24,0);
          if (iVar3 != 0) {
            ppppuVar5 = apppuStack_1dc;
            if (0xf < uStack_1c8) {
              ppppuVar5 = (undefined4 ****)apppuStack_1dc[0];
            }
            FUN_0039ac74((int)ppppuVar5 + uStack_1cc,ppppuRam00d95188,uStack_3c);
            ppppuVar5 = apppuStack_1dc;
            if (0xf < uStack_1c8) {
              ppppuVar5 = (undefined4 ****)apppuStack_1dc[0];
            }
            uStack_1cc = uStack_24;
            *(undefined1 *)((int)ppppuVar5 + uStack_24) = 0;
            puVar7 = auStack_1e0;
            goto LAB_001255f0;
          }
        }
        puVar7 = auStack_1e0;
      }
LAB_001255f0:
      iStack_ec = 6;
      FUN_005f4290(auStack_1c0,puVar7);
      FUN_005e8e00(auStack_1e0);
      iStack_ec = 5;
      iStack_20 = 0xea0854;
      FUN_005f4290(auStack_1e0,auStack_1c0);
      uStack_18 = *(uint *)(iStack_20 + 0x14);
      uStack_1c = 0xffffffff;
      if (uStack_18 != 0xffffffff) {
        uStack_1c = uStack_18;
      }
      if (~uStack_1cc <= uStack_1c) {
        iStack_ec = 4;
        FUN_002513e0(auStack_1e0);
      }
      if (uStack_1c != 0) {
        uStack_18 = uStack_1cc + uStack_1c;
        iStack_ec = 4;
        iVar3 = FUN_005f0030(auStack_1e0,uStack_18,0);
        if (iVar3 != 0) {
          ppppuVar5 = apppuStack_1dc;
          if (0xf < uStack_1c8) {
            ppppuVar5 = (undefined4 ****)apppuStack_1dc[0];
          }
          iVar3 = iStack_20 + 4;
          if (0xf < *(uint *)(iStack_20 + 0x18)) {
            iVar3 = *(int *)(iStack_20 + 4);
          }
          FUN_0039ac74((int)ppppuVar5 + uStack_1cc,iVar3,uStack_1c);
          ppppuVar5 = apppuStack_1dc;
          if (0xf < uStack_1c8) {
            ppppuVar5 = (undefined4 ****)apppuStack_1dc[0];
          }
          uStack_1cc = uStack_18;
          *(undefined1 *)((int)ppppuVar5 + uStack_18) = 0;
        }
      }
      iStack_ec = 4;
      FUN_005f4290(auStack_1a0,auStack_1e0);
      FUN_005e8e00(auStack_1e0);
      FUN_005e8e00(auStack_1c0);
      iVar3 = -1;
      if (piStack_48[5] != 0) {
        iStack_ec = 3;
        iVar3 = FUN_001d9204(piStack_48[5],0xffffffff);
      }
      if (iVar3 == 0) {
        iVar3 = FUN_00616f40(piStack_48 + 0x19,auStack_1a0);
        if (iVar3 != piStack_48[0x1b]) {
          iStack_ec = 3;
          FUN_005ea15c(auStack_220,iVar3 + 0x24,0,0xffffffff);
          iStack_40 = 0;
        }
        iStack_44 = iStack_40;
        if (piStack_48[5] != 0) {
          iStack_ec = 3;
          FUN_001d92bc();
          iStack_44 = iStack_40;
        }
      }
      else {
        iStack_44 = -1;
      }
      FUN_005e8e00(auStack_1a0);
      iVar3 = iStack_44;
    }
    if (iVar3 != 0) {
      iStack_88 = 0;
      goto LAB_00125094;
    }
    iStack_ec = 0xd;
    FUN_005ea3bc(auStack_1a0,0xd4bca4);
    iStack_ec = 2;
    FUN_005ea15c(auStack_200,auStack_1a0,0,0xffffffff);
    FUN_005e8e00(auStack_1a0);
    pppcStack_a4 = (char ***)apppcStack_21c;
    if (0xf < uStack_208) {
      pppcStack_a4 = apppcStack_21c[0];
    }
    uStack_9c = 0x2c;
    uStack_9b = 0x20;
    for (ppppcVar9 = (char ****)pppcStack_a4;
        ppppcVar9 != (char ****)((int)pppcStack_a4 + iStack_20c);
        ppppcVar9 = (char ****)((int)ppppcVar9 + 1)) {
      if (*(char *)ppppcVar9 == ',') {
        *(char *)ppppcVar9 = ' ';
      }
    }
    iStack_ec = 0xd;
    pppcStack_a0 = (char ***)((int)pppcStack_a4 + iStack_20c);
    pppcStack_98 = (char ***)ppppcVar9;
    FUN_0061593c(auStack_180,auStack_220,1);
    do {
      if ((uStack_128 & 1) != 0) goto LAB_00125c68;
      iStack_ec = 1;
      FUN_00604b30(auStack_180,&iStack_94);
      if ((uStack_128 & 4) != 0) goto LAB_00125c68;
    } while (iStack_94 != iStack_84);
    iStack_88 = 0;
  }
LAB_00125c68:
  iStack_ec = 0xd;
  FUN_00615818(auStack_180);
LAB_00125094:
  if (iStack_88 == -1) {
    iStack_ec = 0xd;
    FUN_0005e784(0,3,0xb,0xd4bc0c,0x66262c,0x5f2,0xd4bca8,0x66263c);
  }
  FUN_005e8e00(auStack_200);
  FUN_005e8e00(auStack_220);
  if (piStack_22c != (int *)0x0) {
    piStack_c = piStack_22c;
    iVar3 = -1;
    if (piStack_22c[3] != 0) {
      iStack_ec = -1;
      iVar3 = FUN_001d9204(piStack_22c[3],0xffffffff);
    }
    if ((iVar3 == 0) && (*piStack_c = *piStack_c + -1, piStack_c[3] != 0)) {
      iStack_ec = -1;
      FUN_001d92bc();
    }
  }
  FUN_003d12b8(auStack_f0);
  return iStack_88;
}

