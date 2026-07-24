/* 0x00087154  FUN_00087154  size=1000 bytes */


void FUN_00087154(int param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  
  iVar10 = *(int *)(param_1 + 0xb4) * *(int *)(param_1 + 0xb8);
  iVar6 = param_1 + 0xe8;
  puVar1 = (undefined4 *)FUN_00398e40();
  FUN_0039995c(*puVar1,0xd41964);
  puVar1 = (undefined4 *)FUN_00398e40();
  uVar2 = FUN_00086100(param_1,iVar6,0x400);
  iVar7 = param_1 + 0x10e8;
  uVar3 = FUN_00086100(param_1,iVar7,0x400);
  iVar8 = param_1 + 0x20e8;
  uVar4 = FUN_00086100(param_1,iVar8,0x400);
  iVar9 = param_1 + 0x30e8;
  uVar5 = FUN_00086100(param_1,iVar9,0x400);
  FUN_0039995c(*puVar1,0xd41984,uVar2,uVar3,uVar4,uVar5);
  puVar1 = (undefined4 *)FUN_00398e40();
  uVar2 = FUN_0008612c(param_1,iVar6,iVar10,0x400);
  uVar3 = FUN_0008612c(param_1,iVar7,iVar10,0x400);
  uVar4 = FUN_0008612c(param_1,iVar8,iVar10,0x400);
  uVar5 = FUN_0008612c(param_1,iVar9,iVar10,0x400);
  FUN_0039995c(*puVar1,0xd419a4,uVar2,uVar3,uVar4,uVar5);
  uVar2 = FUN_0008616c(param_1,iVar6,0x400);
  uVar3 = FUN_0008616c(param_1,iVar7,0x400);
  uVar4 = FUN_0008616c(param_1,iVar8,0x400);
  uVar11 = FUN_00373dd0(uVar2);
  uVar11 = FUN_0037336c((int)((ulonglong)uVar11 >> 0x20),(int)uVar11,0x40500000,0);
  uVar11 = FUN_00373704((int)((ulonglong)uVar11 >> 0x20),(int)uVar11,&MMIO_40590000,0);
  uVar11 = FUN_003739c0((int)((ulonglong)uVar11 >> 0x20),(int)uVar11,0x408b6000,0);
  uVar12 = FUN_00373dd0(uVar3);
  uVar12 = FUN_0037336c((int)((ulonglong)uVar12 >> 0x20),(int)uVar12,0x40500000,0);
  uVar12 = FUN_00373704((int)((ulonglong)uVar12 >> 0x20),(int)uVar12,&MMIO_40590000,0);
  uVar12 = FUN_003739c0((int)((ulonglong)uVar12 >> 0x20),(int)uVar12,0x408b6000,0);
  uVar13 = FUN_00373dd0(uVar4);
  uVar13 = FUN_0037336c((int)((ulonglong)uVar13 >> 0x20),(int)uVar13,0x40500000,0);
  uVar13 = FUN_00373704((int)((ulonglong)uVar13 >> 0x20),(int)uVar13,&MMIO_40590000,0);
  uVar13 = FUN_003739c0((int)((ulonglong)uVar13 >> 0x20),(int)uVar13,0x408b6000,0);
  puVar1 = (undefined4 *)FUN_00398e40();
  uVar5 = FUN_0008616c(param_1,iVar9,0x400);
  FUN_0039995c(*puVar1,0xd419c4,uVar2,uVar3,uVar4,uVar5,(int)((ulonglong)uVar11 >> 0x20),(int)uVar11
               ,uVar12,uVar13,0xd41a04);
  puVar1 = (undefined4 *)FUN_00398e40();
  uVar2 = FUN_000861b0(param_1,iVar6,0x400);
  uVar3 = FUN_000861b0(param_1,iVar7,0x400);
  uVar4 = FUN_000861b0(param_1,iVar8,0x400);
  uVar5 = FUN_000861b0(param_1,iVar9,0x400);
  FUN_0039995c(*puVar1,0xd41a0c,uVar2,uVar3,uVar4,uVar5);
  puVar1 = (undefined4 *)FUN_00398e40();
  uVar2 = FUN_000860bc(param_1,iVar6,0x400);
  uVar3 = FUN_000860bc(param_1,iVar7,0x400);
  uVar4 = FUN_000860bc(param_1,iVar8,0x400);
  uVar5 = FUN_000860bc(param_1,iVar9,0x400);
  FUN_0039995c(*puVar1,0xd41a2c,uVar2,uVar3,uVar4,uVar5);
  return;
}

