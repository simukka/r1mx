
int MasterModule_fn1(int param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  int iVar5;
  int in_r9;
  undefined1 auStack_e8 [8];
  undefined1 auStack_e0 [4];
  int *piStack_dc;
  undefined1 auStack_d0 [4];
  uint uStack_cc;
  undefined4 uStack_bc;
  uint uStack_b8;
  undefined1 auStack_b0 [4];
  undefined4 uStack_ac;
  int iStack_98;
  undefined4 uStack_94;
  undefined1 *puStack_90;
  undefined4 uStack_8c;
  undefined1 *puStack_88;
  undefined1 *puStack_84;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  int iStack_74;
  int iStack_70;
  uint uStack_6c;
  int iStack_68;
  undefined4 uStack_64;
  int *piStack_54;
  undefined4 uStack_50;
  int *piStack_44;
  int iStack_40;
  int iStack_3c;
  undefined4 uStack_38;
  int iStack_34;
  int iStack_30;
  int iStack_2c;
  uint uStack_28;
  uint uStack_24;
  int iStack_20;
  int iStack_1c;
  int iStack_18;
  int *piStack_14;
  undefined4 uStack_10;
  int *piStack_4;
  
  puStack_84 = &stack0xffffff00;
  iStack_98 = in_r9 + 0x710c;
  puStack_90 = auStack_e8;
  uStack_94 = 0xe985fc;
  uStack_8c = 0x107668;
  puStack_88 = (undefined1 *)register0x00000004;
  iStack_74 = param_1;
  FUN_003d1214(auStack_b0);
  uStack_ac = 0xffffffff;
  uStack_7c = 1;
  uStack_78 = 1;
  FUN_001d9a58(500);
  iVar2 = FUN_0039b0f0(0x6617a4);
  FUN_000f6334(iStack_74,0,0x6617a4,iVar2 + 1,0);
  iVar2 = FUN_0039b0f0(0x661804);
  FUN_000f6334(iStack_74,0,0x661804,iVar2 + 1,0);
  uStack_64 = FUN_0005e890();
  FUN_005ea3bc(auStack_d0,0xd3f2dc);
  uStack_ac = 8;
  iStack_70 = 0;
  FUN_005e817c(auStack_e0,uStack_64,auStack_d0);
  uStack_ac = 7;
  FUN_005e8a40(auStack_e0,&uStack_7c,0xffffffff);
  if (piStack_dc != (int *)0x0) {
    piStack_54 = piStack_dc;
    iVar2 = -1;
    if (piStack_dc[3] != 0) {
      uStack_ac = 8;
      iVar2 = FUN_001d9204(piStack_dc[3],0xffffffff);
    }
    if (iVar2 == 0) {
      *piStack_54 = *piStack_54 + -1;
      if (piStack_54[3] != 0) {
        uStack_ac = 8;
        FUN_001d92bc();
      }
    }
  }
  if (0xf < uStack_b8) {
    FUN_00245c34(uStack_cc);
  }
  uStack_b8 = 0xf;
  uStack_cc = uStack_cc & 0xffffff;
  uStack_ac = 0xffffffff;
  uStack_bc = 0;
  uStack_50 = FUN_0005e890();
  FUN_005ea3bc(auStack_d0,0xd458e8);
  uStack_ac = 6;
  FUN_005e817c(auStack_e0,uStack_50,auStack_d0);
  uStack_ac = 5;
  FUN_005e8a40(auStack_e0,&uStack_7c,0xffffffff);
  if (piStack_dc != (int *)0x0) {
    piStack_44 = piStack_dc;
    iVar2 = -1;
    if (piStack_dc[3] != 0) {
      uStack_ac = 6;
      iVar2 = FUN_001d9204(piStack_dc[3],0xffffffff);
    }
    if (iVar2 == 0) {
      *piStack_44 = *piStack_44 + -1;
      if (piStack_44[3] != 0) {
        uStack_ac = 6;
        FUN_001d92bc();
      }
    }
  }
  if (0xf < uStack_b8) {
    FUN_00245c34(uStack_cc);
  }
  uStack_b8 = 0xf;
  uStack_cc = uStack_cc & 0xffffff;
  uStack_bc = 0;
  iVar2 = iStack_74 + 0x28;
  if (0xf < *(uint *)(iStack_74 + 0x3c)) {
    iVar2 = *(int *)(iStack_74 + 0x28);
  }
  uStack_ac = 0xffffffff;
  FUN_0005e784(2,3,0x1f,0xd49df8,0x6616b0,0x30e,0xd49f60,iVar2);
  uStack_6c = 0;
  do {
    iStack_40 = iStack_74 + 0x44;
    iStack_3c = -1;
    if (*(int *)(iStack_74 + 0x58) != -1) {
      iStack_3c = *(int *)(iStack_74 + 0x58);
    }
    if (iStack_3c != 0) {
      iVar2 = iStack_74 + 0x48;
      if (0xf < *(uint *)(iStack_74 + 0x5c)) {
        iVar2 = *(int *)(iStack_74 + 0x48);
      }
      iVar5 = iStack_74 + 0x48;
      if (0xf < *(uint *)(iStack_74 + 0x5c)) {
        iVar5 = *(int *)(iStack_74 + 0x48);
      }
      uStack_ac = 0xffffffff;
      FUN_0039acb0(iVar2,iVar5 + iStack_3c,*(int *)(iStack_74 + 0x58) - iStack_3c);
      iVar5 = iStack_40 + 4;
      iVar2 = *(int *)(iStack_40 + 0x14) - iStack_3c;
      if (0xf < *(uint *)(iStack_40 + 0x18)) {
        iVar5 = *(int *)(iStack_40 + 4);
      }
      *(int *)(iStack_40 + 0x14) = iVar2;
      *(undefined1 *)(iVar5 + iVar2) = 0;
    }
    uStack_ac = 0xffffffff;
    uStack_38 = FUN_0005e890();
    FUN_005ea3bc(auStack_d0,*(undefined4 *)(uStack_6c * 4 + 0xe11980));
    uStack_ac = 4;
    iStack_34 = FUN_00248640(8);
    uStack_ac = 3;
    FUN_005e817c(iStack_34,uStack_38,auStack_d0);
    iStack_68 = iStack_34;
    if (0xf < uStack_b8) {
      FUN_00245c34(uStack_cc);
    }
    uStack_b8 = 0xf;
    uStack_cc = uStack_cc & 0xffffff;
    uStack_bc = 0;
    if (iStack_68 != 0) {
      iVar5 = *(int *)(iStack_68 + 4);
      iVar2 = -1;
      if ((iVar5 != 0) && (*(code **)(iVar5 + 0x4c) != reset_vector)) {
        uStack_ac = 0xffffffff;
        iVar2 = (**(code **)(iVar5 + 0x4c))
                          (iVar5 + 0x28,*(undefined4 *)(iVar5 + 0x48),iStack_74 + 0x44);
      }
      iStack_70 = iVar2;
      if (iVar2 == 0) {
        if (*(int *)(iStack_74 + 0x58) == 0) {
          uStack_ac = 0xffffffff;
          puVar4 = (undefined4 *)FUN_00398e40();
          FUN_0039995c(*puVar4,0xd45e8c);
        }
        else {
          iStack_30 = *(int *)(iStack_68 + 4);
          iStack_2c = iStack_30 + 0x28;
          uStack_28 = *(uint *)(iStack_30 + 0x3c);
          uStack_24 = FUN_0039b0f0(uRam00d95114);
          uVar3 = 0;
          if (uStack_28 != 0) {
            iVar2 = iStack_30 + 0x2c;
            if (0xf < *(uint *)(iStack_2c + 0x18)) {
              iVar2 = *(int *)(iStack_2c + 4);
            }
            uVar3 = uStack_24;
            if (uStack_28 < uStack_24) {
              uVar3 = uStack_28;
            }
            uVar3 = FUN_0039ac2c(iVar2,uRam00d95114,uVar3);
          }
          if ((uVar3 == 0) && (uVar3 = (uint)(uStack_28 != uStack_24), uStack_28 < uStack_24)) {
            uVar3 = 0xffffffff;
          }
          if (uVar3 != 0) {
            iVar2 = iStack_74 + 0x48;
            if (0xf < *(uint *)(iStack_74 + 0x5c)) {
              iVar2 = *(int *)(iStack_74 + 0x48);
            }
            uStack_ac = 0xffffffff;
            FUN_000f6334(iStack_74,0,iVar2,*(undefined4 *)(iStack_74 + 0x58),0);
          }
          uStack_ac = 0xffffffff;
          FUN_001d9a58(100);
        }
      }
      else {
        uStack_ac = 0xffffffff;
        FUN_0005e784(0,3,0x1f,0xd49df8,0x6616b0,0x31a,0xd3f734,0x6616c0);
      }
      iStack_20 = iStack_74 + 0x44;
      iStack_1c = -1;
      if (*(int *)(iStack_74 + 0x58) != -1) {
        iStack_1c = *(int *)(iStack_74 + 0x58);
      }
      if (iStack_1c != 0) {
        iVar2 = iStack_74 + 0x48;
        if (0xf < *(uint *)(iStack_74 + 0x5c)) {
          iVar2 = *(int *)(iStack_74 + 0x48);
        }
        iVar5 = iStack_74 + 0x48;
        if (0xf < *(uint *)(iStack_74 + 0x5c)) {
          iVar5 = *(int *)(iStack_74 + 0x48);
        }
        uStack_ac = 0xffffffff;
        FUN_0039acb0(iVar2,iVar5 + iStack_1c,*(int *)(iStack_74 + 0x58) - iStack_1c);
        iVar5 = iStack_20 + 4;
        iVar2 = *(int *)(iStack_20 + 0x14) - iStack_1c;
        if (0xf < *(uint *)(iStack_20 + 0x18)) {
          iVar5 = *(int *)(iStack_20 + 4);
        }
        *(int *)(iStack_20 + 0x14) = iVar2;
        *(undefined1 *)(iVar5 + iVar2) = 0;
      }
      iStack_18 = iStack_68;
      if (iStack_68 != 0) {
        piVar1 = *(int **)(iStack_68 + 4);
        if (piVar1 != (int *)0x0) {
          iVar2 = -1;
          piStack_14 = piVar1;
          if (piVar1[3] != 0) {
            uStack_ac = 0xffffffff;
            iVar2 = FUN_001d9204(piVar1[3],0xffffffff);
          }
          if (iVar2 == 0) {
            *piStack_14 = *piStack_14 + -1;
            if (piStack_14[3] != 0) {
              uStack_ac = 0xffffffff;
              FUN_001d92bc();
            }
          }
        }
        FUN_00245c34(iStack_18);
      }
    }
    uStack_6c = uStack_6c + 1;
  } while (uStack_6c < 0x75);
  uStack_ac = 0xffffffff;
  FUN_001d9a58(500);
  iVar2 = FUN_0039b0f0(0x6616d0);
  FUN_000f6334(iStack_74,0,0x6616d0,iVar2 + 1,0);
  iVar2 = FUN_0039b0f0(0x661718);
  FUN_000f6334(iStack_74,0,0x661718,iVar2 + 1,0);
  iVar2 = FUN_0039b0f0(0x661760);
  FUN_000f6334(iStack_74,0,0x661760,iVar2 + 1,0);
  uStack_10 = FUN_0005e890();
  FUN_005ea3bc(auStack_d0,0xd3ebc8);
  uStack_ac = 2;
  FUN_005e817c(auStack_e0,uStack_10,auStack_d0);
  uStack_ac = 1;
  FUN_005e8a40(auStack_e0,&uStack_78,0xffffffff);
  if (piStack_dc != (int *)0x0) {
    piStack_4 = piStack_dc;
    iVar2 = -1;
    if (piStack_dc[3] != 0) {
      uStack_ac = 2;
      iVar2 = FUN_001d9204(piStack_dc[3],0xffffffff);
    }
    if (iVar2 == 0) {
      *piStack_4 = *piStack_4 + -1;
      if (piStack_4[3] != 0) {
        uStack_ac = 2;
        FUN_001d92bc();
      }
    }
  }
  if (0xf < uStack_b8) {
    FUN_00245c34(uStack_cc);
  }
  uStack_b8 = 0xf;
  uStack_cc = uStack_cc & 0xffffff;
  uStack_bc = 0;
  iVar2 = iStack_74 + 0x28;
  if (0xf < *(uint *)(iStack_74 + 0x3c)) {
    iVar2 = *(int *)(iStack_74 + 0x28);
  }
  uStack_ac = 0xffffffff;
  FUN_0005e784(2,3,0x1f,0xd49df8,0x6616b0,0x340,0xd49f88,iVar2);
  FUN_003d12b8(auStack_b0);
  return iStack_70;
}

