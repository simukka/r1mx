/* 0x000f038c  FUN_000f038c  size=940 bytes */


void FUN_000f038c(void)

{
  int iVar1;
  uint uVar2;
  undefined4 ***pppuVar3;
  undefined4 uVar4;
  undefined1 auStack_b8 [8];
  undefined1 auStack_b0 [4];
  undefined4 **appuStack_ac [4];
  uint uStack_9c;
  uint uStack_98;
  undefined1 auStack_90 [4];
  int *piStack_8c;
  undefined1 auStack_80 [32];
  undefined1 auStack_60 [4];
  undefined4 uStack_5c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined1 *puStack_40;
  undefined4 uStack_3c;
  undefined1 *puStack_38;
  undefined1 *puStack_34;
  undefined4 uStack_2c;
  int *piStack_1c;
  uint uStack_18;
  uint uStack_14;
  uint uStack_10;
  uint uStack_c;
  uint uStack_8;
  uint uStack_4;
  
  puStack_34 = &stack0xffffff40;
  uStack_48 = 0x25710c;
  puStack_40 = auStack_b8;
  uStack_44 = 0xe984be;
  uStack_3c = 0x1006c4;
  puStack_38 = (undefined1 *)register0x00000004;
  FUN_003d1214(auStack_60);
  FUN_005e8e80(auStack_b0);
  uStack_5c = 3;
  uStack_2c = FUN_0005e890();
  FUN_005ea3bc(auStack_80,0xd48ee4);
  uStack_5c = 2;
  FUN_005e817c(auStack_90,uStack_2c,auStack_80);
  uStack_5c = 1;
  FUN_005ea8a8(auStack_90,auStack_b0);
  if (piStack_8c != (int *)0x0) {
    piStack_1c = piStack_8c;
    iVar1 = -1;
    if (piStack_8c[3] != 0) {
      uStack_5c = 2;
      iVar1 = FUN_001d9204(piStack_8c[3],0xffffffff);
    }
    if (iVar1 == 0) {
      *piStack_1c = *piStack_1c + -1;
      if (piStack_1c[3] != 0) {
        uStack_5c = 2;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e75e4(auStack_80,1,0);
  uStack_18 = uStack_9c;
  uStack_14 = FUN_0039b0f0(uRam00d950d8);
  uVar2 = 0;
  if (uStack_18 != 0) {
    pppuVar3 = appuStack_ac;
    if (0xf < uStack_98) {
      pppuVar3 = (undefined4 ***)appuStack_ac[0];
    }
    uVar2 = uStack_14;
    if (uStack_18 < uStack_14) {
      uVar2 = uStack_18;
    }
    uVar2 = FUN_0039ac2c(pppuVar3,uRam00d950d8,uVar2);
  }
  if ((uVar2 == 0) && (uVar2 = (uint)(uStack_18 != uStack_14), uStack_18 < uStack_14)) {
    uVar2 = 0xffffffff;
  }
  if (uVar2 == 0) {
    uStack_5c = 3;
    FUN_001cdfd4();
    uVar4 = 1;
LAB_000f079c:
    FUN_001ce040(uVar4);
    iVar1 = 0;
  }
  else {
    uStack_10 = uStack_9c;
    uStack_c = FUN_0039b0f0(uRam00d950dc);
    uVar2 = 0;
    if (uStack_10 != 0) {
      pppuVar3 = appuStack_ac;
      if (0xf < uStack_98) {
        pppuVar3 = (undefined4 ***)appuStack_ac[0];
      }
      uVar2 = uStack_c;
      if (uStack_10 < uStack_c) {
        uVar2 = uStack_10;
      }
      uVar2 = FUN_0039ac2c(pppuVar3,uRam00d950dc,uVar2);
    }
    if ((uVar2 == 0) && (uVar2 = (uint)(uStack_10 != uStack_c), uStack_10 < uStack_c)) {
      uVar2 = 0xffffffff;
    }
    if (uVar2 == 0) {
      uStack_5c = 3;
      FUN_001cdfd4(1);
      uVar4 = 1;
    }
    else {
      uStack_8 = uStack_9c;
      uStack_4 = FUN_0039b0f0(uRam00d950e0);
      uVar2 = 0;
      if (uStack_8 != 0) {
        pppuVar3 = appuStack_ac;
        if (0xf < uStack_98) {
          pppuVar3 = (undefined4 ***)appuStack_ac[0];
        }
        uVar2 = uStack_4;
        if (uStack_8 < uStack_4) {
          uVar2 = uStack_8;
        }
        uVar2 = FUN_0039ac2c(pppuVar3,uRam00d950e0,uVar2);
      }
      if ((uVar2 == 0) && (uVar2 = (uint)(uStack_8 != uStack_4), uStack_8 < uStack_4)) {
        uVar2 = 0xffffffff;
      }
      if (uVar2 != 0) {
        uStack_5c = 3;
        FUN_001cdfd4(0);
        uVar4 = 0;
        goto LAB_000f079c;
      }
      uStack_5c = 3;
      FUN_001cdfd4(1);
      uVar4 = 0;
    }
    FUN_001ce040(uVar4);
    iVar1 = FUN_001d0064();
    iVar1 = iVar1 * 0xa0 + -0xa0;
  }
  FUN_001cdf68(iVar1);
  uStack_5c = 3;
  FUN_001ddd3c(0,2);
  FUN_001ddc70();
  FUN_001ddd3c(1,2);
  FUN_005e75e4(auStack_b0,1,0);
  FUN_003d12b8(auStack_60);
  return;
}

