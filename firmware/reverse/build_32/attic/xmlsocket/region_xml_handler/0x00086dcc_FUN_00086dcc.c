/* 0x00086dcc  FUN_00086dcc  size=904 bytes */


void FUN_00086dcc(int param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  
  puVar1 = (undefined4 *)FUN_00398e40();
  FUN_0039995c(*puVar1,0xd417c0);
  iVar14 = param_1 + 0xe8;
  iVar10 = 0;
  iVar8 = 0;
  iVar9 = 0;
  iVar7 = 0;
  iVar5 = 0;
  iVar6 = 0;
  iVar11 = 0;
  do {
    while( true ) {
      iVar12 = iVar11 * 4;
      iVar13 = iVar12 + iVar14;
      iVar8 = iVar8 + *(int *)(iVar13 + 0x1000);
      iVar10 = iVar10 + *(int *)(iVar12 + iVar14);
      iVar9 = iVar9 + *(int *)(iVar13 + 0x2000);
      puVar1 = (undefined4 *)FUN_00398e40();
      iVar4 = iVar12 + param_1 + 0x68e8;
      FUN_0039995c(*puVar1,0xd41828,iVar11,*(undefined4 *)(iVar12 + iVar14),
                   *(undefined4 *)(iVar13 + 0x1000),*(undefined4 *)(iVar13 + 0x2000),
                   *(undefined4 *)(iVar13 + 0x3000),*(undefined4 *)(iVar12 + param_1 + 0x68e8),
                   *(undefined4 *)(iVar4 + 0x1000),*(undefined4 *)(iVar4 + 0x2000));
      iVar12 = iVar12 + param_1;
      if (iVar11 < 0x200) break;
      puVar1 = (undefined4 *)FUN_00398e40();
      iVar11 = iVar11 + 1;
      FUN_0039995c(*puVar1,0xd37ae4);
      if (0x3ff < iVar11) goto LAB_00086f24;
    }
    iVar7 = iVar7 + *(int *)(iVar12 + 0x50e8);
    iVar5 = iVar5 + *(int *)(iVar12 + 0x58e8);
    iVar6 = iVar6 + *(int *)(iVar12 + 0x60e8);
    puVar1 = (undefined4 *)FUN_00398e40();
    iVar11 = iVar11 + 1;
    FUN_0039995c(*puVar1,0xd4184c,*(undefined4 *)(iVar12 + 0x50e8),*(undefined4 *)(iVar12 + 0x58e8),
                 *(undefined4 *)(iVar12 + 0x60e8));
  } while (iVar11 < 0x400);
LAB_00086f24:
  puVar1 = (undefined4 *)FUN_00398e40();
  FUN_0039995c(*puVar1,0xd4185c,iVar10,iVar8,iVar9);
  puVar1 = (undefined4 *)FUN_00398e40();
  uVar2 = FUN_001d16fc();
  uVar3 = FUN_001d1678();
  iVar8 = FUN_001d16fc();
  iVar9 = FUN_001d1678();
  FUN_0039995c(*puVar1,0xd41878,uVar2,uVar3,iVar8 * iVar9);
  puVar1 = (undefined4 *)FUN_00398e40();
  FUN_0039995c(*puVar1,0xd418b4,iVar7,iVar5,iVar6);
  puVar1 = (undefined4 *)FUN_00398e40();
  uVar2 = FUN_00220f9c();
  uVar3 = FUN_0022109c();
  iVar5 = FUN_00220f9c();
  iVar6 = FUN_0022109c();
  FUN_0039995c(*puVar1,0xd418d0,uVar2,uVar3,iVar5 * iVar6);
  puVar1 = (undefined4 *)FUN_00398e40();
  iVar5 = param_1 + 0x10000;
  FUN_0039995c(*puVar1,0xd37ae4);
  iVar6 = *(int *)(param_1 + 0x15bf4);
  if (iVar6 < 0x200) {
    iVar6 = 0x200;
  }
  puVar1 = (undefined4 *)FUN_00398e40();
  iVar7 = 0;
  FUN_0039995c(*puVar1,0xd4190c);
  if (0 < iVar6) {
    do {
      while (*(int *)(param_1 + 0x15bf4) <= iVar7) {
        puVar1 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar1,0xd4194c);
        if (0x1ff < iVar7) goto LAB_000870e8;
LAB_00087078:
        puVar1 = (undefined4 *)FUN_00398e40();
        uVar3 = *puVar1;
        uVar2 = *(undefined4 *)(iVar5 + 0x5bfc);
        FUN_00373e9c(*(undefined4 *)(iVar5 + 0x5c00));
        iVar8 = iVar7 + 1;
        FUN_0039995c(uVar3,0xd41930,iVar7,uVar2,*(undefined4 *)(iVar5 + 0x5bf8));
        iVar5 = iVar5 + 0xc;
        iVar7 = iVar8;
        if (iVar6 <= iVar8) {
          return;
        }
      }
      puVar1 = (undefined4 *)FUN_00398e40();
      uVar3 = *puVar1;
      uVar2 = *(undefined4 *)(iVar5 + -0x408);
      FUN_00373e9c(*(undefined4 *)(iVar5 + -0x404));
      FUN_0039995c(uVar3,0xd4191c,iVar7,uVar2,*(undefined4 *)(iVar5 + -0x40c));
      if (iVar7 < 0x200) goto LAB_00087078;
LAB_000870e8:
      puVar1 = (undefined4 *)FUN_00398e40();
      iVar7 = iVar7 + 1;
      FUN_0039995c(*puVar1,0xd37ae4);
      iVar5 = iVar5 + 0xc;
    } while (iVar7 < iVar6);
  }
  return;
}

