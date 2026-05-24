/* 0x0008b620  FUN_0008b620  size=2020 bytes */


void FUN_0008b620(int param_1)

{
  int iVar1;
  undefined4 ***pppuVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  undefined1 auStack_d8 [8];
  undefined1 auStack_d0 [4];
  int *piStack_cc;
  undefined1 auStack_c0 [4];
  undefined4 **appuStack_bc [4];
  uint uStack_ac;
  uint uStack_a8;
  undefined1 auStack_90 [4];
  undefined4 uStack_8c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined1 *puStack_70;
  undefined4 uStack_6c;
  undefined1 *puStack_68;
  undefined1 *puStack_64;
  int iStack_5c;
  undefined4 uStack_58;
  uint uStack_50;
  uint uStack_4c;
  int *piStack_40;
  undefined4 uStack_3c;
  uint uStack_38;
  uint uStack_34;
  int *piStack_28;
  undefined4 uStack_24;
  uint uStack_20;
  uint uStack_1c;
  int *piStack_10;
  
  puStack_64 = &stack0xffffff10;
  uStack_78 = 0x25710c;
  puStack_70 = auStack_d8;
  uStack_74 = 0xe9703c;
  uStack_6c = 0x9bc2c;
  puStack_68 = (undefined1 *)register0x00000004;
  iStack_5c = param_1;
  FUN_003d1214(auStack_90);
  uStack_8c = 0xffffffff;
  uStack_58 = FUN_0005e890();
  uStack_a8 = 0xf;
  appuStack_bc[0] = (undefined4 **)((uint)appuStack_bc[0] & 0xffffff);
  uStack_ac = 0;
  uStack_50 = FUN_0039b0f0(uRam00d94e0c);
  uStack_4c = uStack_50;
  if (0xfffffffe < uStack_50) {
    uStack_8c = 0xffffffff;
    FUN_002513e0(auStack_c0);
  }
  if (uStack_a8 < uStack_50) {
    uStack_8c = 0xffffffff;
    FUN_005e7bb8(auStack_c0,uStack_50,uStack_ac);
  }
  else if (uStack_4c == 0) {
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    uStack_ac = 0;
    *(undefined1 *)pppuVar2 = 0;
  }
  if (uStack_4c != 0) {
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    FUN_0039ac74(pppuVar2,uRam00d94e0c,uStack_50);
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    uStack_ac = uStack_50;
    *(undefined1 *)((int)pppuVar2 + uStack_50) = 0;
  }
  uStack_8c = 6;
  FUN_005e817c(auStack_d0,uStack_58,auStack_c0);
  uStack_8c = 5;
  FUN_005f3d3c(auStack_d0,iStack_5c + 0xd4);
  if (piStack_cc != (int *)0x0) {
    piStack_40 = piStack_cc;
    iVar1 = -1;
    if (piStack_cc[3] != 0) {
      uStack_8c = 6;
      iVar1 = FUN_001d9204(piStack_cc[3],0xffffffff);
    }
    if (iVar1 == 0) {
      *piStack_40 = *piStack_40 + -1;
      if (piStack_40[3] != 0) {
        uStack_8c = 6;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e75e4(auStack_c0,1,0);
  uStack_8c = 0xffffffff;
  uStack_3c = FUN_0005e890();
  uStack_a8 = 0xf;
  appuStack_bc[0] = (undefined4 **)((uint)appuStack_bc[0] & 0xffffff);
  uStack_ac = 0;
  uStack_38 = FUN_0039b0f0(uRam00d94e10);
  uStack_34 = uStack_38;
  if (0xfffffffe < uStack_38) {
    uStack_8c = 0xffffffff;
    FUN_002513e0(auStack_c0);
  }
  if (uStack_a8 < uStack_38) {
    uStack_8c = 0xffffffff;
    FUN_005e7bb8(auStack_c0,uStack_38,uStack_ac);
  }
  else if (uStack_34 == 0) {
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    uStack_ac = 0;
    *(undefined1 *)pppuVar2 = 0;
  }
  if (uStack_34 != 0) {
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    FUN_0039ac74(pppuVar2,uRam00d94e10,uStack_38);
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    uStack_ac = uStack_38;
    *(undefined1 *)((int)pppuVar2 + uStack_38) = 0;
  }
  uStack_8c = 4;
  FUN_005e817c(auStack_d0,uStack_3c,auStack_c0);
  uStack_8c = 3;
  FUN_005f3d3c(auStack_d0,iStack_5c + 0xdc);
  if (piStack_cc != (int *)0x0) {
    piStack_28 = piStack_cc;
    iVar1 = -1;
    if (piStack_cc[3] != 0) {
      uStack_8c = 4;
      iVar1 = FUN_001d9204(piStack_cc[3],0xffffffff);
    }
    if (iVar1 == 0) {
      *piStack_28 = *piStack_28 + -1;
      if (piStack_28[3] != 0) {
        uStack_8c = 4;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e75e4(auStack_c0,1,0);
  uStack_8c = 0xffffffff;
  uStack_24 = FUN_0005e890();
  uStack_a8 = 0xf;
  appuStack_bc[0] = (undefined4 **)((uint)appuStack_bc[0] & 0xffffff);
  uStack_ac = 0;
  uStack_20 = FUN_0039b0f0(uRam00d94e14);
  uStack_1c = uStack_20;
  if (0xfffffffe < uStack_20) {
    uStack_8c = 0xffffffff;
    FUN_002513e0(auStack_c0);
  }
  if (uStack_a8 < uStack_20) {
    uStack_8c = 0xffffffff;
    FUN_005e7bb8(auStack_c0,uStack_20,uStack_ac);
  }
  else if (uStack_1c == 0) {
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    uStack_ac = 0;
    *(undefined1 *)pppuVar2 = 0;
  }
  if (uStack_1c != 0) {
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    FUN_0039ac74(pppuVar2,uRam00d94e14,uStack_20);
    pppuVar2 = appuStack_bc;
    if (0xf < uStack_a8) {
      pppuVar2 = (undefined4 ***)appuStack_bc[0];
    }
    uStack_ac = uStack_20;
    *(undefined1 *)((int)pppuVar2 + uStack_20) = 0;
  }
  uStack_8c = 2;
  FUN_005e817c(auStack_d0,uStack_24,auStack_c0);
  uStack_8c = 1;
  FUN_005f3d3c(auStack_d0,iStack_5c + 0xd8);
  if (piStack_cc != (int *)0x0) {
    piStack_10 = piStack_cc;
    iVar1 = -1;
    if (piStack_cc[3] != 0) {
      uStack_8c = 2;
      iVar1 = FUN_001d9204(piStack_cc[3],0xffffffff);
    }
    if (iVar1 == 0) {
      *piStack_10 = *piStack_10 + -1;
      if (piStack_10[3] != 0) {
        uStack_8c = 2;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e75e4(auStack_c0,1,0);
  uVar3 = *(uint *)(iStack_5c + 0xd4);
  if ((int)uVar3 < 0) {
    uVar4 = FUN_0037517c(uVar3 & 1 | uVar3 >> 1);
    FUN_00374be8(uVar4,uVar4);
  }
  else {
    FUN_0037517c();
  }
  uVar5 = FUN_00373e9c();
  uVar5 = FUN_003739c0((int)((ulonglong)uVar5 >> 0x20),(int)uVar5,&MMIO_40590000,0);
  FUN_00373704((int)((ulonglong)uVar5 >> 0x20),(int)uVar5,0x40940000,0);
  iVar1 = FUN_003740a0();
  *(int *)(iStack_5c + 0xd4) = iVar1;
  if (iVar1 == 0) {
    iVar1 = 1;
  }
  uVar3 = *(uint *)(iStack_5c + 0xd8);
  *(int *)(iStack_5c + 0xd4) = iVar1;
  if ((int)uVar3 < 0) {
    uVar4 = FUN_0037517c(uVar3 & 1 | uVar3 >> 1);
    FUN_00374be8(uVar4,uVar4);
  }
  else {
    FUN_0037517c();
  }
  uVar5 = FUN_00373e9c();
  uVar5 = FUN_003739c0((int)((ulonglong)uVar5 >> 0x20),(int)uVar5,&MMIO_40590000,0);
  FUN_00373704((int)((ulonglong)uVar5 >> 0x20),(int)uVar5,0x40868000,0);
  iVar1 = FUN_003740a0();
  *(int *)(iStack_5c + 0xd8) = iVar1;
  if (iVar1 == 0) {
    iVar1 = 1;
  }
  uVar3 = *(uint *)(iStack_5c + 0xdc);
  *(int *)(iStack_5c + 0xd8) = iVar1;
  if ((int)uVar3 < 0) {
    uVar4 = FUN_0037517c(uVar3 & 1 | uVar3 >> 1);
    FUN_00374be8(uVar4,uVar4);
  }
  else {
    FUN_0037517c();
  }
  uVar5 = FUN_00373e9c();
  uVar5 = FUN_003739c0((int)((ulonglong)uVar5 >> 0x20),(int)uVar5,&MMIO_40590000,0);
  FUN_00373704((int)((ulonglong)uVar5 >> 0x20),(int)uVar5,0x40868000,0);
  iVar1 = FUN_003740a0();
  *(int *)(iStack_5c + 0xdc) = iVar1;
  if (0x500 < (uint)(*(int *)(iStack_5c + 0xd4) + iVar1)) {
    uStack_8c = 0xffffffff;
    FUN_0005e784(0,3,0x17,0xd41584,0x65e640,0xba7,0xd41d4c,0x65e640);
    *(int *)(iStack_5c + 0xd4) = 0x500 - *(int *)(iStack_5c + 0xdc);
  }
  if (0x2d0 < (uint)(*(int *)(iStack_5c + 0xd8) + *(int *)(iStack_5c + 0xdc))) {
    uStack_8c = 0xffffffff;
    FUN_0005e784(0,3,0x17,0xd41584,0x65e640,0xbaf,0xd41cec,0x65e640);
    *(int *)(iStack_5c + 0xd8) = 0x2d0 - *(int *)(iStack_5c + 0xdc);
  }
  FUN_003d12b8(auStack_90);
  return;
}

