/* 0x0008fd90  FUN_0008fd90  size=1284 bytes */


void FUN_0008fd90(void)

{
  int iVar1;
  uint uVar2;
  undefined4 ***pppuVar3;
  undefined1 auStack_e8 [8];
  undefined1 auStack_e0 [4];
  undefined4 **appuStack_dc [4];
  uint uStack_cc;
  uint uStack_c8;
  undefined1 auStack_b0 [4];
  int *piStack_ac;
  undefined1 auStack_a0 [4];
  undefined4 **appuStack_9c [4];
  uint uStack_8c;
  uint uStack_88;
  undefined1 auStack_80 [4];
  undefined4 uStack_7c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined1 *puStack_60;
  undefined4 uStack_5c;
  undefined1 *puStack_58;
  undefined1 *puStack_54;
  int iStack_4c;
  uint uStack_48;
  undefined4 uStack_40;
  uint uStack_3c;
  uint uStack_38;
  int *piStack_2c;
  undefined4 uStack_28;
  uint uStack_24;
  uint uStack_20;
  int *piStack_14;
  uint uStack_10;
  uint uStack_c;
  
  puStack_54 = &stack0xffffff10;
  uStack_68 = 0x25710c;
  puStack_60 = auStack_e8;
  uStack_64 = 0xe970b6;
  uStack_5c = 0xa01b8;
  puStack_58 = (undefined1 *)register0x00000004;
  FUN_003d1214(auStack_80);
  uStack_48 = 0;
  iStack_4c = 0;
  uStack_c8 = 0xf;
  uStack_cc = 0;
  appuStack_dc[0] = (undefined4 **)((uint)appuStack_dc[0] & 0xffffff);
  uStack_7c = 5;
  uStack_40 = FUN_0005e890();
  uStack_88 = 0xf;
  appuStack_9c[0] = (undefined4 **)CONCAT13((char)uStack_48,appuStack_9c[0]._1_3_);
  uStack_8c = uStack_48;
  uStack_3c = FUN_0039b0f0(uRam00d94e68);
  uStack_38 = uStack_3c;
  if (0xfffffffe < uStack_3c) {
    uStack_7c = 5;
    FUN_002513e0(auStack_a0);
  }
  if (uStack_88 < uStack_3c) {
    uStack_7c = 5;
    FUN_005e7bb8(auStack_a0,uStack_3c,uStack_8c);
  }
  else if (uStack_38 == 0) {
    pppuVar3 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar3 = (undefined4 ***)appuStack_9c[0];
    }
    uStack_8c = 0;
    *(undefined1 *)pppuVar3 = 0;
  }
  if (uStack_38 != 0) {
    pppuVar3 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar3 = (undefined4 ***)appuStack_9c[0];
    }
    FUN_0039ac74(pppuVar3,uRam00d94e68,uStack_3c);
    pppuVar3 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar3 = (undefined4 ***)appuStack_9c[0];
    }
    uStack_8c = uStack_3c;
    *(undefined1 *)((int)pppuVar3 + uStack_3c) = 0;
  }
  uStack_7c = 4;
  FUN_005e817c(auStack_b0,uStack_40,auStack_a0);
  uStack_7c = 3;
  FUN_005f3d3c(auStack_b0,&iStack_4c);
  if (piStack_ac != (int *)0x0) {
    piStack_2c = piStack_ac;
    iVar1 = -1;
    if (piStack_ac[3] != 0) {
      uStack_7c = 4;
      iVar1 = FUN_001d9204(piStack_ac[3],0xffffffff);
    }
    if (iVar1 == 0) {
      *piStack_2c = *piStack_2c + -1;
      if (piStack_2c[3] != 0) {
        uStack_7c = 4;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e75e4(auStack_a0,1,0);
  uStack_48 = 1;
  if ((iStack_4c != 0) && (uStack_48 = 2, iStack_4c != 100)) {
    uStack_48 = 0;
  }
  uStack_7c = 5;
  uStack_28 = FUN_0005e890();
  uStack_88 = 0xf;
  appuStack_9c[0] = (undefined4 **)((uint)appuStack_9c[0] & 0xffffff);
  uStack_8c = 0;
  uStack_24 = FUN_0039b0f0(uRam00d94e6c);
  uStack_20 = uStack_24;
  if (0xfffffffe < uStack_24) {
    uStack_7c = 5;
    FUN_002513e0(auStack_a0);
  }
  if (uStack_88 < uStack_24) {
    uStack_7c = 5;
    FUN_005e7bb8(auStack_a0,uStack_24,uStack_8c);
  }
  else if (uStack_20 == 0) {
    pppuVar3 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar3 = (undefined4 ***)appuStack_9c[0];
    }
    uStack_8c = 0;
    *(undefined1 *)pppuVar3 = 0;
  }
  if (uStack_20 != 0) {
    pppuVar3 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar3 = (undefined4 ***)appuStack_9c[0];
    }
    FUN_0039ac74(pppuVar3,uRam00d94e6c,uStack_24);
    pppuVar3 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar3 = (undefined4 ***)appuStack_9c[0];
    }
    uStack_8c = uStack_24;
    *(undefined1 *)((int)pppuVar3 + uStack_24) = 0;
  }
  uStack_7c = 2;
  FUN_005e817c(auStack_b0,uStack_28,auStack_a0);
  uStack_7c = 1;
  FUN_005ea8a8(auStack_b0,auStack_e0);
  if (piStack_ac != (int *)0x0) {
    piStack_14 = piStack_ac;
    iVar1 = -1;
    if (piStack_ac[3] != 0) {
      uStack_7c = 2;
      iVar1 = FUN_001d9204(piStack_ac[3],0xffffffff);
    }
    if (iVar1 == 0) {
      *piStack_14 = *piStack_14 + -1;
      if (piStack_14[3] != 0) {
        uStack_7c = 2;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e75e4(auStack_a0,1,0);
  uStack_10 = uStack_cc;
  uStack_c = FUN_0039b0f0(uRam00d94e70);
  uVar2 = 0;
  if (uStack_10 != 0) {
    pppuVar3 = appuStack_dc;
    if (0xf < uStack_c8) {
      pppuVar3 = (undefined4 ***)appuStack_dc[0];
    }
    uVar2 = uStack_c;
    if (uStack_10 < uStack_c) {
      uVar2 = uStack_10;
    }
    uVar2 = FUN_0039ac2c(pppuVar3,uRam00d94e70,uVar2);
  }
  if ((uVar2 == 0) && (uVar2 = (uint)(uStack_10 != uStack_c), uStack_10 < uStack_c)) {
    uVar2 = 0xffffffff;
  }
  if (uVar2 == 0) {
    uStack_7c = 5;
    FUN_001cdf38(uStack_48);
  }
  FUN_005e75e4(auStack_e0,1,0);
  FUN_003d12b8(auStack_80);
  return;
}

