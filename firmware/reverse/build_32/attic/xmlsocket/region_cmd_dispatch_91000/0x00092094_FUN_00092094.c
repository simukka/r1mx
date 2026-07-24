/* 0x00092094  FUN_00092094  size=2240 bytes */


void FUN_00092094(int param_1,uint param_2)

{
  undefined4 ***pppuVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  undefined1 auStack_b8 [8];
  undefined1 auStack_b0 [4];
  int *piStack_ac;
  undefined1 auStack_a0 [4];
  undefined4 **appuStack_9c [4];
  uint uStack_8c;
  uint uStack_88;
  undefined1 auStack_70 [4];
  int iStack_6c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined1 *puStack_50;
  undefined4 uStack_4c;
  undefined1 *puStack_48;
  undefined1 *puStack_44;
  int iStack_3c;
  uint uStack_38;
  undefined4 uStack_34;
  uint uStack_2c;
  uint uStack_28;
  int iStack_24;
  char *pcStack_20;
  char *pcStack_1c;
  int *piStack_10;
  int *piStack_c;
  
  puStack_44 = &stack0xffffff30;
  uStack_58 = 0x25710c;
  puStack_50 = auStack_b8;
  uStack_54 = 0xe970da;
  uStack_4c = 0xa24c8;
  puStack_48 = (undefined1 *)register0x00000004;
  iStack_3c = param_1;
  uStack_38 = param_2;
  FUN_003d1214(auStack_70);
  iStack_6c = 0xffffffff;
  uStack_34 = FUN_0005e890();
  uStack_88 = 0xf;
  appuStack_9c[0] = (undefined4 **)((uint)appuStack_9c[0] & 0xffffff);
  uStack_8c = 0;
  uStack_2c = FUN_0039b0f0(uRam00d94e84);
  uStack_28 = uStack_2c;
  if (0xfffffffe < uStack_2c) {
    iStack_6c = 0xffffffff;
    FUN_002513e0(auStack_a0);
  }
  if (uStack_88 < uStack_2c) {
    iStack_6c = 0xffffffff;
    FUN_005e7bb8(auStack_a0,uStack_2c,uStack_8c);
  }
  else if (uStack_28 == 0) {
    pppuVar1 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar1 = (undefined4 ***)appuStack_9c[0];
    }
    uStack_8c = 0;
    *(undefined1 *)pppuVar1 = 0;
  }
  if (uStack_28 != 0) {
    pppuVar1 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar1 = (undefined4 ***)appuStack_9c[0];
    }
    FUN_0039ac74(pppuVar1,uRam00d94e84,uStack_2c);
    pppuVar1 = appuStack_9c;
    if (0xf < uStack_88) {
      pppuVar1 = (undefined4 ***)appuStack_9c[0];
    }
    uStack_8c = uStack_2c;
    *(undefined1 *)((int)pppuVar1 + uStack_2c) = 0;
  }
  iStack_6c = 2;
  FUN_005e817c(auStack_b0,uStack_34,auStack_a0);
  FUN_005e75e4(auStack_a0,1,0);
  if (*(byte *)(iStack_3c + 0x68) == uStack_38) {
    if (piStack_ac == (int *)0x0) goto LAB_000924b0;
    piStack_c = piStack_ac;
    iVar2 = -1;
    if (piStack_ac[3] != 0) {
      iStack_6c = -1;
      iVar2 = FUN_001d9204(piStack_ac[3],0xffffffff);
    }
    if (iVar2 != 0) goto LAB_000924b0;
    iVar2 = piStack_c[3];
    iVar3 = *piStack_c;
    piVar4 = piStack_c;
  }
  else {
    *(char *)(iStack_3c + 0x68) = (char)uStack_38;
    if (uStack_38 == 0) {
      pcStack_1c = *(char **)(iStack_3c + 0x173f8);
      if ((((pcStack_1c != (char *)0x0) && (*(int *)(pcStack_1c + 4) != 0)) &&
          (*(int *)(pcStack_1c + 0x10) != 0)) && (*pcStack_1c != '\0')) {
        iStack_6c = 1;
        iVar2 = FUN_001da174();
        *pcStack_1c = '\x01' - (iVar2 == 0);
      }
      if (*(int *)(iStack_3c + 0x9c) != 0) {
        iStack_6c = 1;
        FUN_001a83e4();
        FUN_0005e784(3,3,0x17,0xd41584,0x65e708,0x680,0xd42078,*(undefined4 *)(iStack_3c + 0x9c));
        *(undefined4 *)(iStack_3c + 0x9c) = 0;
      }
    }
    else {
      if (*(int *)(iStack_3c + 0x9c) != 0) {
        iStack_6c = 1;
        FUN_001a83e4();
        FUN_0005e784(3,3,0x17,0xd41584,0x65e708,0x61b,0xd42078,*(undefined4 *)(iStack_3c + 0x9c));
        *(undefined4 *)(iStack_3c + 0x9c) = 0;
      }
      iStack_6c = 1;
      FUN_00091504(iStack_3c,auStack_b0);
      iStack_24 = *(int *)(iStack_3c + 0x8c);
      if (iStack_24 == 4) {
        iVar2 = FUN_001a8294(1,0,0x310,0x500,0x40);
        *(int *)(iStack_3c + 0x9c) = iVar2;
        if (iVar2 != 0) {
          FUN_001a8a64(iVar2,2,2,*(undefined4 *)(iStack_3c + 0x58),0,0x310,0x500,0x40);
        }
        iStack_6c = 1;
        FUN_0005e784(3,3,0x17,0xd41584,0x65e708,0x62b,0xd42090,*(undefined4 *)(iStack_3c + 0x9c));
      }
      else if (iStack_24 - 5U < 4) {
        iStack_6c = 1;
        iVar2 = FUN_001a8294(1,0x100,0x310,0x160,0x40);
        *(int *)(iStack_3c + 0x9c) = iVar2;
        if (iVar2 != 0) {
          FUN_001a8a64(iVar2,2,2,*(undefined4 *)(iStack_3c + 0x60),0x100,0x310,0x160,0x40);
        }
        iStack_6c = 1;
        FUN_0005e784(3,3,0x17,0xd41584,0x65e708,0x637,0xd42090,*(undefined4 *)(iStack_3c + 0x9c));
      }
      else if (iStack_24 == 0) {
        iStack_6c = 1;
        iVar2 = FUN_001a8294(1,0x100,0x310,0x160,0x40);
        *(int *)(iStack_3c + 0x9c) = iVar2;
        if (iVar2 != 0) {
          FUN_001a8a64(iVar2,2,2,*(undefined4 *)(iStack_3c + 0x60),0x100,0x310,0x160,0x40);
        }
        iStack_6c = 1;
        FUN_0005e784(3,3,0x17,0xd41584,0x65e708,0x643,0xd42090,*(undefined4 *)(iStack_3c + 0x9c));
      }
      else if (iStack_24 == 2) {
        iStack_6c = 1;
        iVar2 = FUN_001a8294(1,0,0x310,0x500,0x40);
        *(int *)(iStack_3c + 0x9c) = iVar2;
        if (iVar2 != 0) {
          FUN_001a8a64(iVar2,2,2,*(undefined4 *)(iStack_3c + 0x58),0,0x310,0x500,0x40);
        }
        iStack_6c = 1;
        FUN_0005e784(3,3,0x17,0xd41584,0x65e708,0x64f,0xd42090,*(undefined4 *)(iStack_3c + 0x9c));
      }
      else if (iStack_24 == 3) {
        iStack_6c = 1;
        iVar2 = FUN_001a8294(1,0x40,400,0x480,0x100);
        *(int *)(iStack_3c + 0x9c) = iVar2;
        if (iVar2 != 0) {
          FUN_001a8a64(iVar2,2,2,*(undefined4 *)(iStack_3c + 100),0x40,400,0x480,0x100);
        }
        iStack_6c = 1;
        FUN_0005e784(3,3,0x17,0xd41584,0x65e708,0x65b,0xd42090,*(undefined4 *)(iStack_3c + 0x9c));
      }
      else if (iStack_24 == 9) {
        *(undefined4 *)(iStack_3c + 0x9c) = 0;
      }
      else if (iStack_24 == 1) {
        iStack_6c = iStack_24;
        iVar2 = FUN_001a8294(1,0,0x310,0x500,0x40);
        *(int *)(iStack_3c + 0x9c) = iVar2;
        if (iVar2 != 0) {
          FUN_001a8a64(iVar2,2,2,*(undefined4 *)(iStack_3c + 0x58),0,0x310,0x500,0x40);
        }
        iStack_6c = iStack_24;
        FUN_0005e784(3,3,0x17,0xd41584,0x65e708,0x66b,0xd42090,*(undefined4 *)(iStack_3c + 0x9c));
      }
      if ((*(int *)(iStack_3c + 0x9c) == 0) && (*(int *)(iStack_3c + 0x8c) != 9)) {
        iStack_6c = 1;
        FUN_00442914();
        FUN_0005e784(0,3,0x17,0xd41584,0x65e708,0x671,0xd415f8,0x65e708);
      }
      pcStack_20 = *(char **)(iStack_3c + 0x173f8);
      if (((pcStack_20 != (char *)0x0) && (*(int *)(pcStack_20 + 4) != 0)) &&
         ((*(int *)(pcStack_20 + 0x10) != 0 && (*pcStack_20 == '\0')))) {
        iStack_6c = 1;
        iVar2 = FUN_001da0bc(*(int *)(pcStack_20 + 4),*(undefined4 *)(pcStack_20 + 8),
                             *(int *)(pcStack_20 + 0x10),*(undefined4 *)(pcStack_20 + 0xc));
        *pcStack_20 = iVar2 == 0;
      }
    }
    if (piStack_ac == (int *)0x0) goto LAB_000924b0;
    piStack_10 = piStack_ac;
    iVar2 = -1;
    if (piStack_ac[3] != 0) {
      iStack_6c = -1;
      iVar2 = FUN_001d9204(piStack_ac[3],0xffffffff);
    }
    if (iVar2 != 0) goto LAB_000924b0;
    iVar2 = piStack_10[3];
    iVar3 = *piStack_10;
    piVar4 = piStack_10;
  }
  *piVar4 = iVar3 + -1;
  if (iVar2 != 0) {
    iStack_6c = -1;
    FUN_001d92bc();
  }
LAB_000924b0:
  FUN_003d12b8(auStack_70);
  return;
}

