/* 0x0006a14c  FUN_0006a14c  size=400 bytes */


undefined4 FUN_0006a14c(int param_1)

{
  uint uVar1;
  int iVar2;
  undefined1 auStack_98 [8];
  undefined1 auStack_90 [32];
  undefined1 auStack_70 [32];
  undefined1 auStack_50 [4];
  undefined4 uStack_4c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 *puStack_30;
  undefined4 uStack_2c;
  undefined1 *puStack_28;
  undefined1 *puStack_24;
  undefined4 uStack_1c;
  int iStack_18;
  int iStack_14;
  uint uStack_10;
  uint uStack_c;
  undefined4 uStack_8;
  
  puStack_24 = &stack0xffffff60;
  uStack_38 = 0x25710c;
  puStack_30 = auStack_98;
  uStack_34 = 0xe96a06;
  uStack_2c = 0x7a290;
  puStack_28 = (undefined1 *)register0x00000004;
  iStack_18 = param_1;
  FUN_003d1214(auStack_50);
  FUN_005e8e80(auStack_90);
  iStack_14 = iStack_18 + 0x44;
  uStack_10 = *(uint *)(iStack_18 + 0x58);
  uStack_c = FUN_0039b0f0(uRam00d94d34);
  uVar1 = 0;
  if (uStack_10 != 0) {
    iVar2 = iStack_18 + 0x48;
    if (0xf < *(uint *)(iStack_14 + 0x18)) {
      iVar2 = *(int *)(iStack_14 + 4);
    }
    uVar1 = uStack_c;
    if (uStack_10 < uStack_c) {
      uVar1 = uStack_10;
    }
    uVar1 = FUN_0039ac2c(iVar2,uRam00d94d34,uVar1);
  }
  if ((uVar1 == 0) && (uVar1 = (uint)(uStack_10 != uStack_c), uStack_10 < uStack_c)) {
    uVar1 = 0xffffffff;
  }
  if (uVar1 != 0) {
    uStack_4c = 1;
    iVar2 = FUN_00067684(iStack_18,auStack_90);
    if (iVar2 == 0) {
      uStack_4c = 1;
      FUN_005f4290(auStack_70,auStack_90);
      uStack_8 = FUN_0006303c(iStack_18,auStack_70);
      FUN_005e8e00(auStack_70);
      FUN_005e8e00(auStack_90);
      uStack_1c = uStack_8;
      goto LAB_0006a270;
    }
  }
  FUN_005e8e00(auStack_90);
  uStack_1c = 0;
LAB_0006a270:
  FUN_003d12b8(auStack_50);
  return uStack_1c;
}

