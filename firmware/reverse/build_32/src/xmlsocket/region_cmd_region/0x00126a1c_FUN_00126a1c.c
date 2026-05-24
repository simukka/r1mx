/* 0x00126a1c  FUN_00126a1c  size=2256 bytes */


int FUN_00126a1c(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined4 uVar4;
  undefined4 ****ppppuVar5;
  undefined4 ****ppppuVar6;
  undefined1 auStack_1a8 [8];
  int *apiStack_1a0 [4];
  undefined1 auStack_190 [16];
  int *apiStack_180 [4];
  undefined1 auStack_170 [20];
  uint uStack_15c;
  undefined1 auStack_150 [4];
  undefined4 ***apppuStack_14c [4];
  uint uStack_13c;
  uint uStack_138;
  undefined1 auStack_130 [4];
  undefined4 ***apppuStack_12c [4];
  uint uStack_11c;
  uint uStack_118;
  undefined1 auStack_110 [4];
  undefined4 ***apppuStack_10c [4];
  uint uStack_fc;
  uint uStack_f8;
  undefined1 auStack_f0 [4];
  int *piStack_ec;
  undefined8 uStack_e0;
  undefined1 auStack_d0 [28];
  undefined1 auStack_b4 [36];
  undefined1 auStack_90 [4];
  undefined4 uStack_8c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined1 *puStack_70;
  undefined4 uStack_6c;
  undefined1 *puStack_68;
  undefined1 *puStack_64;
  int iStack_5c;
  int iStack_58;
  int iStack_54;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  uint uStack_40;
  uint uStack_3c;
  undefined1 *puStack_38;
  uint uStack_34;
  uint uStack_30;
  int *piStack_2c;
  uint uStack_28;
  uint uStack_24;
  int *piStack_20;
  int iStack_1c;
  int *piStack_10;
  
  puStack_64 = &stack0xfffffe40;
  uStack_78 = 0x25710c;
  puStack_70 = auStack_1a8;
  uStack_74 = 0xe99340;
  uStack_6c = 0x136f94;
  puStack_68 = (undefined1 *)register0x00000004;
  iStack_5c = param_1;
  FUN_003d1214(auStack_90);
  iStack_58 = 0;
  iStack_54 = 0;
  iStack_50 = 0;
  uVar4 = 0xea09a8;
  if (0xf < uRam00ea09bc) {
    uVar4 = uRam00ea09a8;
  }
  uStack_8c = 0xffffffff;
  FUN_002264b0(apiStack_180,iStack_5c + 0x30,uVar4);
  uVar4 = 0xea083c;
  if (0xf < uRam00ea0850) {
    uVar4 = uRam00ea083c;
  }
  uStack_8c = 0xffffffff;
  FUN_002264b0(auStack_190,apiStack_180,uVar4);
  FUN_002264b0(apiStack_1a0,auStack_190,0xd4bd98);
  if ((apiStack_1a0[0] == (int *)0x0) ||
     (iVar2 = (**(code **)(*apiStack_1a0[0] + 0x2c))(), iVar2 == 0)) {
    iStack_4c = 0;
  }
  else {
    iStack_4c = (**(code **)(*apiStack_1a0[0] + 0x2c))();
  }
  uVar4 = 0xea09a8;
  if (0xf < uRam00ea09bc) {
    uVar4 = uRam00ea09a8;
  }
  uStack_8c = 0xffffffff;
  FUN_002264b0(apiStack_1a0,iStack_5c + 0x30,uVar4);
  uVar4 = 0xea083c;
  if (0xf < uRam00ea0850) {
    uVar4 = uRam00ea083c;
  }
  uStack_8c = 0xffffffff;
  FUN_002264b0(auStack_190,apiStack_1a0,uVar4);
  FUN_002264b0(apiStack_180,auStack_190,0xd4bda0);
  if ((apiStack_180[0] == (int *)0x0) ||
     (iVar2 = (**(code **)(*apiStack_180[0] + 0x2c))(), iVar2 == 0)) {
    iStack_48 = 0;
  }
  else {
    iStack_48 = (**(code **)(*apiStack_180[0] + 0x2c))();
  }
  uStack_8c = 0xffffffff;
  FUN_005ea3bc(auStack_170,0xd6f55c);
  if (iStack_4c != 0) {
    uStack_8c = 0xd;
    iStack_54 = FUN_002260a4(iStack_4c);
  }
  if (iStack_48 != 0) {
    uStack_8c = 0xd;
    iStack_50 = FUN_002260a4(iStack_48);
  }
  if (iStack_54 != 0) {
    uStack_8c = 0xd;
    FUN_005ea3bc(auStack_150,iStack_54);
    uStack_8c = 0xc;
    FUN_005ea15c(auStack_170,auStack_150,0,0xffffffff);
    FUN_005e8e00(auStack_150);
    iStack_58 = 1;
  }
  if (iStack_50 != 0) {
    if (iStack_54 == 0) {
      uStack_8c = 0xd;
      FUN_005ea3bc(auStack_110,iStack_50);
      uStack_8c = 8;
      FUN_005ea15c(auStack_170,auStack_110,0,0xffffffff);
      puVar3 = auStack_110;
    }
    else {
      uStack_8c = 0xd;
      FUN_005ea3bc(auStack_130,iStack_50);
      uStack_8c = 0xb;
      FUN_005ea3bc(auStack_110,0xd7ce94);
      uStack_3c = uStack_11c;
      uStack_40 = 0xffffffff;
      if (uStack_11c != 0xffffffff) {
        uStack_40 = uStack_11c;
      }
      if (~uStack_fc <= uStack_40) {
        uStack_8c = 10;
        FUN_002513e0(auStack_110);
      }
      if (uStack_40 != 0) {
        uStack_3c = uStack_fc + uStack_40;
        uStack_8c = 10;
        iVar2 = FUN_005f0030(auStack_110,uStack_3c,0);
        if (iVar2 != 0) {
          ppppuVar5 = apppuStack_10c;
          if (0xf < uStack_f8) {
            ppppuVar5 = (undefined4 ****)apppuStack_10c[0];
          }
          ppppuVar6 = apppuStack_12c;
          if (0xf < uStack_118) {
            ppppuVar6 = (undefined4 ****)apppuStack_12c[0];
          }
          FUN_0039ac74((int)ppppuVar5 + uStack_fc,ppppuVar6,uStack_40);
          ppppuVar5 = apppuStack_10c;
          if (0xf < uStack_f8) {
            ppppuVar5 = (undefined4 ****)apppuStack_10c[0];
          }
          uStack_fc = uStack_3c;
          *(undefined1 *)((int)ppppuVar5 + uStack_3c) = 0;
        }
      }
      uStack_8c = 10;
      FUN_005f4290(auStack_150,auStack_110);
      FUN_005e8e00(auStack_110);
      puStack_38 = auStack_170;
      uStack_30 = uStack_13c;
      uStack_34 = 0xffffffff;
      if (uStack_13c != 0xffffffff) {
        uStack_34 = uStack_13c;
      }
      if (~uStack_15c <= uStack_34) {
        uStack_8c = 9;
        FUN_002513e0(puStack_38);
      }
      if (uStack_34 != 0) {
        uStack_30 = *(int *)(puStack_38 + 0x14) + uStack_34;
        uStack_8c = 9;
        iVar2 = FUN_005f0030(puStack_38,uStack_30,0);
        if (iVar2 != 0) {
          puVar3 = puStack_38 + 4;
          if (0xf < *(uint *)(puStack_38 + 0x18)) {
            puVar3 = *(undefined1 **)(puStack_38 + 4);
          }
          ppppuVar5 = apppuStack_14c;
          if (0xf < uStack_138) {
            ppppuVar5 = (undefined4 ****)apppuStack_14c[0];
          }
          FUN_0039ac74(puVar3 + *(int *)(puStack_38 + 0x14),ppppuVar5,uStack_34);
          uVar1 = uStack_30;
          puVar3 = puStack_38 + 4;
          if (0xf < *(uint *)(puStack_38 + 0x18)) {
            puVar3 = *(undefined1 **)(puStack_38 + 4);
          }
          *(uint *)(puStack_38 + 0x14) = uStack_30;
          puVar3[uVar1] = 0;
        }
      }
      FUN_005e8e00(auStack_150);
      puVar3 = auStack_130;
    }
    FUN_005e8e00(puVar3);
    iStack_58 = 1;
  }
  if (iStack_58 != 0) {
    uVar4 = 0xea09a8;
    if (0xf < uRam00ea09bc) {
      uVar4 = uRam00ea09a8;
    }
    uStack_8c = 0xd;
    FUN_0005e784(3,0x20,0xb,0xd4bc0c,0x6626cc,0x488,0xd4bda8,uVar4);
    uVar4 = FUN_0005e890();
    FUN_005e817c(auStack_f0,uVar4,*(int *)(iStack_5c + 0x3c) + 0x30);
    if (piStack_ec != (int *)0x0) {
      uStack_8c = 7;
      piStack_2c = piStack_ec;
      FUN_005f0cd8(auStack_130,0xea09a4,0xdb8b44);
      uStack_8c = 6;
      FUN_005f4290(auStack_150,auStack_130);
      uStack_24 = uRam00ea084c;
      uStack_28 = 0xffffffff;
      if (uRam00ea084c != 0xffffffff) {
        uStack_28 = uRam00ea084c;
      }
      if (~uStack_13c <= uStack_28) {
        uStack_8c = 5;
        FUN_002513e0(auStack_150);
      }
      if (uStack_28 != 0) {
        uStack_24 = uStack_13c + uStack_28;
        uStack_8c = 5;
        iVar2 = FUN_005f0030(auStack_150,uStack_24,0);
        if (iVar2 != 0) {
          ppppuVar5 = apppuStack_14c;
          if (0xf < uStack_138) {
            ppppuVar5 = (undefined4 ****)apppuStack_14c[0];
          }
          uVar4 = 0xea083c;
          if (0xf < uRam00ea0850) {
            uVar4 = uRam00ea083c;
          }
          FUN_0039ac74((int)ppppuVar5 + uStack_13c,uVar4,uStack_28);
          ppppuVar5 = apppuStack_14c;
          if (0xf < uStack_138) {
            ppppuVar5 = (undefined4 ****)apppuStack_14c[0];
          }
          uStack_13c = uStack_24;
          *(undefined1 *)((int)ppppuVar5 + uStack_24) = 0;
        }
      }
      uStack_8c = 5;
      FUN_005f4290(auStack_110,auStack_150);
      FUN_005e8e00(auStack_150);
      FUN_005e8e00(auStack_130);
      iVar2 = -1;
      if (piStack_2c[5] != 0) {
        uStack_8c = 4;
        iVar2 = FUN_001d9204(piStack_2c[5],0xffffffff);
      }
      if (iVar2 == 0) {
        piStack_20 = piStack_2c + 0x19;
        iStack_1c = FUN_00616f40(piStack_20,auStack_110);
        if (iStack_1c == piStack_2c[0x1b]) {
          FUN_005e8e80(auStack_130);
          uStack_8c = 3;
          FUN_005f4290(auStack_d0,auStack_110);
          uStack_8c = 2;
          FUN_005f4290(auStack_b4,auStack_130);
          uStack_8c = 1;
          uStack_e0 = FUN_0061a308(piStack_20,auStack_d0);
          iStack_1c = (int)((ulonglong)uStack_e0 >> 0x20);
          FUN_005e8e00(auStack_b4);
          FUN_005e8e00(auStack_d0);
          FUN_005e8e00(auStack_130);
        }
        uStack_8c = 4;
        FUN_005ea15c(iStack_1c + 0x24,auStack_170,0,0xffffffff);
        FUN_00616f40(piStack_2c + 0x19,auStack_110);
        if (piStack_2c[5] != 0) {
          uStack_8c = 4;
          FUN_001d92bc();
        }
      }
      FUN_005e8e00(auStack_110);
    }
    if (piStack_ec != (int *)0x0) {
      piStack_10 = piStack_ec;
      iVar2 = -1;
      if (piStack_ec[3] != 0) {
        uStack_8c = 0xd;
        iVar2 = FUN_001d9204(piStack_ec[3],0xffffffff);
      }
      if ((iVar2 == 0) && (*piStack_10 = *piStack_10 + -1, piStack_10[3] != 0)) {
        uStack_8c = 0xd;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e8e00(auStack_170);
  FUN_003d12b8(auStack_90);
  return iStack_58;
}

