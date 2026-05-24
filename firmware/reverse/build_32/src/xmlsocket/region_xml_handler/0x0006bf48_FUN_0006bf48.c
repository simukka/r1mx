/* 0x0006bf48  FUN_0006bf48  size=2072 bytes */


undefined4 FUN_0006bf48(int param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  bool bVar7;
  undefined4 uVar6;
  int iVar8;
  undefined1 *puVar9;
  undefined1 auStack_1f8 [8];
  char acStack_1f0 [16];
  undefined1 auStack_1e0 [32];
  undefined1 auStack_1c0 [32];
  undefined1 auStack_1a0 [32];
  undefined1 auStack_180 [32];
  undefined1 auStack_160 [32];
  undefined1 auStack_140 [32];
  undefined1 auStack_120 [32];
  undefined1 auStack_100 [32];
  undefined1 auStack_e0 [32];
  undefined1 auStack_c0 [32];
  undefined1 auStack_a0 [32];
  undefined1 auStack_80 [4];
  undefined4 uStack_7c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined1 *puStack_60;
  undefined4 uStack_5c;
  undefined1 *puStack_58;
  undefined1 *puStack_54;
  int iStack_4c;
  int iStack_48;
  undefined4 uStack_44;
  int iStack_40;
  uint uStack_3c;
  uint uStack_38;
  int iStack_34;
  int iStack_30;
  uint uStack_2c;
  uint uStack_28;
  int iStack_24;
  uint uStack_20;
  int iStack_18;
  int iStack_14;
  int iStack_10;
  
  puStack_54 = &stack0xfffffe00;
  uStack_68 = 0x25710c;
  puStack_60 = auStack_1f8;
  uStack_64 = 0xe96a82;
  uStack_5c = 0x7c698;
  puStack_58 = (undefined1 *)register0x00000004;
  iStack_4c = param_1;
  iStack_48 = param_2;
  FUN_003d1214(auStack_80);
  uStack_3c = *(uint *)(iStack_48 * 0x94 + 0xe10a74);
  iStack_40 = iStack_4c + 0x68;
  uStack_38 = FUN_0039b0f0(uStack_3c);
  uStack_44 = 1;
  uVar1 = iStack_4c + 0x6c;
  if (0xf < *(uint *)(iStack_40 + 0x18)) {
    uVar1 = *(uint *)(iStack_40 + 4);
  }
  if (uStack_3c < uVar1) {
LAB_0006c024:
    bVar7 = false;
  }
  else {
    iVar8 = iStack_40 + 4;
    if (0xf < *(uint *)(iStack_40 + 0x18)) {
      iVar8 = *(int *)(iStack_40 + 4);
    }
    bVar7 = true;
    if ((uint)(iVar8 + *(int *)(iStack_40 + 0x14)) <= uStack_3c) goto LAB_0006c024;
  }
  if (bVar7) {
    iStack_34 = iStack_40;
    iStack_30 = iStack_40;
    if (*(uint *)(iStack_40 + 0x18) < 0x10) {
      uStack_2c = uStack_3c - (iStack_40 + 4);
      if (*(uint *)(iStack_40 + 0x14) < uStack_2c) {
LAB_0006c5a0:
        uStack_7c = 0xffffffff;
        FUN_00250ea4(iStack_40);
      }
    }
    else {
      uStack_2c = uStack_3c - *(int *)(iStack_40 + 4);
      if (*(uint *)(iStack_40 + 0x14) < uStack_2c) goto LAB_0006c5a0;
    }
    uStack_28 = *(int *)(iStack_30 + 0x14) - uStack_2c;
    if (uStack_38 < uStack_28) {
      uStack_28 = uStack_38;
    }
    if (iStack_34 == iStack_30) {
      uStack_7c = 0xffffffff;
      FUN_005f3808(iStack_34,uStack_2c + uStack_28,0xffffffff);
      FUN_005f3808(iStack_34,0,uStack_2c);
    }
    else {
      uStack_20 = uStack_28;
      iStack_24 = iStack_34;
      if (0xfffffffe < uStack_28) {
        uStack_7c = 0xffffffff;
        FUN_002513e0(iStack_34);
      }
      if (*(uint *)(iStack_34 + 0x18) < uStack_28) {
        uStack_7c = 0xffffffff;
        FUN_005e7bb8(iStack_34,uStack_28,*(undefined4 *)(iStack_34 + 0x14));
      }
      else if (uStack_20 == 0) {
        puVar9 = (undefined1 *)(iStack_24 + 4);
        if (0xf < *(uint *)(iStack_24 + 0x18)) {
          puVar9 = *(undefined1 **)(iStack_24 + 4);
        }
        *(undefined4 *)(iStack_24 + 0x14) = 0;
        *puVar9 = 0;
      }
      if (uStack_20 != 0) {
        iVar8 = iStack_34 + 4;
        if (0xf < *(uint *)(iStack_34 + 0x18)) {
          iVar8 = *(int *)(iStack_34 + 4);
        }
        iVar3 = iStack_30 + 4;
        if (0xf < *(uint *)(iStack_30 + 0x18)) {
          iVar3 = *(int *)(iStack_30 + 4);
        }
        FUN_0039ac74(iVar8,iVar3 + uStack_2c,uStack_28);
        uVar2 = *(uint *)(iStack_34 + 0x18);
        iVar8 = iStack_34;
        uVar1 = uStack_28;
        goto LAB_0006c130;
      }
    }
  }
  else {
    uStack_7c = 0xffffffff;
    iVar8 = FUN_005f0030(iStack_40,uStack_38,0);
    if (iVar8 != 0) {
      iVar8 = iStack_40 + 4;
      if (0xf < *(uint *)(iStack_40 + 0x18)) {
        iVar8 = *(int *)(iStack_40 + 4);
      }
      FUN_0039ac74(iVar8,uStack_3c,uStack_38);
      uVar2 = *(uint *)(iStack_40 + 0x18);
      iVar8 = iStack_40;
      uVar1 = uStack_38;
LAB_0006c130:
      iVar3 = iVar8 + 4;
      if (0xf < uVar2) {
        iVar3 = *(int *)(iVar8 + 4);
      }
      *(uint *)(iVar8 + 0x14) = uVar1;
      *(undefined1 *)(iVar3 + uVar1) = 0;
    }
  }
  uStack_7c = 0xffffffff;
  FUN_005f4290(auStack_140,iStack_4c + 0x68);
  iStack_18 = iStack_4c + 0xa0;
  uStack_7c = 0x19;
  FUN_005ea3bc(auStack_120,0xd880c8);
  uStack_7c = 0x18;
  FUN_005f43dc(auStack_160,auStack_140,auStack_120);
  uStack_7c = 0x17;
  FUN_005f4290(auStack_100,0xe9ee70);
  uStack_7c = 0x16;
  FUN_005f43dc(auStack_180,auStack_160,auStack_100);
  uStack_7c = 0x15;
  FUN_005ea3bc(auStack_e0,0xd5abe4);
  uStack_7c = 0x14;
  FUN_005f43dc(auStack_1a0,auStack_180,auStack_e0);
  uStack_7c = 0x13;
  FUN_005f4290(auStack_c0,0xe9ee54);
  uStack_7c = 0x12;
  FUN_005f43dc(auStack_1c0,auStack_1a0,auStack_c0);
  uStack_7c = 0x11;
  FUN_005f4290(auStack_a0,0xe9f4a4);
  uStack_7c = 0x10;
  FUN_005f43dc(auStack_1e0,auStack_1c0,auStack_a0);
  uStack_7c = 0xf;
  FUN_005ea15c(iStack_18,auStack_1e0,0,0xffffffff);
  FUN_005e8e00(auStack_1e0);
  FUN_005e8e00(auStack_a0);
  FUN_005e8e00(auStack_1c0);
  FUN_005e8e00(auStack_c0);
  FUN_005e8e00(auStack_1a0);
  FUN_005e8e00(auStack_e0);
  FUN_005e8e00(auStack_180);
  FUN_005e8e00(auStack_100);
  FUN_005e8e00(auStack_160);
  FUN_005e8e00(auStack_120);
  FUN_005e8e00(auStack_140);
  uStack_7c = 0xffffffff;
  FUN_005f4290(auStack_140,iStack_4c + 0x68);
  iStack_14 = iStack_4c + 0xbc;
  uStack_7c = 0xe;
  FUN_005ea3bc(auStack_160,0xd880c8);
  uStack_7c = 0xd;
  FUN_005f43dc(auStack_120,auStack_140,auStack_160);
  uStack_7c = 0xc;
  FUN_005f4290(auStack_180,0xe9ee70);
  uStack_7c = 0xb;
  FUN_005f43dc(auStack_100,auStack_120,auStack_180);
  uStack_7c = 10;
  FUN_005ea3bc(auStack_1a0,0xd5abe4);
  uStack_7c = 9;
  FUN_005f43dc(auStack_e0,auStack_100,auStack_1a0);
  uStack_7c = 8;
  FUN_005f4290(auStack_1c0,0xe9ee38);
  uStack_7c = 7;
  FUN_005f43dc(auStack_c0,auStack_e0,auStack_1c0);
  uStack_7c = 6;
  FUN_005f4290(auStack_1e0,0xe9f4a4);
  uStack_7c = 5;
  FUN_005f43dc(auStack_a0,auStack_c0,auStack_1e0);
  uStack_7c = 4;
  FUN_005ea15c(iStack_14,auStack_a0,0,0xffffffff);
  FUN_005e8e00(auStack_a0);
  FUN_005e8e00(auStack_1e0);
  FUN_005e8e00(auStack_c0);
  FUN_005e8e00(auStack_1c0);
  FUN_005e8e00(auStack_e0);
  FUN_005e8e00(auStack_1a0);
  FUN_005e8e00(auStack_100);
  FUN_005e8e00(auStack_180);
  FUN_005e8e00(auStack_120);
  FUN_005e8e00(auStack_160);
  FUN_005e8e00(auStack_140);
  iVar8 = iStack_4c + 0xa4;
  if (0xf < *(uint *)(iStack_4c + 0xb8)) {
    iVar8 = *(int *)(iStack_4c + 0xa4);
  }
  uStack_7c = 0xffffffff;
  iVar8 = FUN_001aca04(iVar8,0);
  if (iVar8 == 0) {
    uStack_7c = 0xffffffff;
    iVar8 = FUN_0006976c(iStack_4c);
    if (iVar8 == 0) {
      iVar8 = iStack_4c + 0x6c;
      if (0xf < *(uint *)(iStack_4c + 0x80)) {
        iVar8 = *(int *)(iStack_4c + 0x6c);
      }
      uStack_7c = 0xffffffff;
      iVar8 = FUN_001ad444(iVar8,acStack_1f0);
      if ((iVar8 == 0) && (acStack_1f0[0] != '\0')) goto LAB_0006c4cc;
      uVar6 = 0xd3f1f8;
      uVar4 = 0x20;
      uVar5 = 0x504;
      uStack_7c = 0xffffffff;
    }
    else {
      uVar6 = 0xd3f21c;
      uVar4 = 0x20;
      uVar5 = 0x4fe;
    }
  }
  else {
    uVar6 = 0xd3f1c8;
    uVar4 = 2;
    uVar5 = 0x4f6;
  }
  FUN_0005e784(3,uVar4,6,0xd3e720,0x65df70,uVar5,uVar6,0x65df80);
  uStack_44 = 0;
LAB_0006c4cc:
  uStack_7c = 0xffffffff;
  FUN_005f0cd8(auStack_e0,iStack_4c + 0x68,0xd880c8);
  iStack_10 = iStack_4c + 0x84;
  uStack_7c = 3;
  FUN_005f0cd8(auStack_c0,auStack_e0,acStack_1f0);
  uStack_7c = 2;
  FUN_005f0cd8(auStack_a0,auStack_c0,0xd3f1f0);
  uStack_7c = 1;
  FUN_005ea15c(iStack_10,auStack_a0,0,0xffffffff);
  FUN_005e8e00(auStack_a0);
  FUN_005e8e00(auStack_c0);
  FUN_005e8e00(auStack_e0);
  FUN_003d12b8(auStack_80);
  return uStack_44;
}

