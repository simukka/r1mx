/* 0x00127454  FUN_00127454  size=1960 bytes */


/* WARNING: Heritage AFTER dead removal. Example location: s0xfffffe74 : 0x00127718 */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

int FUN_00127454(int param_1)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  undefined1 *puVar5;
  undefined4 uVar6;
  undefined4 ****ppppuVar7;
  undefined4 ****ppppuVar8;
  undefined4 *puVar9;
  undefined1 auStack_198 [8];
  undefined1 auStack_190 [4];
  undefined4 ***apppuStack_18c [4];
  uint uStack_17c;
  uint uStack_178;
  int *apiStack_170 [4];
  undefined1 auStack_160 [16];
  undefined1 auStack_150 [16];
  undefined1 auStack_140 [4];
  undefined4 ***apppuStack_13c [4];
  uint uStack_12c;
  uint uStack_128;
  undefined1 auStack_120 [4];
  undefined4 ***apppuStack_11c [4];
  uint uStack_10c;
  uint uStack_108;
  undefined1 auStack_100 [4];
  undefined4 ***apppuStack_fc [4];
  uint uStack_ec;
  uint uStack_e8;
  undefined1 auStack_e0 [4];
  int *piStack_dc;
  undefined8 uStack_d0;
  undefined1 auStack_c0 [28];
  undefined1 auStack_a4 [36];
  undefined1 auStack_80 [4];
  undefined4 uStack_7c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined1 *puStack_60;
  undefined4 uStack_5c;
  int iStack_48;
  uint uStack_40;
  uint uStack_30;
  uint uStack_24;
  int iStack_18;
  
  uStack_68 = 0x25710c;
  puStack_60 = auStack_198;
  uStack_64 = 0xe9935e;
  uStack_5c = 0x1378d8;
  FUN_003d1214(auStack_80);
  uStack_7c = 0xffffffff;
  FUN_005ea3bc(auStack_190,0xd6f55c);
  iStack_48 = 0;
  puVar9 = &uRam00ea09a8;
  if (0xf < uRam00ea09bc) {
    puVar9 = uRam00ea09a8;
  }
  uStack_7c = 0xc;
  FUN_002264b0(auStack_150,param_1 + 0x30,puVar9);
  puVar9 = &uRam00ea0858;
  if (0xf < uRam00ea086c) {
    puVar9 = uRam00ea0858;
  }
  uStack_7c = 0xc;
  FUN_002264b0(auStack_160,auStack_150,puVar9);
  FUN_002264b0(apiStack_170,auStack_160,0xd4bdbc);
  if ((apiStack_170[0] == (int *)0x0) ||
     (iVar3 = (**(code **)(*apiStack_170[0] + 0x2c))(), iVar3 == 0)) {
    iVar3 = 0;
  }
  else {
    iVar3 = (**(code **)(*apiStack_170[0] + 0x2c))();
  }
  for (; iVar3 != 0; iVar3 = FUN_00225120(iVar3)) {
    uStack_7c = 0xc;
    iVar4 = FUN_002260a4(iVar3);
    if (iVar4 != 0) {
      if (uStack_17c == 0) {
        uStack_7c = 0xc;
        FUN_005ea3bc(auStack_100,iVar4);
        uStack_7c = 8;
        FUN_005ea15c(auStack_190,auStack_100,0,0xffffffff);
        puVar5 = auStack_100;
      }
      else {
        FUN_005ea3bc(auStack_120,iVar4);
        uStack_7c = 0xb;
        FUN_005ea3bc(auStack_100,0xd7ce94);
        uStack_40 = 0xffffffff;
        if (uStack_10c != 0xffffffff) {
          uStack_40 = uStack_10c;
        }
        if (~uStack_ec <= uStack_40) {
          uStack_7c = 10;
          FUN_002513e0(auStack_100);
        }
        if (uStack_40 != 0) {
          uVar2 = uStack_ec + uStack_40;
          uStack_7c = 10;
          iVar4 = FUN_005f0030(auStack_100,uVar2,0);
          if (iVar4 != 0) {
            ppppuVar7 = apppuStack_fc;
            if (0xf < uStack_e8) {
              ppppuVar7 = (undefined4 ****)apppuStack_fc[0];
            }
            ppppuVar8 = apppuStack_11c;
            if (0xf < uStack_108) {
              ppppuVar8 = (undefined4 ****)apppuStack_11c[0];
            }
            FUN_0039ac74((int)ppppuVar7 + uStack_ec,ppppuVar8,uStack_40);
            ppppuVar7 = apppuStack_fc;
            if (0xf < uStack_e8) {
              ppppuVar7 = (undefined4 ****)apppuStack_fc[0];
            }
            uStack_ec = uVar2;
            *(undefined1 *)((int)ppppuVar7 + uVar2) = 0;
          }
        }
        uStack_7c = 10;
        FUN_005f4290(auStack_140,auStack_100);
        FUN_005e8e00(auStack_100);
        uStack_30 = 0xffffffff;
        if (uStack_12c != 0xffffffff) {
          uStack_30 = uStack_12c;
        }
        if (~uStack_17c <= uStack_30) {
          uStack_7c = 9;
          FUN_002513e0(auStack_190);
        }
        if (uStack_30 != 0) {
          uVar2 = uStack_17c + uStack_30;
          uStack_7c = 9;
          iVar4 = FUN_005f0030(auStack_190,uVar2,0);
          if (iVar4 != 0) {
            ppppuVar7 = apppuStack_18c;
            if (0xf < uStack_178) {
              ppppuVar7 = (undefined4 ****)apppuStack_18c[0];
            }
            ppppuVar8 = apppuStack_13c;
            if (0xf < uStack_128) {
              ppppuVar8 = (undefined4 ****)apppuStack_13c[0];
            }
            FUN_0039ac74((int)ppppuVar7 + uStack_17c,ppppuVar8,uStack_30);
            ppppuVar7 = apppuStack_18c;
            if (0xf < uStack_178) {
              ppppuVar7 = (undefined4 ****)apppuStack_18c[0];
            }
            *(undefined1 *)((int)ppppuVar7 + uVar2) = 0;
            uStack_17c = uVar2;
          }
        }
        FUN_005e8e00(auStack_140);
        puVar5 = auStack_120;
      }
      FUN_005e8e00(puVar5);
      iStack_48 = 1;
    }
    uStack_7c = 0xc;
  }
  if (iStack_48 != 0) {
    puVar9 = &uRam00ea09a8;
    if (0xf < uRam00ea09bc) {
      puVar9 = uRam00ea09a8;
    }
    uStack_7c = 0xc;
    FUN_0005e784(3,0x10,0xb,0xd4bc0c,0x6626ec,0x44a,0xd4bda8,puVar9);
    uVar6 = FUN_0005e890();
    FUN_005e817c(auStack_e0,uVar6,*(int *)(param_1 + 0x3c) + 0x30);
    piVar1 = piStack_dc;
    if (piStack_dc != (int *)0x0) {
      uStack_7c = 7;
      FUN_005f0cd8(auStack_120,0xea09a4,0xdb8b44);
      uStack_7c = 6;
      FUN_005f4290(auStack_140,auStack_120);
      uStack_24 = 0xffffffff;
      if (uRam00ea0868 != 0xffffffff) {
        uStack_24 = uRam00ea0868;
      }
      if (~uStack_12c <= uStack_24) {
        uStack_7c = 5;
        FUN_002513e0(auStack_140);
      }
      if (uStack_24 != 0) {
        uVar2 = uStack_12c + uStack_24;
        uStack_7c = 5;
        iVar3 = FUN_005f0030(auStack_140,uVar2,0);
        if (iVar3 != 0) {
          ppppuVar7 = apppuStack_13c;
          if (0xf < uStack_128) {
            ppppuVar7 = (undefined4 ****)apppuStack_13c[0];
          }
          puVar9 = &uRam00ea0858;
          if (0xf < uRam00ea086c) {
            puVar9 = uRam00ea0858;
          }
          FUN_0039ac74((int)ppppuVar7 + uStack_12c,puVar9,uStack_24);
          ppppuVar7 = apppuStack_13c;
          if (0xf < uStack_128) {
            ppppuVar7 = (undefined4 ****)apppuStack_13c[0];
          }
          uStack_12c = uVar2;
          *(undefined1 *)((int)ppppuVar7 + uVar2) = 0;
        }
      }
      uStack_7c = 5;
      FUN_005f4290(auStack_100,auStack_140);
      FUN_005e8e00(auStack_140);
      FUN_005e8e00(auStack_120);
      iVar3 = -1;
      if (piVar1[5] != 0) {
        uStack_7c = 4;
        iVar3 = FUN_001d9204(piVar1[5],0xffffffff);
      }
      if (iVar3 == 0) {
        iStack_18 = FUN_00616f40(piVar1 + 0x19,auStack_100);
        if (iStack_18 == piVar1[0x1b]) {
          FUN_005e8e80(auStack_120);
          uStack_7c = 3;
          FUN_005f4290(auStack_c0,auStack_100);
          uStack_7c = 2;
          FUN_005f4290(auStack_a4,auStack_120);
          uStack_7c = 1;
          uStack_d0 = FUN_0061a308(piVar1 + 0x19,auStack_c0);
          iStack_18 = (int)((ulonglong)uStack_d0 >> 0x20);
          FUN_005e8e00(auStack_a4);
          FUN_005e8e00(auStack_c0);
          FUN_005e8e00(auStack_120);
        }
        uStack_7c = 4;
        FUN_005ea15c(iStack_18 + 0x24,auStack_190,0,0xffffffff);
        FUN_00616f40(piVar1 + 0x19,auStack_100);
        if (piVar1[5] != 0) {
          uStack_7c = 4;
          FUN_001d92bc();
        }
      }
      FUN_005e8e00(auStack_100);
    }
    if (piStack_dc != (int *)0x0) {
      iVar3 = -1;
      if (piStack_dc[3] != 0) {
        uStack_7c = 0xc;
        iVar3 = FUN_001d9204(piStack_dc[3],0xffffffff);
      }
      if ((iVar3 == 0) && (*piStack_dc = *piStack_dc + -1, piStack_dc[3] != 0)) {
        uStack_7c = 0xc;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e8e00(auStack_190);
  FUN_003d12b8(auStack_80);
  return iStack_48;
}

