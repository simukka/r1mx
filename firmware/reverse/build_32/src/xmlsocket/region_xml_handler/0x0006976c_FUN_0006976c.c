/* 0x0006976c  FUN_0006976c  size=528 bytes */


int FUN_0006976c(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_78 [8];
  undefined1 auStack_70 [32];
  undefined1 auStack_50 [4];
  undefined4 uStack_4c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 *puStack_30;
  undefined4 uStack_2c;
  undefined1 *puStack_28;
  undefined1 *puStack_24;
  int iStack_1c;
  int iStack_18;
  int iStack_14;
  int iStack_10;
  int iStack_c;
  
  puStack_24 = &stack0xffffff80;
  uStack_38 = 0x25710c;
  puStack_30 = auStack_78;
  uStack_2c = 0x798c4;
  uStack_34 = 0xe969f4;
  puStack_28 = (undefined1 *)register0x00000004;
  iStack_18 = param_1;
  FUN_003d1214(auStack_50);
  FUN_005e8e80(auStack_70);
  uStack_4c = 1;
  FUN_0005e784(3,0x400,6,0xd3e720,0x65defc,0x63a,0xd52788,0x65df08);
  FUN_005ea15c(auStack_70,0xe9ee54,0,0xffffffff);
  uVar1 = FUN_0005e8a8();
  iStack_10 = iStack_18 + 0xa0;
  iStack_14 = FUN_000a82b0(uVar1,iStack_10,auStack_70,0);
  if (iStack_14 == 0) {
    uStack_4c = 1;
    FUN_005ea15c(auStack_70,0xe9ee38,0,0xffffffff);
    uVar1 = FUN_0005e8a8();
    FUN_000a8138(uVar1,auStack_70);
    uVar1 = FUN_0005e8a8();
    iStack_c = iStack_18 + 0xbc;
    iVar2 = FUN_000a82b0(uVar1,iStack_c,auStack_70,0);
    if (iVar2 == -1) {
      iVar2 = iStack_18 + 0xc0;
      if (0xf < *(uint *)(iStack_c + 0x18)) {
        iVar2 = *(int *)(iStack_c + 4);
      }
      uStack_4c = 1;
      FUN_0005e784(0,3,6,0xd3e720,0x65defc,0x650,0xd3efc8,iVar2);
    }
    FUN_005e8e00(auStack_70);
    iStack_1c = 0;
  }
  else {
    iVar2 = iStack_18 + 0xa4;
    if (0xf < *(uint *)(iStack_10 + 0x18)) {
      iVar2 = *(int *)(iStack_10 + 4);
    }
    uStack_4c = 1;
    FUN_0005e784(0,3,6,0xd3e720,0x65defc,0x641,0xd3efc8,iVar2);
    FUN_005e8e00(auStack_70);
    iStack_1c = iStack_14;
  }
  FUN_003d12b8(auStack_50);
  return iStack_1c;
}

