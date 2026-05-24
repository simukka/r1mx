
int MasterModule_fn3(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  int in_r9;
  int iVar3;
  uint uVar4;
  undefined1 auStack_e8 [8];
  undefined1 auStack_e0 [4];
  int *piStack_dc;
  undefined1 auStack_d0 [4];
  uint uStack_cc;
  undefined4 uStack_bc;
  uint uStack_b8;
  int iStack_b0;
  int iStack_ac;
  undefined4 uStack_a8;
  undefined4 uStack_a4;
  int iStack_a0;
  int iStack_9c;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  int iStack_80;
  int iStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined1 auStack_70 [4];
  int iStack_6c;
  undefined1 auStack_68 [4];
  undefined4 uStack_64;
  int iStack_50;
  undefined4 uStack_4c;
  undefined1 *puStack_48;
  undefined1 *puStack_44;
  undefined1 *puStack_40;
  undefined1 *puStack_3c;
  int iStack_34;
  int iStack_30;
  int iStack_2c;
  uint uStack_28;
  undefined4 uStack_24;
  int *piStack_20;
  int *piStack_1c;
  int iStack_18;
  int *piStack_8;
  
  puStack_3c = &stack0xffffff00;
  iStack_50 = in_r9 + 0x710c;
  puStack_48 = auStack_e8;
  puStack_44 = &LAB_0010a014;
  uStack_4c = 0xe98648;
  puStack_40 = (undefined1 *)register0x00000004;
  iStack_34 = param_1;
  iStack_30 = param_2;
  FUN_003d1214(auStack_68);
  iStack_2c = 0;
  if (iStack_30 == 0xc) {
    uStack_28 = 0;
    do {
      uStack_64 = 0xffffffff;
      uStack_24 = FUN_0005e890();
      FUN_005ea3bc(auStack_d0,*(undefined4 *)(uStack_28 * 4 + 0xe11980));
      uStack_64 = 2;
      FUN_005e817c(auStack_e0,uStack_24,auStack_d0);
      uStack_90 = uRam00661980;
      uStack_8c = uRam00661984;
      iStack_80 = iStack_34;
      if (iStack_34 == 0) {
        iStack_7c = iStack_34;
      }
      else {
        FUN_0039ac74(&iStack_7c,&uStack_90,8);
      }
      uStack_74 = 0x61fedc;
      iStack_ac = iStack_7c;
      iStack_9c = iStack_7c;
      iStack_b0 = iStack_80;
      uStack_a8 = uStack_78;
      uStack_a4 = 0x61fedc;
      iStack_a0 = iStack_80;
      uStack_98 = uStack_78;
      uStack_94 = 0x61fedc;
      iVar3 = -1;
      if (piStack_dc != (int *)0x0) {
        piStack_20 = piStack_dc;
        iVar1 = -1;
        if (piStack_dc[7] != 0) {
          uStack_64 = 1;
          iVar1 = FUN_001d9204(piStack_dc[7],0xffffffff);
        }
        iVar3 = -1;
        if (iVar1 == 0) {
          uVar4 = 0;
          piStack_1c = piStack_20 + 0x15;
          if (piStack_20[0x16] != 0) {
            uVar4 = piStack_20[0x17] - piStack_20[0x16] >> 4;
          }
          uVar2 = 0;
          if (piStack_20[0x16] != 0) {
            uVar2 = piStack_20[0x18] - piStack_20[0x16] >> 4;
          }
          if (uVar4 < uVar2) {
            iStack_18 = piStack_20[0x17];
            FUN_005f1618(iStack_18,1,&iStack_b0,piStack_1c,auStack_70);
            piStack_1c[2] = iStack_18 + 0x10;
          }
          else {
            iStack_6c = piStack_20[0x17];
            uStack_64 = 1;
            FUN_005f1804(piStack_1c,&iStack_6c,1,&iStack_b0);
          }
          if (piStack_20[7] == 0) {
            iVar3 = 0;
          }
          else {
            uStack_64 = 1;
            FUN_001d92bc();
            iVar3 = 0;
          }
        }
      }
      iStack_2c = iVar3;
      if (piStack_dc != (int *)0x0) {
        piStack_8 = piStack_dc;
        iVar3 = -1;
        if (piStack_dc[3] != 0) {
          uStack_64 = 2;
          iVar3 = FUN_001d9204(piStack_dc[3],0xffffffff);
        }
        if ((iVar3 == 0) && (*piStack_8 = *piStack_8 + -1, piStack_8[3] != 0)) {
          uStack_64 = 2;
          FUN_001d92bc();
        }
      }
      if (0xf < uStack_b8) {
        FUN_00245c34(uStack_cc);
      }
      uStack_b8 = 0xf;
      uStack_cc = uStack_cc & 0xffffff;
      uStack_bc = 0;
      if (iStack_2c != 0) {
        uStack_64 = 0xffffffff;
        FUN_0005e784(0,3,0x1f,0xd49df8,0x661968,0x168,0xd3f734,0x661974);
      }
      uStack_28 = uStack_28 + 1;
    } while (uStack_28 < 0x75);
  }
  FUN_003d12b8(auStack_68);
  return iStack_2c;
}

