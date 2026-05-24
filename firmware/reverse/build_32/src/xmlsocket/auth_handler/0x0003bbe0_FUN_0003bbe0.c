/* 0x0003bbe0  FUN_0003bbe0  size=5536 bytes */


undefined4 FUN_0003bbe0(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined4 uVar7;
  uint uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  byte in_cr0;
  byte in_cr1;
  byte unaff_cr2;
  byte unaff_cr3;
  byte unaff_cr4;
  byte in_cr5;
  byte in_cr6;
  byte in_cr7;
  undefined8 uVar14;
  undefined8 uVar15;
  undefined8 uVar16;
  undefined8 uVar17;
  int iStack_120;
  int iStack_11c;
  uint uStack_118;
  int iStack_f0;
  int iStack_ec;
  undefined4 uStack_e8;
  int iStack_e4;
  int iStack_e0;
  int iStack_dc;
  int iStack_c8;
  int iStack_c4;
  int iStack_c0;
  int iStack_bc;
  int iStack_b8;
  undefined4 uStack_a8;
  undefined4 uStack_a4;
  undefined2 uStack_90;
  short sStack_8e;
  int iStack_80;
  undefined8 uStack_78;
  undefined8 uStack_70;
  undefined8 uStack_68;
  undefined8 uStack_60;
  uint uStack_4c;
  
  uStack_4c = (uint)(in_cr0 & 0xf) << 0x1c | (uint)(in_cr1 & 0xf) << 0x18 |
              (uint)(unaff_cr2 & 0xf) << 0x14 | (uint)(unaff_cr3 & 0xf) << 0x10 |
              (uint)(unaff_cr4 & 0xf) << 0xc | (uint)(in_cr5 & 0xf) << 8 | (uint)(in_cr6 & 0xf) << 4
              | (uint)(in_cr7 & 0xf);
  iVar1 = FUN_0044f4cc(0xd39684,2,0);
  if (iVar1 == -1) {
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65cda4,0x493,0xd3a47c,0xd39684);
  }
  else {
    iVar2 = FUN_0044e510(iVar1,0x5656000c,&iStack_120);
    if (iVar2 != 0) {
      FUN_0005e784(2,3,0xc,0xd38d1c,0x65cda4,0x499,0xd3a460);
      FUN_0044f9fc(iVar1);
      return 0xffffffff;
    }
    iStack_80 = FUN_0044e510(iVar1,0x5656000d,0);
    FUN_0044f9fc(iVar1);
    iVar1 = FUN_0044f4cc(0xd3968c,2,0);
    uVar9 = 0x4191b3dc;
    uVar10 = 0x40000000;
    if (-1 < iVar1) {
      uStack_90 = 0x4d;
      sStack_8e = 0;
      FUN_0044e510(iVar1,0x73790008,&uStack_90);
      if (sStack_8e == 0xb) {
        puVar3 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar3,0xd3a448);
      }
      else {
        if (sStack_8e != 0xc) {
          puVar3 = (undefined4 *)FUN_00398e40();
          FUN_0039995c(*puVar3,0xd3a408,sStack_8e);
          return 0xffffffff;
        }
        puVar3 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar3,0xd39694);
        uVar9 = 0x4191af55;
        uVar10 = 0x40b40b41;
      }
      FUN_0044f9fc(iVar1);
      uVar6 = uStack_118;
      uVar14 = FUN_00373dd0(uStack_118);
      if ((int)uVar6 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uStack_78 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      iVar1 = iStack_120;
      uVar14 = FUN_00373dd0(iStack_120);
      uVar13 = (undefined4)((ulonglong)uVar14 >> 0x20);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370(uVar13,(int)uVar14,0x41f00000,0);
        uStack_70 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
        iVar1 = iStack_11c;
        uVar14 = FUN_00373dd0(iStack_11c);
      }
      else {
        uStack_70 = FUN_003739c0(uVar13,(int)uVar14,uVar9,uVar10);
        iVar1 = iStack_11c;
        uVar14 = FUN_00373dd0(iStack_11c);
      }
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uStack_68 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      iVar1 = FUN_0021fc44();
      iVar1 = iVar1 + 1;
      if (cRam00e149b4 == '\a') {
        iVar2 = FUN_0021fcbc();
        iVar4 = FUN_0021ff7c();
        iVar5 = FUN_0021ff04();
        uVar14 = FUN_00373dd0(iVar2);
      }
      else {
        iVar2 = FUN_0021fcbc();
        iVar2 = iVar2 + 3;
        iVar4 = FUN_0021ff7c();
        iVar5 = FUN_0021ff04();
        uVar14 = FUN_00373dd0(iVar2);
      }
      if (iVar2 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x3e65798e,0xe2308c3a);
      uVar13 = (undefined4)((ulonglong)uVar14 >> 0x20);
      uVar12 = (undefined4)uVar14;
      uVar8 = (iVar4 - iVar5) + 1;
      uVar6 = FUN_0021fe8c();
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar13,uVar12);
      uVar15 = FUN_00373dd0(uVar8 + uVar8 / uVar6);
      uVar16 = FUN_00373704((int)((ulonglong)uVar15 >> 0x20),(int)uVar15,uVar13,uVar12);
      uVar7 = (undefined4)((ulonglong)uVar16 >> 0x20);
      uVar15 = uStack_78;
      if (uVar6 != 0) {
        uVar15 = FUN_00373dd0(iVar1);
        if (iVar1 < 0) {
          uVar15 = FUN_00373370((int)((ulonglong)uVar15 >> 0x20),(int)uVar15,0x41f00000,0);
        }
        uVar17 = FUN_00373704((int)((ulonglong)uVar15 >> 0x20),(int)uVar15,uVar13,uVar12);
        uVar15 = FUN_00373dd0(uVar6);
        if ((int)uVar6 < 0) {
          uVar15 = FUN_00373370((int)((ulonglong)uVar15 >> 0x20),(int)uVar15,0x41f00000,0);
        }
        uVar15 = FUN_003739c0((int)((ulonglong)uVar17 >> 0x20),(int)uVar17,
                              (int)((ulonglong)uVar15 >> 0x20),(int)uVar15);
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,
                              (int)((ulonglong)uVar15 >> 0x20),(int)uVar15);
        uVar15 = uStack_78;
      }
      uStack_78._0_4_ = (undefined4)((ulonglong)uVar15 >> 0x20);
      uStack_78._4_4_ = (undefined4)uVar15;
      uStack_60 = FUN_0037336c(uStack_78._0_4_,uStack_78._4_4_,uVar7,(int)uVar16);
      uStack_78 = uVar15;
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd396b4);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar11 = *puVar3;
      uVar15 = FUN_00373704(uStack_78._0_4_,uStack_78._4_4_,0x408f4000,0);
      uVar17 = FUN_003739c0(0x3ff00000,0,uStack_78._0_4_,uStack_78._4_4_);
      FUN_0039995c(uVar11,0xd396cc,(int)((ulonglong)uVar15 >> 0x20),(int)uVar15,
                   (int)((ulonglong)uVar17 >> 0x20),(int)uVar17,uStack_118);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar11 = 0xd3970c;
      if (iStack_80 == 0) {
        uVar11 = 0xd39714;
      }
      FUN_0039995c(*puVar3,0xd3971c,uVar11);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar11 = *puVar3;
      uVar15 = FUN_00373704(uStack_70._0_4_,uStack_70._4_4_,0x408f4000,0);
      FUN_0039995c(uVar11,0xd39744,(int)((ulonglong)uVar15 >> 0x20),(int)uVar15,iStack_120);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar11 = *puVar3;
      uVar15 = FUN_00373704(uStack_68._0_4_,uStack_68._4_4_,0x408f4000,0);
      FUN_0039995c(uVar11,0xd3977c,(int)((ulonglong)uVar15 >> 0x20),(int)uVar15,iStack_11c);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar11 = *puVar3;
      uVar15 = FUN_00373704(uVar7,(int)uVar16,0x408f4000,0);
      uVar16 = FUN_00373704(uVar13,uVar12,0x412e8480,0);
      uVar13 = (undefined4)((ulonglong)uVar16 >> 0x20);
      FUN_0039995c(uVar11,0xd397b4,(int)((ulonglong)uVar15 >> 0x20),(int)uVar15,uVar8,uVar8 / uVar6,
                   uVar13,(int)uVar16);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar12 = *puVar3;
      uVar15 = FUN_00373704(uStack_60._0_4_,uStack_60._4_4_,0x408f4000,0);
      FUN_0039995c(uVar12,0xd39808,(int)((ulonglong)uVar15 >> 0x20),(int)uVar15);
      if (cRam00e149b4 == '\a') {
        puVar3 = (undefined4 *)FUN_00398e40();
        uVar12 = *puVar3;
      }
      else {
        puVar3 = (undefined4 *)FUN_00398e40();
        uVar12 = *puVar3;
        iVar2 = iVar2 + -3;
      }
      FUN_0039995c(uVar12,0xd39834,uVar13,(int)uVar16,iVar2);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd3986c,iVar1);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd3988c,uVar6);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd398ac,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(uStack_a8);
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd398d8,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uStack_a8);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(uStack_a4);
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39910,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uStack_a4);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd37ae4);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd39948);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_f0);
      if (iStack_f0 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd3996c,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_e4);
      if (iStack_e4 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd399a8,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_e0);
      if (iStack_e0 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd399e4,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_dc);
      if (iStack_dc < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x412e8480,0);
      FUN_0039995c(uVar13,0xd39a20,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_ec);
      if (iStack_ec < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd39a5c,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd39a98,uStack_e8);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd37ae4);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd39ac4);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_c8);
      if (iStack_c8 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd39ae8,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14,iStack_c8);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_c4);
      if (iStack_c4 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd39b28,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14,iStack_c4);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_c0);
      if (iStack_c0 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd39b68,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_bc);
      if (iStack_bc < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd39ba4,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iStack_b8);
      if (iStack_b8 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_0039995c(uVar13,0xd39be0,(int)((ulonglong)uVar14 >> 0x20),(int)uVar14);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd37ae4);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd39c1c);
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = FUN_001cf390();
      FUN_0039995c(*puVar3,0xd39c48,uVar13);
      iVar1 = FUN_001cf3fc();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39c94,iVar1);
      iVar1 = FUN_001cf468();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39cec,iVar1);
      iVar1 = FUN_001cf4d4();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39d44,iVar1);
      iVar1 = FUN_001cf540();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39d9c,iVar1);
      iVar1 = FUN_001cf5ac();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39df4,iVar1);
      iVar1 = FUN_001cf618();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39e4c,iVar1);
      iVar1 = FUN_001cf684();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39ea4,iVar1);
      iVar1 = FUN_001cf6f0();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39efc,iVar1);
      iVar1 = FUN_001cf75c();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39f54,iVar1);
      iVar1 = FUN_001cf7c8();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd39fac,iVar1);
      iVar1 = FUN_001cf834();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd3a004,iVar1);
      iVar1 = FUN_001cf8a0();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd3a05c,iVar1);
      iVar1 = FUN_001cf90c();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd3a0b4,iVar1);
      iVar1 = FUN_001cf978();
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd3a10c,iVar1);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd37ae4);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd3a164);
      iVar1 = FUN_001cf210();
      iVar1 = iVar1 * 0x350 + 0x109000;
      puVar3 = (undefined4 *)FUN_00398e40();
      uVar13 = *puVar3;
      uVar14 = FUN_00373dd0(iVar1);
      if (iVar1 < 0) {
        uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
      }
      uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
      FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
      FUN_0039995c(uVar13,0xd3a17c,iVar1);
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd37ae4);
      iVar1 = FUN_001ce888();
      if (iVar1 == 1) {
        puVar3 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar3,0xd3a35c);
        uVar6 = FUN_001ce7ec();
        puVar3 = (undefined4 *)FUN_00398e40();
        uVar13 = *puVar3;
        uVar14 = FUN_00373dd0(uVar6);
        if ((int)uVar6 < 0) {
          uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
        }
        uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
        FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
        if ((int)uStack_118 < 0) {
          uVar9 = FUN_0037517c(uStack_118 & 1 | uStack_118 >> 1);
          uVar9 = FUN_00374be8(uVar9,uVar9);
        }
        else {
          uVar9 = FUN_0037517c();
        }
        if ((int)uVar6 < 0) {
          uVar10 = FUN_0037517c(uVar6 & 1 | uVar6 >> 1);
          uVar10 = FUN_00374be8(uVar10,uVar10);
        }
        else {
          uVar10 = FUN_0037517c(uVar6);
        }
        FUN_00374f8c(uVar9,uVar10);
        FUN_00373e9c();
        FUN_0039995c(uVar13,0xd3a374,uVar6);
        uVar14 = uStack_78;
        uVar15 = uStack_70;
      }
      else {
        uVar6 = FUN_001ce83c();
        if (uVar6 == 0) {
          puVar3 = (undefined4 *)FUN_00398e40();
          FUN_0039995c(*puVar3,0xd3a1d4);
          uVar14 = uStack_78;
          uVar15 = uStack_70;
        }
        else {
          puVar3 = (undefined4 *)FUN_00398e40();
          uVar13 = 0xd58070;
          if (uVar6 < 2) {
            uVar13 = 0xd78e54;
          }
          FUN_0039995c(*puVar3,0xd3a298,uVar6,uVar13);
          uVar8 = FUN_001ce7ec();
          puVar3 = (undefined4 *)FUN_00398e40();
          uVar13 = *puVar3;
          uVar14 = FUN_00373dd0(uVar8);
          if ((int)uVar8 < 0) {
            uVar14 = FUN_00373370((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x41f00000,0);
          }
          uVar14 = FUN_00373704((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x408f4000,0);
          FUN_003739c0((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,uVar9,uVar10);
          if ((int)uVar8 < 0) {
            uVar9 = FUN_0037517c(uVar8 & 1 | uVar8 >> 1);
            uVar9 = FUN_00374be8(uVar9,uVar9);
          }
          else {
            uVar9 = FUN_0037517c(uVar8);
          }
          if ((int)uStack_118 < 0) {
            uVar10 = FUN_0037517c(uStack_118 & 1 | uStack_118 >> 1);
            uVar10 = FUN_00374be8(uVar10,uVar10);
          }
          else {
            uVar10 = FUN_0037517c();
          }
          if ((int)uVar6 < 0) {
            uVar12 = FUN_0037517c(uVar6 & 1 | uVar6 >> 1);
            uVar12 = FUN_00374be8(uVar12,uVar12);
          }
          else {
            uVar12 = FUN_0037517c(uVar6);
          }
          uVar10 = FUN_00374f8c(uVar10,uVar12);
          FUN_00374f8c(uVar9,uVar10);
          uVar14 = FUN_00373e9c();
          FUN_0037336c((int)((ulonglong)uVar14 >> 0x20),(int)uVar14,0x3ff00000,0);
          FUN_0039995c(uVar13,0xd3a2e4,uVar8);
          uVar14 = uStack_78;
          uVar15 = uStack_70;
        }
      }
      uStack_70._0_4_ = (undefined4)((ulonglong)uVar15 >> 0x20);
      uStack_70._4_4_ = (undefined4)uVar15;
      uStack_78._0_4_ = (undefined4)((ulonglong)uVar14 >> 0x20);
      uStack_78._4_4_ = (undefined4)uVar14;
      iVar1 = FUN_00377f2c(uStack_70._0_4_,uStack_70._4_4_,uStack_78._0_4_,uStack_78._4_4_);
      uStack_70 = uVar15;
      uStack_78 = uVar14;
      uVar14 = uStack_68;
      uVar15 = uStack_78;
      if (-1 < iVar1) {
        puVar3 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar3,0xd3a1e8);
        uVar14 = uStack_68;
        uVar15 = uStack_78;
      }
      uStack_78._0_4_ = (undefined4)((ulonglong)uVar15 >> 0x20);
      uStack_78._4_4_ = (undefined4)uVar15;
      uStack_68._0_4_ = (undefined4)((ulonglong)uVar14 >> 0x20);
      uStack_68._4_4_ = (undefined4)uVar14;
      iVar1 = FUN_00377f2c(uStack_68._0_4_,uStack_68._4_4_,uStack_78._0_4_,uStack_78._4_4_);
      uStack_78 = uVar15;
      uStack_68 = uVar14;
      uVar14 = uStack_68;
      uVar15 = uStack_70;
      if (-1 < iVar1) {
        puVar3 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar3,0xd3a224);
        uVar14 = uStack_68;
        uVar15 = uStack_70;
      }
      uStack_70._0_4_ = (undefined4)((ulonglong)uVar15 >> 0x20);
      uStack_70._4_4_ = (undefined4)uVar15;
      uStack_68._0_4_ = (undefined4)((ulonglong)uVar14 >> 0x20);
      uStack_68._4_4_ = (undefined4)uVar14;
      iVar1 = FUN_00377f2c(uStack_70._0_4_,uStack_70._4_4_,uStack_68._0_4_,uStack_68._4_4_);
      uStack_70 = uVar15;
      uStack_68 = uVar14;
      uVar14 = uStack_60;
      if (-1 < iVar1) {
        puVar3 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar3,0xd3a260);
        uVar14 = uStack_60;
      }
      uStack_60._0_4_ = (undefined4)((ulonglong)uVar14 >> 0x20);
      uStack_60._4_4_ = (undefined4)uVar14;
      iVar1 = FUN_00377f7c(uStack_60._0_4_,uStack_60._4_4_,0,0);
      uStack_60 = uVar14;
      if (iVar1 < 0) {
        puVar3 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar3,0xd3a3f0);
      }
      return 0;
    }
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65cda4,0x4a9,0xd3a498,0xd3968c);
  }
  return 0xffffffff;
}

