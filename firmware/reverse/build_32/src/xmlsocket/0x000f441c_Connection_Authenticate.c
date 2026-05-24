
undefined4 Connection_Authenticate(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int in_r9;
  uint uVar4;
  undefined1 auStack_168 [8];
  undefined4 uStack_160;
  int iStack_15c;
  undefined1 auStack_150 [32];
  int iStack_130;
  int iStack_12c;
  undefined4 uStack_128;
  undefined4 uStack_124;
  int iStack_120;
  int iStack_11c;
  undefined4 uStack_118;
  undefined4 uStack_114;
  undefined4 uStack_110;
  int iStack_10c;
  int iStack_100;
  int iStack_fc;
  undefined4 uStack_f8;
  undefined4 uStack_f4;
  undefined1 auStack_f0 [4];
  undefined4 uStack_ec;
  undefined1 auStack_e8 [4];
  undefined4 uStack_e4;
  int iStack_d0;
  undefined4 uStack_cc;
  undefined1 *puStack_c8;
  undefined4 uStack_c4;
  undefined1 *puStack_c0;
  undefined1 *puStack_bc;
  int iStack_b4;
  int iStack_b0;
  int iStack_ac;
  undefined4 uStack_a8;
  int iStack_a4;
  int iStack_a0;
  int iStack_9c;
  undefined4 uStack_94;
  int iStack_90;
  int iStack_8c;
  int iStack_88;
  undefined4 uStack_84;
  int iStack_80;
  int iStack_7c;
  int iStack_78;
  undefined4 uStack_74;
  int iStack_70;
  int iStack_6c;
  int iStack_68;
  undefined4 uStack_64;
  int iStack_60;
  int iStack_5c;
  int iStack_58;
  undefined4 uStack_54;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  undefined4 uStack_44;
  int iStack_40;
  int iStack_3c;
  int iStack_38;
  undefined4 uStack_34;
  int iStack_30;
  int iStack_2c;
  int iStack_28;
  undefined4 uStack_24;
  int iStack_20;
  int iStack_1c;
  int iStack_18;
  char *pcStack_14;
  int iStack_10;
  int iStack_c;
  
  puStack_bc = &stack0xfffffe80;
  iStack_d0 = in_r9 + 0x710c;
  puStack_c8 = auStack_168;
  uStack_cc = 0xe9850a;
  uStack_c4 = 0x105674;
  puStack_c0 = (undefined1 *)register0x00000004;
  iStack_b4 = param_1;
  iStack_b0 = param_2;
  FUN_003d1214(auStack_e8);
  if (iStack_b0 == 0xc) {
    uStack_e4 = 0xffffffff;
    uStack_a8 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd48b78);
    uStack_e4 = 0x12;
    FUN_005e817c(&uStack_160,uStack_a8,auStack_150);
    uStack_110 = uRam0066121c;
    iStack_10c = iRam00661220;
    iStack_100 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_fc = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_fc,&uStack_110,8);
    }
    uStack_f4 = 0x61fdac;
    iStack_12c = iStack_fc;
    iStack_11c = iStack_fc;
    iStack_130 = iStack_100;
    uStack_128 = uStack_f8;
    uStack_124 = 0x61fdac;
    iStack_120 = iStack_100;
    uStack_118 = uStack_f8;
    uStack_114 = 0x61fdac;
    iStack_ac = -1;
    if (iStack_15c != 0) {
      iStack_a4 = iStack_15c;
      iVar3 = -1;
      if (*(int *)(iStack_15c + 0x1c) != 0) {
        uStack_e4 = 0x11;
        iVar3 = FUN_001d9204(*(int *)(iStack_15c + 0x1c),0xffffffff);
      }
      iStack_ac = -1;
      if (iVar3 == 0) {
        uVar4 = 0;
        iStack_a0 = iStack_a4 + 0x54;
        if (*(int *)(iStack_a4 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_a4 + 0x5c) - *(int *)(iStack_a4 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_a4 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_a4 + 0x60) - *(int *)(iStack_a4 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_9c = *(int *)(iStack_a4 + 0x5c);
          FUN_005f1618(iStack_9c,1,&iStack_130,iStack_a0,auStack_f0);
          *(int *)(iStack_a0 + 8) = iStack_9c + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_a4 + 0x5c);
          uStack_e4 = 0x11;
          FUN_005f1804(iStack_a0,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_a4 + 0x1c) == 0) {
          iStack_ac = 0;
        }
        else {
          uStack_e4 = 0x11;
          FUN_001d92bc();
          iStack_ac = 0;
        }
      }
    }
    uStack_e4 = 0x12;
    FUN_005e7ed0(&uStack_160);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x11b,0xd3d54c,0x661210);
    }
    uStack_e4 = 0xffffffff;
    uStack_94 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd48be4);
    uStack_e4 = 0x10;
    FUN_005e817c(&uStack_110,uStack_94,auStack_150);
    uStack_160 = uRam00661224;
    iStack_15c = uRam00661228;
    iStack_120 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_11c = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_11c,&uStack_160,8);
    }
    uStack_114 = 0x61fdac;
    iStack_12c = iStack_11c;
    iStack_fc = iStack_11c;
    iStack_130 = iStack_120;
    uStack_128 = uStack_118;
    uStack_124 = 0x61fdac;
    iStack_100 = iStack_120;
    uStack_f8 = uStack_118;
    uStack_f4 = 0x61fdac;
    iVar3 = -1;
    if (iStack_10c != 0) {
      iStack_90 = iStack_10c;
      iVar2 = -1;
      if (*(int *)(iStack_10c + 0x1c) != 0) {
        uStack_e4 = 0xf;
        iVar2 = FUN_001d9204(*(int *)(iStack_10c + 0x1c),0xffffffff);
      }
      iVar3 = -1;
      if (iVar2 == 0) {
        uVar4 = 0;
        iStack_8c = iStack_90 + 0x54;
        if (*(int *)(iStack_90 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_90 + 0x5c) - *(int *)(iStack_90 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_90 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_90 + 0x60) - *(int *)(iStack_90 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_88 = *(int *)(iStack_90 + 0x5c);
          FUN_005f1618(iStack_88,1,&iStack_130,iStack_8c,auStack_f0);
          *(int *)(iStack_8c + 8) = iStack_88 + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_90 + 0x5c);
          uStack_e4 = 0xf;
          FUN_005f1804(iStack_8c,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_90 + 0x1c) == 0) {
          iVar3 = 0;
        }
        else {
          uStack_e4 = 0xf;
          FUN_001d92bc();
          iVar3 = 0;
        }
      }
    }
    uStack_e4 = 0x10;
    iStack_ac = iVar3;
    FUN_005e7ed0(&uStack_110);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x122,0xd3d54c,0x661210);
    }
    uStack_e4 = 0xffffffff;
    uStack_84 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd48b94);
    uStack_e4 = 0xe;
    FUN_005e817c(&uStack_110,uStack_84,auStack_150);
    uStack_160 = uRam0066122c;
    iStack_15c = uRam00661230;
    iStack_120 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_11c = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_11c,&uStack_160,8);
    }
    uStack_114 = 0x61fdac;
    iStack_12c = iStack_11c;
    iStack_fc = iStack_11c;
    iStack_130 = iStack_120;
    uStack_128 = uStack_118;
    uStack_124 = 0x61fdac;
    iStack_100 = iStack_120;
    uStack_f8 = uStack_118;
    uStack_f4 = 0x61fdac;
    iVar3 = -1;
    if (iStack_10c != 0) {
      iStack_80 = iStack_10c;
      iVar2 = -1;
      if (*(int *)(iStack_10c + 0x1c) != 0) {
        uStack_e4 = 0xd;
        iVar2 = FUN_001d9204(*(int *)(iStack_10c + 0x1c),0xffffffff);
      }
      iVar3 = -1;
      if (iVar2 == 0) {
        uVar4 = 0;
        iStack_7c = iStack_80 + 0x54;
        if (*(int *)(iStack_80 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_80 + 0x5c) - *(int *)(iStack_80 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_80 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_80 + 0x60) - *(int *)(iStack_80 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_78 = *(int *)(iStack_80 + 0x5c);
          FUN_005f1618(iStack_78,1,&iStack_130,iStack_7c,auStack_f0);
          *(int *)(iStack_7c + 8) = iStack_78 + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_80 + 0x5c);
          uStack_e4 = 0xd;
          FUN_005f1804(iStack_7c,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_80 + 0x1c) == 0) {
          iVar3 = 0;
        }
        else {
          uStack_e4 = 0xd;
          FUN_001d92bc();
          iVar3 = 0;
        }
      }
    }
    uStack_e4 = 0xe;
    iStack_ac = iVar3;
    FUN_005e7ed0(&uStack_110);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x129,0xd3d54c,0x661210);
    }
    uStack_e4 = 0xffffffff;
    uStack_74 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd48bb8);
    uStack_e4 = 0xc;
    FUN_005e817c(&uStack_110,uStack_74,auStack_150);
    uStack_160 = uRam00661234;
    iStack_15c = uRam00661238;
    iStack_120 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_11c = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_11c,&uStack_160,8);
    }
    uStack_114 = 0x61fdac;
    iStack_12c = iStack_11c;
    iStack_fc = iStack_11c;
    iStack_130 = iStack_120;
    uStack_128 = uStack_118;
    uStack_124 = 0x61fdac;
    iStack_100 = iStack_120;
    uStack_f8 = uStack_118;
    uStack_f4 = 0x61fdac;
    iVar3 = -1;
    if (iStack_10c != 0) {
      iStack_70 = iStack_10c;
      iVar2 = -1;
      if (*(int *)(iStack_10c + 0x1c) != 0) {
        uStack_e4 = 0xb;
        iVar2 = FUN_001d9204(*(int *)(iStack_10c + 0x1c),0xffffffff);
      }
      iVar3 = -1;
      if (iVar2 == 0) {
        uVar4 = 0;
        iStack_6c = iStack_70 + 0x54;
        if (*(int *)(iStack_70 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_70 + 0x5c) - *(int *)(iStack_70 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_70 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_70 + 0x60) - *(int *)(iStack_70 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_68 = *(int *)(iStack_70 + 0x5c);
          FUN_005f1618(iStack_68,1,&iStack_130,iStack_6c,auStack_f0);
          *(int *)(iStack_6c + 8) = iStack_68 + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_70 + 0x5c);
          uStack_e4 = 0xb;
          FUN_005f1804(iStack_6c,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_70 + 0x1c) == 0) {
          iVar3 = 0;
        }
        else {
          uStack_e4 = 0xb;
          FUN_001d92bc();
          iVar3 = 0;
        }
      }
    }
    uStack_e4 = 0xc;
    iStack_ac = iVar3;
    FUN_005e7ed0(&uStack_110);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x130,0xd3d54c,0x661210);
    }
    uStack_e4 = 0xffffffff;
    uStack_64 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd3b6bc);
    uStack_e4 = 10;
    FUN_005e817c(&uStack_110,uStack_64,auStack_150);
    uStack_160 = uRam0066123c;
    iStack_15c = uRam00661240;
    iStack_120 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_11c = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_11c,&uStack_160,8);
    }
    uStack_114 = 0x61fdac;
    iStack_12c = iStack_11c;
    iStack_fc = iStack_11c;
    iStack_130 = iStack_120;
    uStack_128 = uStack_118;
    uStack_124 = 0x61fdac;
    iStack_100 = iStack_120;
    uStack_f8 = uStack_118;
    uStack_f4 = 0x61fdac;
    iVar3 = -1;
    if (iStack_10c != 0) {
      iStack_60 = iStack_10c;
      iVar2 = -1;
      if (*(int *)(iStack_10c + 0x1c) != 0) {
        uStack_e4 = 9;
        iVar2 = FUN_001d9204(*(int *)(iStack_10c + 0x1c),0xffffffff);
      }
      iVar3 = -1;
      if (iVar2 == 0) {
        uVar4 = 0;
        iStack_5c = iStack_60 + 0x54;
        if (*(int *)(iStack_60 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_60 + 0x5c) - *(int *)(iStack_60 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_60 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_60 + 0x60) - *(int *)(iStack_60 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_58 = *(int *)(iStack_60 + 0x5c);
          FUN_005f1618(iStack_58,1,&iStack_130,iStack_5c,auStack_f0);
          *(int *)(iStack_5c + 8) = iStack_58 + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_60 + 0x5c);
          uStack_e4 = 9;
          FUN_005f1804(iStack_5c,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_60 + 0x1c) != 0) {
          uStack_e4 = 9;
          FUN_001d92bc();
        }
        iVar3 = 0;
      }
    }
    uStack_e4 = 10;
    iStack_ac = iVar3;
    FUN_005e7ed0(&uStack_110);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x137,0xd3d54c,0x661210);
    }
    uStack_e4 = 0xffffffff;
    uStack_54 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd3b6ec);
    uStack_e4 = 8;
    FUN_005e817c(&uStack_110,uStack_54,auStack_150);
    uStack_160 = uRam00661244;
    iStack_15c = uRam00661248;
    iStack_120 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_11c = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_11c,&uStack_160,8);
    }
    uStack_114 = 0x61fdac;
    iStack_12c = iStack_11c;
    iStack_fc = iStack_11c;
    iStack_130 = iStack_120;
    uStack_128 = uStack_118;
    uStack_124 = 0x61fdac;
    iStack_100 = iStack_120;
    uStack_f8 = uStack_118;
    uStack_f4 = 0x61fdac;
    iVar3 = -1;
    if (iStack_10c != 0) {
      iStack_50 = iStack_10c;
      iVar2 = -1;
      if (*(int *)(iStack_10c + 0x1c) != 0) {
        uStack_e4 = 7;
        iVar2 = FUN_001d9204(*(int *)(iStack_10c + 0x1c),0xffffffff);
      }
      iVar3 = -1;
      if (iVar2 == 0) {
        uVar4 = 0;
        iStack_4c = iStack_50 + 0x54;
        if (*(int *)(iStack_50 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_50 + 0x5c) - *(int *)(iStack_50 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_50 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_50 + 0x60) - *(int *)(iStack_50 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_48 = *(int *)(iStack_50 + 0x5c);
          FUN_005f1618(iStack_48,1,&iStack_130,iStack_4c,auStack_f0);
          *(int *)(iStack_4c + 8) = iStack_48 + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_50 + 0x5c);
          uStack_e4 = 7;
          FUN_005f1804(iStack_4c,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_50 + 0x1c) != 0) {
          uStack_e4 = 7;
          FUN_001d92bc();
        }
        iVar3 = 0;
      }
    }
    uStack_e4 = 8;
    iStack_ac = iVar3;
    FUN_005e7ed0(&uStack_110);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x13e,0xd3d54c,0x661210);
    }
    uStack_e4 = 0xffffffff;
    FUN_000f038c(iStack_b4);
    uStack_44 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd48ee4);
    uStack_e4 = 6;
    FUN_005e817c(&uStack_110,uStack_44,auStack_150);
    uStack_160 = uRam0066124c;
    iStack_15c = uRam00661250;
    iStack_120 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_11c = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_11c,&uStack_160,8);
    }
    uStack_114 = 0x61fdac;
    iStack_12c = iStack_11c;
    iStack_fc = iStack_11c;
    iStack_130 = iStack_120;
    uStack_128 = uStack_118;
    uStack_124 = 0x61fdac;
    iStack_100 = iStack_120;
    uStack_f8 = uStack_118;
    uStack_f4 = 0x61fdac;
    iVar3 = -1;
    if (iStack_10c != 0) {
      iStack_40 = iStack_10c;
      iVar2 = -1;
      if (*(int *)(iStack_10c + 0x1c) != 0) {
        uStack_e4 = 5;
        iVar2 = FUN_001d9204(*(int *)(iStack_10c + 0x1c),0xffffffff);
      }
      iVar3 = -1;
      if (iVar2 == 0) {
        uVar4 = 0;
        iStack_3c = iStack_40 + 0x54;
        if (*(int *)(iStack_40 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_40 + 0x5c) - *(int *)(iStack_40 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_40 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_40 + 0x60) - *(int *)(iStack_40 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_38 = *(int *)(iStack_40 + 0x5c);
          FUN_005f1618(iStack_38,1,&iStack_130,iStack_3c,auStack_f0);
          *(int *)(iStack_3c + 8) = iStack_38 + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_40 + 0x5c);
          uStack_e4 = 5;
          FUN_005f1804(iStack_3c,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_40 + 0x1c) != 0) {
          uStack_e4 = 5;
          FUN_001d92bc();
        }
        iVar3 = 0;
      }
    }
    uStack_e4 = 6;
    iStack_ac = iVar3;
    FUN_005e7ed0(&uStack_110);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x147,0xd3d54c,0x661210);
    }
    uStack_e4 = 0xffffffff;
    FUN_000f0c5c(iStack_b4);
    uStack_34 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd41e40);
    uStack_e4 = 4;
    FUN_005e817c(&uStack_110,uStack_34,auStack_150);
    uStack_160 = uRam00661254;
    iStack_15c = uRam00661258;
    iStack_120 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_11c = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_11c,&uStack_160,8);
    }
    uStack_114 = 0x61fdac;
    iStack_12c = iStack_11c;
    iStack_fc = iStack_11c;
    iStack_130 = iStack_120;
    uStack_128 = uStack_118;
    uStack_124 = 0x61fdac;
    iStack_100 = iStack_120;
    uStack_f8 = uStack_118;
    uStack_f4 = 0x61fdac;
    iVar3 = -1;
    if (iStack_10c != 0) {
      iStack_30 = iStack_10c;
      iVar2 = -1;
      if (*(int *)(iStack_10c + 0x1c) != 0) {
        uStack_e4 = 3;
        iVar2 = FUN_001d9204(*(int *)(iStack_10c + 0x1c),0xffffffff);
      }
      iVar3 = -1;
      if (iVar2 == 0) {
        uVar4 = 0;
        iStack_2c = iStack_30 + 0x54;
        if (*(int *)(iStack_30 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_30 + 0x5c) - *(int *)(iStack_30 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_30 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_30 + 0x60) - *(int *)(iStack_30 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_28 = *(int *)(iStack_30 + 0x5c);
          FUN_005f1618(iStack_28,1,&iStack_130,iStack_2c,auStack_f0);
          *(int *)(iStack_2c + 8) = iStack_28 + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_30 + 0x5c);
          uStack_e4 = 3;
          FUN_005f1804(iStack_2c,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_30 + 0x1c) != 0) {
          uStack_e4 = 3;
          FUN_001d92bc();
        }
        iVar3 = 0;
      }
    }
    uStack_e4 = 4;
    iStack_ac = iVar3;
    FUN_005e7ed0(&uStack_110);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x150,0xd3d54c,0x661210);
    }
    uStack_e4 = 0xffffffff;
    uStack_24 = FUN_0005e890();
    FUN_005ea3bc(auStack_150,0xd49404);
    uStack_e4 = 2;
    FUN_005e817c(&uStack_110,uStack_24,auStack_150);
    uStack_160 = uRam0066125c;
    iStack_15c = iRam00661260;
    iStack_120 = iStack_b4;
    if (iStack_b4 == 0) {
      iStack_11c = iStack_b4;
    }
    else {
      FUN_0039ac74(&iStack_11c,&uStack_160,8);
    }
    uStack_114 = 0x61fdac;
    iStack_12c = iStack_11c;
    iStack_fc = iStack_11c;
    iStack_130 = iStack_120;
    uStack_128 = uStack_118;
    uStack_124 = 0x61fdac;
    iStack_100 = iStack_120;
    uStack_f8 = uStack_118;
    uStack_f4 = 0x61fdac;
    iVar3 = -1;
    if (iStack_10c != 0) {
      iStack_20 = iStack_10c;
      iVar2 = -1;
      if (*(int *)(iStack_10c + 0x1c) != 0) {
        uStack_e4 = 1;
        iVar2 = FUN_001d9204(*(int *)(iStack_10c + 0x1c),0xffffffff);
      }
      iVar3 = -1;
      if (iVar2 == 0) {
        uVar4 = 0;
        iStack_1c = iStack_20 + 0x54;
        if (*(int *)(iStack_20 + 0x58) != 0) {
          uVar4 = *(int *)(iStack_20 + 0x5c) - *(int *)(iStack_20 + 0x58) >> 4;
        }
        uVar1 = 0;
        if (*(int *)(iStack_20 + 0x58) != 0) {
          uVar1 = *(int *)(iStack_20 + 0x60) - *(int *)(iStack_20 + 0x58) >> 4;
        }
        if (uVar4 < uVar1) {
          iStack_18 = *(int *)(iStack_20 + 0x5c);
          FUN_005f1618(iStack_18,1,&iStack_130,iStack_1c,auStack_f0);
          *(int *)(iStack_1c + 8) = iStack_18 + 0x10;
        }
        else {
          uStack_ec = *(undefined4 *)(iStack_20 + 0x5c);
          uStack_e4 = 1;
          FUN_005f1804(iStack_1c,&uStack_ec,1,&iStack_130);
        }
        if (*(int *)(iStack_20 + 0x1c) != 0) {
          uStack_e4 = 1;
          FUN_001d92bc();
        }
        iVar3 = 0;
      }
    }
    uStack_e4 = 2;
    iStack_ac = iVar3;
    FUN_005e7ed0(&uStack_110);
    FUN_005e75e4(auStack_150,1,0);
    if (iStack_ac != 0) {
      uStack_e4 = 0xffffffff;
      FUN_0005e784(0,3,0xe,0xd48700,0x661210,0x158,0xd3d54c,0x661210);
    }
  }
  else if (iStack_b0 == 0x10) {
    pcStack_14 = *(char **)(iStack_b4 + 0x31a0);
    if (pcStack_14 != (char *)0x0) {
      if (((*(int *)(pcStack_14 + 4) != 0) && (*(int *)(pcStack_14 + 0x10) != 0)) &&
         (*pcStack_14 != '\0')) {
        uStack_e4 = 0xffffffff;
        iVar3 = FUN_001da174();
        *pcStack_14 = '\x01' - (iVar3 == 0);
      }
      iStack_10 = *(int *)(iStack_b4 + 0x31a0);
      uStack_110 = uRam00661058;
      iStack_10c = iRam0066105c;
      iStack_c = *(int *)(iStack_10 + 0xc);
      if (iStack_c != 0) {
        FUN_005e75e4(iStack_c + 0x10,1,0);
        FUN_00245c34(iStack_c);
      }
      *(undefined4 *)(iStack_10 + 0xc) = 0;
      if (iStack_10 != 0) {
        uStack_e4 = 0xffffffff;
        FUN_001d9fb8(*(undefined4 *)(iStack_10 + 4));
        FUN_00245c34(iStack_10);
      }
    }
    uStack_e4 = 0xffffffff;
    FUN_001cd39c(0);
    FUN_003d12b8(auStack_e8);
    return 0;
  }
  FUN_003d12b8(auStack_e8);
  return 0;
}

