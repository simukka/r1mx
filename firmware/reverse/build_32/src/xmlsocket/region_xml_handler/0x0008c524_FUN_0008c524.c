/* 0x0008c524  FUN_0008c524  size=4016 bytes */


void FUN_0008c524(undefined4 *param_1)

{
  bool bVar1;
  undefined1 *puVar2;
  int iVar3;
  undefined4 ***pppuVar4;
  undefined4 uVar5;
  undefined2 uVar6;
  undefined4 *puVar7;
  undefined8 uVar8;
  undefined1 auStack_138 [8];
  undefined4 uStack_130;
  undefined4 **appuStack_12c [4];
  uint uStack_11c;
  uint uStack_118;
  undefined4 uStack_100;
  undefined4 **ppuStack_fc;
  undefined4 uStack_f0;
  undefined4 **ppuStack_ec;
  undefined4 uStack_e0;
  undefined4 **ppuStack_dc;
  undefined1 auStack_d0 [4];
  undefined4 uStack_cc;
  undefined4 uStack_b8;
  undefined4 uStack_b4;
  undefined1 *puStack_b0;
  undefined4 uStack_ac;
  undefined1 *puStack_a8;
  undefined1 *puStack_a4;
  undefined4 *puStack_9c;
  uint uStack_94;
  uint uStack_90;
  int iStack_8c;
  int iStack_88;
  undefined4 *puStack_84;
  undefined1 *puStack_80;
  undefined1 *puStack_7c;
  undefined4 *puStack_78;
  undefined4 *puStack_74;
  uint uStack_70;
  undefined4 *puStack_6c;
  uint uStack_68;
  undefined4 *puStack_64;
  undefined1 *puStack_60;
  undefined1 *puStack_5c;
  undefined4 *puStack_58;
  undefined4 *puStack_54;
  uint uStack_50;
  undefined4 *puStack_4c;
  uint uStack_48;
  undefined4 *puStack_44;
  undefined1 *puStack_40;
  undefined1 *puStack_3c;
  undefined4 *puStack_38;
  undefined4 *puStack_34;
  uint uStack_30;
  undefined4 *puStack_2c;
  uint uStack_28;
  int iStack_24;
  int iStack_20;
  undefined4 *puStack_1c;
  undefined4 *puStack_18;
  undefined4 uStack_14;
  int iStack_10;
  undefined2 *puStack_c;
  undefined4 *puStack_8;
  
  puStack_a4 = &stack0xfffffec0;
  uStack_b8 = 0x25710c;
  puStack_b0 = auStack_138;
  uStack_b4 = 0xe97054;
  uStack_ac = 0x9ce84;
  puStack_a8 = (undefined1 *)register0x00000004;
  puStack_9c = param_1;
  FUN_003d1214(auStack_d0);
  uStack_118 = 0xf;
  appuStack_12c[0] = (undefined4 **)((uint)appuStack_12c[0] & 0xffffff);
  uStack_11c = 0;
  uStack_94 = FUN_0039b0f0(uRam00d94e1c);
  uStack_90 = uStack_94;
  if (0xfffffffe < uStack_94) {
    uStack_cc = 0xffffffff;
    FUN_002513e0(&uStack_130);
  }
  if (uStack_118 < uStack_94) {
    uStack_cc = 0xffffffff;
    FUN_005e7bb8(&uStack_130,uStack_94,uStack_11c);
  }
  else if (uStack_90 == 0) {
    pppuVar4 = appuStack_12c;
    if (0xf < uStack_118) {
      pppuVar4 = (undefined4 ***)appuStack_12c[0];
    }
    uStack_11c = 0;
    *(undefined1 *)pppuVar4 = 0;
  }
  if (uStack_90 != 0) {
    pppuVar4 = appuStack_12c;
    if (0xf < uStack_118) {
      pppuVar4 = (undefined4 ***)appuStack_12c[0];
    }
    FUN_0039ac74(pppuVar4,uRam00d94e1c,uStack_94);
    pppuVar4 = appuStack_12c;
    if (0xf < uStack_118) {
      pppuVar4 = (undefined4 ***)appuStack_12c[0];
    }
    uStack_11c = uStack_94;
    *(undefined1 *)((int)pppuVar4 + uStack_94) = 0;
  }
  uStack_cc = 10;
  FUN_00059684(puStack_9c,&uStack_130,8,0x4b,0x4000,100);
  FUN_005e75e4(&uStack_130,1,0);
  *puStack_9c = 0xe08870;
  puStack_9c[0x20] = 0;
  puStack_9c[0x21] = 0xf;
  *(undefined1 *)(puStack_9c + 0x1c) = 0;
  puStack_80 = (undefined1 *)FUN_00248450(0x14,0xef9080);
  puStack_84 = puStack_9c + 0x4000;
  puVar2 = (undefined1 *)0x0;
  if (puStack_80 != (undefined1 *)0x0) {
    appuStack_12c[0] = pppuRam0065e678;
    uStack_130 = uRam0065e674;
    *puStack_80 = 0;
    uStack_cc = 8;
    puStack_7c = puStack_80;
    uVar5 = FUN_001d9ed8(1);
    *(undefined4 *)(puStack_80 + 4) = uVar5;
    *(undefined4 *)(puStack_80 + 8) = 100;
    uStack_100 = uStack_130;
    ppuStack_fc = appuStack_12c[0];
    puStack_78 = (undefined4 *)FUN_00248640(0x2c);
    ppuStack_dc = ppuStack_fc;
    ppuStack_ec = ppuStack_fc;
    uStack_e0 = uStack_100;
    uStack_f0 = uStack_100;
    *puStack_78 = puStack_9c;
    puStack_74 = puStack_78 + 4;
    puStack_78[1] = uStack_100;
    puStack_78[2] = ppuStack_fc;
    puStack_78[10] = 0xf;
    puStack_78[9] = 0;
    puStack_78[3] = 0;
    *(undefined1 *)(puStack_78 + 5) = 0;
    uStack_70 = FUN_0039b0f0(puRam00d94e20);
    puVar7 = puStack_78 + 5;
    if (0xf < (uint)puStack_74[6]) {
      puVar7 = (undefined4 *)puStack_74[1];
    }
    if (puRam00d94e20 < puVar7) {
LAB_0008d264:
      bVar1 = false;
    }
    else {
      puVar7 = puStack_74 + 1;
      if (0xf < (uint)puStack_74[6]) {
        puVar7 = (undefined4 *)puStack_74[1];
      }
      bVar1 = true;
      if ((undefined4 *)((int)puVar7 + puStack_74[5]) <= puRam00d94e20) goto LAB_0008d264;
    }
    if (bVar1) {
      puVar7 = puStack_74 + 1;
      if (0xf < (uint)puStack_74[6]) {
        puVar7 = (undefined4 *)puStack_74[1];
      }
      uStack_cc = 7;
      FUN_005ea15c(puStack_74,puStack_74,0xd6f55c - (int)puVar7,uStack_70);
    }
    else {
      puStack_6c = puStack_74;
      uStack_68 = uStack_70;
      if (0xfffffffe < uStack_70) {
        uStack_cc = 7;
        FUN_002513e0(puStack_74);
      }
      if ((uint)puStack_74[6] < uStack_70) {
        uStack_cc = 7;
        FUN_005e7bb8(puStack_74,uStack_70,puStack_74[5]);
      }
      else if (uStack_68 == 0) {
        puVar7 = puStack_6c + 1;
        if (0xf < (uint)puStack_6c[6]) {
          puVar7 = (undefined4 *)puStack_6c[1];
        }
        puStack_6c[5] = 0;
        *(undefined1 *)puVar7 = 0;
      }
      if (uStack_68 != 0) {
        puVar7 = puStack_74 + 1;
        if (0xf < (uint)puStack_74[6]) {
          puVar7 = (undefined4 *)puStack_74[1];
        }
        FUN_0039ac74(puVar7,puRam00d94e20,uStack_70);
        puVar7 = puStack_74 + 1;
        if (0xf < (uint)puStack_74[6]) {
          puVar7 = (undefined4 *)puStack_74[1];
        }
        puStack_74[5] = uStack_70;
        *(undefined1 *)((int)puVar7 + uStack_70) = 0;
      }
    }
    *(undefined4 *)(puStack_7c + 0x10) = 0x604c38;
    *(undefined4 **)(puStack_7c + 0xc) = puStack_78;
    puVar2 = puStack_80;
  }
  puStack_84[0x1cfe] = puVar2;
  puStack_60 = (undefined1 *)FUN_00248450(0x14,0xef9080);
  puStack_64 = puStack_9c + 0x4000;
  puVar2 = (undefined1 *)0x0;
  if (puStack_60 != (undefined1 *)0x0) {
    ppuStack_dc = pppuRam0065e680;
    uStack_e0 = uRam0065e67c;
    *puStack_60 = 0;
    uStack_cc = 6;
    puStack_5c = puStack_60;
    uVar5 = FUN_001d9ed8(1);
    *(undefined4 *)(puStack_60 + 4) = uVar5;
    *(undefined4 *)(puStack_60 + 8) = 500;
    uStack_f0 = uStack_e0;
    ppuStack_ec = ppuStack_dc;
    puStack_58 = (undefined4 *)FUN_00248640(0x2c);
    appuStack_12c[0] = ppuStack_ec;
    ppuStack_fc = ppuStack_ec;
    uStack_130 = uStack_f0;
    uStack_100 = uStack_f0;
    *puStack_58 = puStack_9c;
    puStack_54 = puStack_58 + 4;
    puStack_58[1] = uStack_f0;
    puStack_58[2] = ppuStack_ec;
    puStack_58[10] = 0xf;
    puStack_58[9] = 0;
    *(undefined1 *)(puStack_58 + 5) = 0;
    puStack_58[3] = 0;
    uStack_50 = FUN_0039b0f0(puRam00d94e20);
    puVar7 = puStack_58 + 5;
    if (0xf < (uint)puStack_54[6]) {
      puVar7 = (undefined4 *)puStack_54[1];
    }
    if (puRam00d94e20 < puVar7) {
LAB_0008d26c:
      bVar1 = false;
    }
    else {
      puVar7 = puStack_54 + 1;
      if (0xf < (uint)puStack_54[6]) {
        puVar7 = (undefined4 *)puStack_54[1];
      }
      bVar1 = true;
      if ((undefined4 *)((int)puVar7 + puStack_54[5]) <= puRam00d94e20) goto LAB_0008d26c;
    }
    if (bVar1) {
      puVar7 = puStack_54 + 1;
      if (0xf < (uint)puStack_54[6]) {
        puVar7 = (undefined4 *)puStack_54[1];
      }
      uStack_cc = 5;
      FUN_005ea15c(puStack_54,puStack_54,0xd6f55c - (int)puVar7,uStack_50);
    }
    else {
      puStack_4c = puStack_54;
      uStack_48 = uStack_50;
      if (0xfffffffe < uStack_50) {
        uStack_cc = 5;
        FUN_002513e0(puStack_54);
      }
      if ((uint)puStack_54[6] < uStack_50) {
        uStack_cc = 5;
        FUN_005e7bb8(puStack_54,uStack_50,puStack_54[5]);
      }
      else if (uStack_48 == 0) {
        puVar7 = puStack_4c + 1;
        if (0xf < (uint)puStack_4c[6]) {
          puVar7 = (undefined4 *)puStack_4c[1];
        }
        puStack_4c[5] = 0;
        *(undefined1 *)puVar7 = 0;
      }
      if (uStack_48 != 0) {
        puVar7 = puStack_54 + 1;
        if (0xf < (uint)puStack_54[6]) {
          puVar7 = (undefined4 *)puStack_54[1];
        }
        FUN_0039ac74(puVar7,puRam00d94e20,uStack_50);
        puVar7 = puStack_54 + 1;
        if (0xf < (uint)puStack_54[6]) {
          puVar7 = (undefined4 *)puStack_54[1];
        }
        puStack_54[5] = uStack_50;
        *(undefined1 *)((int)puVar7 + uStack_50) = 0;
      }
    }
    *(undefined4 *)(puStack_5c + 0x10) = 0x604c38;
    *(undefined4 **)(puStack_5c + 0xc) = puStack_58;
    puVar2 = puStack_60;
  }
  puStack_64[0x1d00] = puVar2;
  puStack_40 = (undefined1 *)FUN_00248450(0x14,0xef9080);
  puStack_44 = puStack_9c + 0x4000;
  puVar2 = (undefined1 *)0x0;
  if (puStack_40 == (undefined1 *)0x0) goto LAB_0008c718;
  ppuStack_dc = pppuRam0065e670;
  uStack_e0 = uRam0065e66c;
  *puStack_40 = 0;
  uStack_cc = 4;
  puStack_3c = puStack_40;
  uVar5 = FUN_001d9ed8(1);
  *(undefined4 *)(puStack_40 + 4) = uVar5;
  *(undefined4 *)(puStack_40 + 8) = 100;
  uStack_f0 = uStack_e0;
  ppuStack_ec = ppuStack_dc;
  puStack_38 = (undefined4 *)FUN_00248640(0x2c);
  appuStack_12c[0] = ppuStack_ec;
  ppuStack_fc = ppuStack_ec;
  uStack_130 = uStack_f0;
  uStack_100 = uStack_f0;
  *puStack_38 = puStack_9c;
  puStack_34 = puStack_38 + 4;
  puStack_38[1] = uStack_f0;
  puStack_38[2] = ppuStack_ec;
  puStack_38[10] = 0xf;
  puStack_38[9] = 0;
  *(undefined1 *)(puStack_38 + 5) = 0;
  puStack_38[3] = 0;
  uStack_30 = FUN_0039b0f0(puRam00d94e20);
  puVar7 = puStack_38 + 5;
  if (0xf < (uint)puStack_34[6]) {
    puVar7 = (undefined4 *)puStack_34[1];
  }
  if (puRam00d94e20 < puVar7) {
LAB_0008d274:
    bVar1 = false;
  }
  else {
    puVar7 = puStack_34 + 1;
    if (0xf < (uint)puStack_34[6]) {
      puVar7 = (undefined4 *)puStack_34[1];
    }
    bVar1 = true;
    if ((undefined4 *)((int)puVar7 + puStack_34[5]) <= puRam00d94e20) goto LAB_0008d274;
  }
  if (bVar1) {
    puVar7 = puStack_34 + 1;
    if (0xf < (uint)puStack_34[6]) {
      puVar7 = (undefined4 *)puStack_34[1];
    }
    uStack_cc = 3;
    FUN_005ea15c(puStack_34,puStack_34,0xd6f55c - (int)puVar7,uStack_30);
  }
  else {
    puStack_2c = puStack_34;
    uStack_28 = uStack_30;
    if (0xfffffffe < uStack_30) {
      uStack_cc = 3;
      FUN_002513e0(puStack_34);
    }
    if ((uint)puStack_34[6] < uStack_30) {
      uStack_cc = 3;
      FUN_005e7bb8(puStack_34,uStack_30,puStack_34[5]);
    }
    else if (uStack_28 == 0) {
      puVar7 = puStack_2c + 1;
      if (0xf < (uint)puStack_2c[6]) {
        puVar7 = (undefined4 *)puStack_2c[1];
      }
      puStack_2c[5] = 0;
      *(undefined1 *)puVar7 = 0;
    }
    if (uStack_28 != 0) {
      puVar7 = puStack_34 + 1;
      if (0xf < (uint)puStack_34[6]) {
        puVar7 = (undefined4 *)puStack_34[1];
      }
      FUN_0039ac74(puVar7,puRam00d94e20,uStack_30);
      puVar7 = puStack_34 + 1;
      if (0xf < (uint)puStack_34[6]) {
        puVar7 = (undefined4 *)puStack_34[1];
      }
      puStack_34[5] = uStack_30;
      *(undefined1 *)((int)puVar7 + uStack_30) = 0;
    }
  }
  *(undefined4 *)(puStack_3c + 0x10) = 0x604c38;
  *(undefined4 **)(puStack_3c + 0xc) = puStack_38;
  puVar2 = puStack_40;
LAB_0008c718:
  iVar3 = puStack_9c[0x5cfe];
  puStack_44[0x1cff] = puVar2;
  if (((iVar3 == 0) || (puStack_9c[0x5d00] == 0)) || (puStack_9c[0x5cff] == 0)) {
    puVar7 = puStack_9c + 10;
    if (0xf < (uint)puStack_9c[0xf]) {
      puVar7 = (undefined4 *)puStack_9c[10];
    }
    uStack_cc = 9;
    FUN_0005e784(0,3,0x17,0xd41584,0x65e65c,0xc9,0xd41ddc,puVar7);
  }
  uStack_cc = 9;
  uVar5 = FUN_0045964c(0x20,0x16000);
  puStack_9c[0x18] = uVar5;
  uVar5 = FUN_0045964c(0x20,0x120000);
  puStack_9c[0x19] = uVar5;
  uVar5 = FUN_0045964c(0x20,0x76c00);
  puStack_9c[0x16] = uVar5;
  uVar5 = FUN_0045964c(0x20,0xed80);
  puStack_9c[0x17] = uVar5;
  *(undefined1 *)((int)puStack_9c + 0x9b) = 0;
  *(undefined1 *)(puStack_9c + 0x1a) = 0;
  *(undefined1 *)((int)puStack_9c + 0x69) = 0;
  *(undefined1 *)(puStack_9c + 0x22) = 0;
  *(undefined1 *)((int)puStack_9c + 0x89) = 0;
  *(undefined1 *)((int)puStack_9c + 0x8a) = 0;
  *(undefined1 *)(puStack_9c + 0x26) = 0;
  *(undefined1 *)((int)puStack_9c + 0x99) = 0;
  *(undefined1 *)((int)puStack_9c + 0x9a) = 0;
  puStack_9c[0x23] = 10;
  iStack_24 = FUN_00248450(0x9eb8,0xef9080);
  if (iStack_24 != 0) {
    uStack_cc = 2;
    FUN_0012ed88();
  }
  puStack_9c[0x24] = iStack_24;
  iStack_20 = FUN_00248450(0x9eb8,0xef9080);
  if (iStack_20 != 0) {
    uStack_cc = 1;
    FUN_0012ed88();
  }
  puStack_9c[0x11] = 10000;
  puStack_9c[0x25] = iStack_20;
  if ((puStack_9c[0x24] == 0) || (iStack_20 == 0)) {
    puVar7 = puStack_9c + 10;
    if (0xf < (uint)puStack_9c[0xf]) {
      puVar7 = (undefined4 *)puStack_9c[10];
    }
    uStack_cc = 9;
    FUN_0005e784(0,3,0x17,0xd41584,0x65e65c,0xe0,0xd41dfc,puVar7);
  }
  puStack_9c[0x28] = 0;
  puStack_9c[0x27] = 0;
  FUN_0039acec(puStack_9c + 0x1a3a,0,0x6800);
  FUN_0039acec(puStack_9c + 0x3a,0,0x6800);
  iStack_8c = 0;
  FUN_0039acec(puStack_9c + 0x343a,0,0x800);
  if (iStack_8c < 5) {
    iStack_8c = 5 - iStack_8c;
    puVar7 = puStack_9c + 0x343a;
    do {
      *puVar7 = 0;
      puVar7 = puVar7 + 1;
      iStack_8c = iStack_8c + -1;
    } while (iStack_8c != 0);
  }
  iVar3 = 0xa3;
  puVar7 = puStack_9c + 0x343f;
  do {
    *puVar7 = 1;
    puVar7 = puVar7 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  iVar3 = 0xaa;
  puVar7 = puStack_9c + 0x34e2;
  do {
    *puVar7 = 2;
    puVar7 = puVar7 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  iStack_8c = 0x152;
  iVar3 = 0xae;
  puVar7 = puStack_9c + 0x358c;
  do {
    *puVar7 = 2;
    puVar7 = puVar7 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  puStack_1c = puStack_9c + 0x4000;
  puStack_9c[0x2b] = 0x37;
  puStack_9c[0x2c] = 0x1f;
  puStack_9c[0x2d] = 0x492;
  puStack_9c[0x2e] = 0x292;
  puStack_9c[0x33] = 0x168;
  puStack_9c[0x34] = 1;
  puStack_9c[0x37] = 100;
  puStack_9c[0x38] = 0x2400;
  puStack_9c[0x2a] = 1;
  puStack_9c[0x35] = 100;
  puStack_9c[0x36] = 100;
  FUN_0039acec(puStack_9c + 0x363a,0,0x1400);
  puStack_8 = puStack_1c + -0x4c6;
  iStack_8c = 0;
  iStack_88 = 0;
  do {
    FUN_00373dd0(iStack_88);
    uStack_cc = 9;
    FUN_00377594();
    iStack_8c = iStack_8c + 1;
    uVar6 = FUN_003740a0();
    *(undefined2 *)puStack_8 = uVar6;
    iStack_88 = iStack_88 + 0x400;
    puStack_8 = (undefined4 *)((int)puStack_8 + 2);
  } while (iStack_8c < 0x385);
  puStack_c = (undefined2 *)((int)puStack_9c + 0xf3f2);
  iStack_8c = 0;
  iStack_88 = 0;
  do {
    FUN_00373dd0(iStack_88);
    uStack_cc = 9;
    FUN_00377594();
    iStack_8c = iStack_8c + 1;
    uVar6 = FUN_003740a0();
    *puStack_c = uVar6;
    iStack_88 = iStack_88 + 0x10;
    puStack_c = puStack_c + 1;
  } while (iStack_8c < 0x401);
  puStack_18 = puStack_9c + 0x4000;
  puStack_9c[0x56fd] = 0;
  FUN_0039acec(puStack_9c + 0x56fe,0,0x1800);
  puStack_18[0x16ff] = 0;
  puStack_18[0x1700] = 0x3f800000;
  puStack_18[0x16fe] = 0;
  iStack_8c = 1;
  do {
    uVar5 = FUN_0037517c(iStack_8c);
    uVar5 = FUN_00374f8c(uVar5,0x439a0000);
    uVar5 = FUN_00374e00(uVar5,0x43ff8000);
    uStack_14 = FUN_00374be4(uVar5,0x3e9a4d27);
    uVar8 = FUN_00373e9c();
    FUN_00373370((int)((ulonglong)uVar8 >> 0x20),(int)uVar8,0x3fe00000,0);
    iStack_10 = FUN_00374010();
    FUN_00374be8(uStack_14,0x3f1a4d27);
    uVar8 = FUN_00373e9c();
    FUN_00373370((int)((ulonglong)uVar8 >> 0x20),(int)uVar8,0x3fe00000,0);
    iVar3 = FUN_00374010();
    if (iStack_10 == iVar3) {
      puStack_9c[iStack_10 * 3 + 0x56ff] = iStack_10;
      puStack_9c[iStack_10 * 3 + 0x5700] = 0x3f800000;
      puStack_9c[iStack_10 * 3 + 0x56fe] = iStack_8c;
    }
    else {
      puStack_9c[iStack_10 * 3 + 0x56ff] = iStack_10;
      puStack_9c[iStack_10 * 3 + 0x56fe] = iStack_8c;
      puStack_9c[iStack_10 * 3 + 0x5700] = 0x3f000000;
      puStack_9c[iVar3 * 3 + 0x56ff] = iVar3;
      puStack_9c[iVar3 * 3 + 0x56fe] = iStack_8c;
      puStack_9c[iVar3 * 3 + 0x5700] = 0x3f000000;
    }
    iStack_8c = iStack_8c + 1;
  } while (iStack_8c < 0x135);
  FUN_003d12b8(auStack_d0);
  return;
}

