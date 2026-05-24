
void Connection_dispatch(int param_1,uint param_2)

{
  undefined4 *puVar1;
  bool bVar2;
  undefined4 ***pppuVar3;
  undefined1 *puVar4;
  int iVar5;
  int *piVar6;
  int in_r9;
  uint uVar7;
  undefined4 ****ppppuVar8;
  undefined1 auStack_32c [4];
  undefined4 ***apppuStack_328 [4];
  undefined1 auStack_318 [4];
  uint uStack_314;
  undefined1 auStack_310 [28];
  undefined1 auStack_2f4 [28];
  undefined1 auStack_2d8 [16];
  int aiStack_2c8 [3];
  undefined1 auStack_2bc [8];
  uint uStack_2b4;
  undefined1 auStack_2b0 [28];
  undefined1 auStack_294 [28];
  undefined1 auStack_278 [16];
  int aiStack_268 [3];
  undefined1 auStack_25c [8];
  uint uStack_254;
  undefined1 auStack_250 [28];
  undefined1 auStack_234 [28];
  undefined1 auStack_218 [12];
  undefined1 auStack_20c [4];
  undefined4 *apuStack_208 [3];
  undefined1 auStack_1fc [8];
  uint uStack_1f4;
  undefined1 auStack_1f0 [28];
  undefined1 auStack_1d4 [4];
  undefined1 auStack_1d0 [16];
  undefined1 auStack_1c0 [16];
  undefined1 auStack_1b0 [4];
  undefined4 ***apppuStack_1ac [4];
  uint uStack_19c;
  uint uStack_198;
  undefined1 auStack_190 [32];
  undefined1 auStack_170 [4];
  undefined4 ***apppuStack_16c [4];
  uint uStack_15c;
  uint uStack_158;
  undefined1 auStack_150 [4];
  undefined4 ***apppuStack_14c [4];
  uint uStack_13c;
  uint uStack_138;
  byte bStack_130;
  byte bStack_12f;
  byte bStack_12e;
  undefined1 uStack_12d;
  undefined1 uStack_12c;
  undefined1 auStack_12b [11];
  undefined1 auStack_120 [4];
  uint uStack_11c;
  undefined4 uStack_10c;
  uint uStack_108;
  undefined1 auStack_100 [4];
  undefined4 uStack_fc;
  int iStack_e8;
  undefined4 uStack_e4;
  undefined1 *puStack_e0;
  undefined4 uStack_dc;
  undefined1 *puStack_d8;
  undefined1 *puStack_d4;
  int iStack_cc;
  uint uStack_c8;
  int iStack_c4;
  int iStack_b0;
  int iStack_a0;
  int iStack_90;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 **ppuStack_48;
  undefined1 *puStack_38;
  undefined1 *puStack_34;
  undefined1 *puStack_2c;
  undefined1 *puStack_28;
  undefined1 *puStack_20;
  undefined1 *puStack_1c;
  undefined1 *puStack_14;
  undefined1 *puStack_10;
  
  puStack_d4 = &stack0xfffffcd0;
  iStack_e8 = in_r9 + 0x710c;
  puStack_e0 = auStack_318;
  uStack_dc = 0x576a4;
  uStack_e4 = 0xe962a8;
  puStack_d8 = (undefined1 *)register0x00000004;
  iStack_cc = param_1;
  uStack_c8 = param_2;
  FUN_003d1214(auStack_100);
  uStack_fc = 0x20;
  iStack_c4 = 2;
  FUN_005ea3bc(auStack_310,0xd3ba60);
  iStack_c4 = 1;
  FUN_005ea3bc(auStack_2f4,0xd3ba6c);
  iStack_c4 = 0;
  FUN_005ea3bc(auStack_2d8,0xd3ba78);
  iStack_c4 = iStack_c4 + -1;
  uStack_fc = 0x1f;
  iStack_b0 = 2;
  FUN_005ea3bc(auStack_2b0,0xd3ba80);
  iStack_b0 = 1;
  FUN_005ea3bc(auStack_294,0xd3baa4);
  iStack_b0 = 0;
  FUN_005ea3bc(auStack_278,0xd3bac0);
  iStack_b0 = iStack_b0 + -1;
  uStack_fc = 0x1e;
  iStack_a0 = 2;
  FUN_005ea3bc(auStack_250,0xd3badc);
  iStack_a0 = 1;
  FUN_005ea3bc(auStack_234,0xd3bafc);
  iStack_a0 = 0;
  FUN_005ea3bc(auStack_218,0xd3bb14);
  iStack_a0 = iStack_a0 + -1;
  uStack_fc = 0x1d;
  iStack_90 = 0;
  FUN_005ea3bc(auStack_1f0,0xd3bb2c);
  auStack_1d0[0] = 3 < uStack_c8;
  iStack_90 = iStack_90 + -1;
  if ((bool)auStack_1d0[0]) {
    uStack_c8 = uStack_c8 - 3;
  }
  uStack_fc = 0x1c;
  uStack_80 = FUN_0005e890();
  FUN_005ea3bc(auStack_1b0,0xd3bb34);
  uStack_fc = 0x1b;
  FUN_005e817c(auStack_1c0,uStack_80,auStack_1b0);
  uStack_fc = 0x1a;
  FUN_005e8510(auStack_1c0,auStack_1d0,0xffffffff);
  uStack_fc = 0x1b;
  FUN_005e7ed0(auStack_1c0);
  if (0xf < uStack_198) {
    FUN_00245c34(apppuStack_1ac[0]);
  }
  pppuVar3 = apppuStack_1ac[0];
  bVar2 = iStack_cc - 1U < 3 && uStack_c8 < 4;
  uVar7 = (uint)bVar2;
  uStack_198 = 0xf;
  uStack_19c = 0;
  apppuStack_1ac[0] = (undefined4 ***)((uint)apppuStack_1ac[0] & 0xffffff);
  if (uVar7 == 0) {
    uStack_138 = 0xf;
    apppuStack_14c[0] = (undefined4 ***)CONCAT13(bVar2,apppuStack_14c[0]._1_3_);
    uStack_fc = 0x13;
    uStack_198 = 0xf;
    apppuStack_1ac[0] = (undefined4 ***)CONCAT13(bVar2,(int3)pppuVar3);
    uStack_158 = 0xf;
    apppuStack_16c[0] = (undefined4 ***)CONCAT13(bVar2,apppuStack_16c[0]._1_3_);
    uStack_19c = uVar7;
    uStack_15c = uVar7;
    uStack_13c = uVar7;
    uStack_70 = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3ba80);
    uStack_fc = 0x12;
    FUN_005e817c(auStack_1c0,uStack_70,auStack_120);
    uStack_fc = 0x11;
    FUN_005ea8a8(auStack_1c0,auStack_1b0);
    uStack_fc = 0x12;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_11c = uStack_11c & 0xffffff;
    uStack_fc = 0x13;
    uStack_108 = 0xf;
    uStack_10c = 0;
    uStack_6c = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3baa4);
    uStack_fc = 0x10;
    FUN_005e817c(auStack_1c0,uStack_6c,auStack_120);
    uStack_fc = 0xf;
    FUN_005ea8a8(auStack_1c0,auStack_170);
    uStack_fc = 0x10;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_108 = 0xf;
    uStack_11c = uStack_11c & 0xffffff;
    uStack_fc = 0x13;
    uStack_10c = 0;
    uStack_68 = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3bac0);
    uStack_fc = 0xe;
    FUN_005e817c(auStack_1c0,uStack_68,auStack_120);
    uStack_fc = 0xd;
    FUN_005ea8a8(auStack_1c0,auStack_150);
    uStack_fc = 0xe;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_108 = 0xf;
    uStack_11c = uStack_11c & 0xffffff;
    uStack_fc = 0x13;
    uStack_10c = 0;
    uStack_64 = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3badc);
    uStack_fc = 0xc;
    FUN_005e817c(auStack_1c0,uStack_64,auStack_120);
    uStack_fc = 0xb;
    FUN_005e8368(auStack_1c0,&bStack_130);
    uStack_fc = 0xc;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_108 = 0xf;
    uStack_11c = uStack_11c & 0xffffff;
    uStack_fc = 0x13;
    uStack_10c = 0;
    uStack_60 = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3bafc);
    uStack_fc = 10;
    FUN_005e817c(auStack_1c0,uStack_60,auStack_120);
    uStack_fc = 9;
    FUN_005e8368(auStack_1c0,&bStack_12f);
    uStack_fc = 10;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_108 = 0xf;
    uStack_11c = uStack_11c & 0xffffff;
    uStack_fc = 0x13;
    uStack_10c = 0;
    uStack_5c = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3bb14);
    uStack_fc = 8;
    FUN_005e817c(auStack_1c0,uStack_5c,auStack_120);
    uStack_fc = 7;
    FUN_005e8368(auStack_1c0,&bStack_12e);
    uStack_fc = 8;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_108 = 0xf;
    uStack_11c = uStack_11c & 0xffffff;
    uStack_fc = 0x13;
    uStack_10c = 0;
    uStack_58 = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3bb94);
    uStack_fc = 6;
    FUN_005e817c(auStack_1c0,uStack_58,auStack_120);
    uStack_fc = 5;
    FUN_005e8368(auStack_1c0,&uStack_12d);
    uStack_fc = 6;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_108 = 0xf;
    uStack_11c = uStack_11c & 0xffffff;
    uStack_fc = 0x13;
    uStack_10c = 0;
    uStack_54 = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3bbb4);
    uStack_fc = 4;
    FUN_005e817c(auStack_1c0,uStack_54,auStack_120);
    uStack_fc = 3;
    FUN_005e8368(auStack_1c0,&uStack_12c);
    uStack_fc = 4;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_108 = 0xf;
    uStack_11c = uStack_11c & 0xffffff;
    uStack_fc = 0x13;
    uStack_10c = 0;
    uStack_50 = FUN_0005e890();
    FUN_005ea3bc(auStack_120,0xd3bbcc);
    uStack_fc = 2;
    FUN_005e817c(auStack_1c0,uStack_50,auStack_120);
    uStack_fc = 1;
    FUN_005e8368(auStack_1c0,auStack_12b);
    uStack_fc = 2;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_108) {
      FUN_00245c34(uStack_11c);
    }
    uStack_108 = 0xf;
    uStack_10c = 0;
    uStack_11c = uStack_11c & 0xffffff;
    apppuStack_328[1] = apppuStack_1ac;
    if (0xf < uStack_198) {
      apppuStack_328[1] = apppuStack_1ac[0];
    }
    apppuStack_328[0] = (undefined4 ***)(uint)bStack_130;
    uStack_fc = 0x13;
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x38f,0xd3bbe4,uStack_12d);
    apppuStack_328[1] = apppuStack_16c;
    if (0xf < uStack_158) {
      apppuStack_328[1] = apppuStack_16c[0];
    }
    apppuStack_328[0] = (undefined4 ***)(uint)bStack_12f;
    uStack_fc = 0x13;
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x390,0xd3bc10,uStack_12c);
    apppuStack_328[1] = apppuStack_14c;
    if (0xf < uStack_138) {
      apppuStack_328[1] = apppuStack_14c[0];
    }
    apppuStack_328[0] = (undefined4 ***)(uint)bStack_12e;
    uStack_fc = 0x13;
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x391,0xd3bc3c,auStack_12b[0]);
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x392,0xd3bc68,0x65d010);
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x393,0xd3bc80);
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x394,0xd3bcb8);
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x395,0xd3bcf4);
    if (bStack_12f != 0) {
      uStack_4c = FUN_001ce7ec();
      ppuStack_48 = (undefined4 **)FUN_001ce83c();
      iVar5 = FUN_001ce888();
      apppuStack_328[1] = (undefined4 ****)0xd48b08;
      if (iVar5 == 0) {
        apppuStack_328[1] = (undefined4 ****)0xddf7cc;
      }
      apppuStack_328[0] = (undefined4 ***)ppuStack_48;
      uStack_fc = 0x13;
      FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x39b,0xd3bd34,uStack_4c);
    }
    if (0xf < uStack_138) {
      FUN_00245c34(apppuStack_14c[0]);
    }
    apppuStack_14c[0] = (undefined4 ***)((uint)apppuStack_14c[0] & 0xffffff);
    uStack_138 = 0xf;
    uStack_13c = 0;
    if (0xf < uStack_158) {
      FUN_00245c34(apppuStack_16c[0]);
    }
    apppuStack_16c[0] = (undefined4 ***)((uint)apppuStack_16c[0] & 0xffffff);
    uStack_15c = 0;
    uStack_158 = 0xf;
    if (0xf < uStack_198) {
      FUN_00245c34(apppuStack_1ac[0]);
    }
  }
  else {
    auStack_190[0] = 0;
    if (uStack_c8 != 0) {
      auStack_190[0] = 1;
      ppppuVar8 = apppuStack_328 + uStack_c8 * 7;
      if (0xf < (&uStack_314)[uStack_c8 * 7]) {
        ppppuVar8 = (undefined4 ****)apppuStack_328[uStack_c8 * 7];
      }
      apppuStack_328[0] = (undefined4 ***)(apuStack_208 + iStack_cc * 7);
      if (0xf < (&uStack_1f4)[iStack_cc * 7]) {
        apppuStack_328[0] = (undefined4 ***)apuStack_208[iStack_cc * 7];
      }
      uStack_fc = 0x1c;
      FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x378,0xd3bb58,ppppuVar8);
      uStack_7c = FUN_0005e890();
      piVar6 = aiStack_2c8 + iStack_cc * 7;
      if (0xf < (&uStack_2b4)[iStack_cc * 7]) {
        piVar6 = (int *)aiStack_2c8[iStack_cc * 7];
      }
      uStack_fc = 0x1c;
      FUN_005ea3bc(auStack_1b0,piVar6);
      uStack_fc = 0x19;
      FUN_005e817c(auStack_1c0,uStack_7c,auStack_1b0);
      uStack_fc = 0x18;
      FUN_005ea6b0(auStack_1c0,auStack_32c + uStack_c8 * 0x1c,0xffffffff);
      uStack_fc = 0x19;
      FUN_005e7ed0(auStack_1c0);
      if (0xf < uStack_198) {
        FUN_00245c34(apppuStack_1ac[0]);
      }
      uStack_198 = 0xf;
      apppuStack_1ac[0] = (undefined4 ***)((uint)apppuStack_1ac[0] & 0xffffff);
      uStack_fc = 0x1c;
      uStack_19c = 0;
      uStack_78 = FUN_0005e890();
      FUN_005ea3bc(auStack_1b0,0xd3bb78);
      uStack_fc = 0x17;
      FUN_005e817c(auStack_1c0,uStack_78,auStack_1b0);
      uStack_fc = 0x16;
      FUN_005ea6b0(auStack_1c0,auStack_20c + iStack_cc * 0x1c,0xffffffff);
      uStack_fc = 0x17;
      FUN_005e7ed0(auStack_1c0);
      if (0xf < uStack_198) {
        FUN_00245c34(apppuStack_1ac[0]);
      }
      apppuStack_1ac[0] = (undefined4 ***)((uint)apppuStack_1ac[0] & 0xffffff);
    }
    uStack_198 = 0xf;
    uStack_19c = 0;
    uStack_fc = 0x1c;
    uStack_74 = FUN_0005e890();
    piVar6 = aiStack_268 + iStack_cc * 7;
    if (0xf < (&uStack_254)[iStack_cc * 7]) {
      piVar6 = (int *)aiStack_268[iStack_cc * 7];
    }
    uStack_fc = 0x1c;
    FUN_005ea3bc(auStack_1b0,piVar6);
    uStack_fc = 0x15;
    FUN_005e817c(auStack_1c0,uStack_74,auStack_1b0);
    uStack_fc = 0x14;
    FUN_005e8510(auStack_1c0,auStack_190,0xffffffff);
    uStack_fc = 0x15;
    FUN_005e7ed0(auStack_1c0);
    if (0xf < uStack_198) {
      FUN_00245c34(apppuStack_1ac[0]);
    }
  }
  apppuStack_1ac[0] = (undefined4 ***)((uint)apppuStack_1ac[0] & 0xffffff);
  uStack_198 = 0xf;
  uStack_19c = 0;
  puStack_38 = auStack_1d4;
  while (auStack_1f0 != puStack_38) {
    puStack_34 = puStack_38 + -0x1c;
    puVar4 = puStack_34;
    if (0xf < *(uint *)(puStack_38 + -4)) {
      puVar1 = (undefined4 *)(puStack_38 + -0x18);
      puStack_38 = puStack_34;
      FUN_00245c34(*puVar1);
      puVar4 = puStack_38;
    }
    puStack_38 = puVar4;
    puVar4 = puStack_34;
    *(undefined4 *)(puStack_34 + 0x14) = 0;
    puVar4[4] = 0;
    *(undefined4 *)(puVar4 + 0x18) = 0xf;
  }
  puStack_2c = auStack_1fc;
  while (auStack_250 != puStack_2c) {
    puStack_28 = puStack_2c + -0x1c;
    puVar4 = puStack_28;
    if (0xf < *(uint *)(puStack_2c + -4)) {
      puVar1 = (undefined4 *)(puStack_2c + -0x18);
      puStack_2c = puStack_28;
      FUN_00245c34(*puVar1);
      puVar4 = puStack_2c;
    }
    puStack_2c = puVar4;
    puVar4 = puStack_28;
    *(undefined4 *)(puStack_28 + 0x14) = 0;
    puVar4[4] = 0;
    *(undefined4 *)(puVar4 + 0x18) = 0xf;
  }
  puStack_20 = auStack_25c;
  while (auStack_2b0 != puStack_20) {
    puStack_1c = puStack_20 + -0x1c;
    puVar4 = puStack_1c;
    if (0xf < *(uint *)(puStack_20 + -4)) {
      puVar1 = (undefined4 *)(puStack_20 + -0x18);
      puStack_20 = puStack_1c;
      FUN_00245c34(*puVar1);
      puVar4 = puStack_20;
    }
    puStack_20 = puVar4;
    puVar4 = puStack_1c;
    *(undefined4 *)(puStack_1c + 0x14) = 0;
    puVar4[4] = 0;
    *(undefined4 *)(puVar4 + 0x18) = 0xf;
  }
  puStack_14 = auStack_2bc;
  while (auStack_310 != puStack_14) {
    puStack_10 = puStack_14 + -0x1c;
    puVar4 = puStack_10;
    if (0xf < *(uint *)(puStack_14 + -4)) {
      puVar1 = (undefined4 *)(puStack_14 + -0x18);
      puStack_14 = puStack_10;
      FUN_00245c34(*puVar1);
      puVar4 = puStack_14;
    }
    puStack_14 = puVar4;
    puVar4 = puStack_10;
    *(undefined4 *)(puStack_10 + 0x14) = 0;
    puVar4[4] = 0;
    *(undefined4 *)(puVar4 + 0x18) = 0xf;
  }
  FUN_003d12b8(auStack_100);
  return;
}

