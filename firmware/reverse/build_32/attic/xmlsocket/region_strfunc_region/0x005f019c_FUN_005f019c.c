/* 0x005f019c  FUN_005f019c  size=424 bytes */


undefined4 FUN_005f019c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 auStack_98 [8];
  undefined1 auStack_90 [4];
  int *piStack_8c;
  undefined1 auStack_80 [32];
  undefined1 auStack_60 [4];
  undefined4 uStack_5c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined1 *puStack_40;
  undefined1 *puStack_3c;
  undefined1 *puStack_38;
  undefined1 *puStack_34;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  int iStack_14;
  int *piStack_4;
  
  puStack_34 = &stack0xffffff50;
  uStack_48 = 0x25710c;
  puStack_40 = auStack_98;
  uStack_44 = 0xe964b0;
  puStack_3c = &LAB_006002d0;
  puStack_38 = (undefined1 *)register0x00000004;
  uStack_28 = param_1;
  uStack_24 = param_2;
  uStack_20 = param_3;
  uStack_1c = param_4;
  FUN_003d1214(auStack_60);
  uStack_5c = 0xffffffff;
  uStack_18 = FUN_0005e890();
  FUN_005ea3bc(auStack_80,uStack_28);
  uStack_5c = 2;
  FUN_005e817c(auStack_90,uStack_18,auStack_80);
  uStack_5c = 1;
  iStack_14 = FUN_005eff88(auStack_90,uStack_24);
  if (piStack_8c != (int *)0x0) {
    piStack_4 = piStack_8c;
    iVar1 = -1;
    if (piStack_8c[3] != 0) {
      uStack_5c = 2;
      iVar1 = FUN_001d9204(piStack_8c[3],0xffffffff);
    }
    if (iVar1 == 0) {
      *piStack_4 = *piStack_4 + -1;
      if (piStack_4[3] != 0) {
        uStack_5c = 2;
        FUN_001d92bc();
      }
    }
  }
  FUN_005e75e4(auStack_80,1,0);
  uStack_2c = 0;
  if (iStack_14 != 0) {
    uStack_5c = 0xffffffff;
    FUN_0005e784(0,3,uStack_20,0xd3c4f0,0x65d124,0x35,0xd3c514,uStack_1c);
    uStack_2c = 0xffffffff;
  }
  FUN_003d12b8(auStack_60);
  return uStack_2c;
}

