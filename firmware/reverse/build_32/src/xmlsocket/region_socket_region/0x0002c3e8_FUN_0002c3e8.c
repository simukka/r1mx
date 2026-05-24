/* 0x0002c3e8  FUN_0002c3e8  size=664 bytes */


undefined4 FUN_0002c3e8(int *param_1,undefined4 param_2,int param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int *piVar7;
  undefined8 uVar8;
  ulonglong uVar9;
  ulonglong uVar10;
  
  iVar4 = *param_1;
  piVar7 = (int *)param_1[1];
  uVar1 = 0x380005;
  if ((*(byte *)((int)piVar7 + 0x42) & 0x10) != 0) {
LAB_0002c674:
    FUN_00442990(uVar1);
    return 0xffffffff;
  }
  if ((*piVar7 == param_3) && (piVar7[1] == param_4)) {
    return 0;
  }
  if ((param_1[0x10] & 2U) == 0) {
    uVar1 = 0x380011;
    goto LAB_0002c674;
  }
  uVar8 = FUN_0002b4cc(param_1,0xffffffff);
  if ((int)((ulonglong)uVar8 >> 0x20) == -1) {
    return 0xffffffff;
  }
  iVar5 = param_1[2];
  uVar6 = param_1[3];
  if ((param_3 < *piVar7) || ((*piVar7 == param_3 && (param_4 < (uint)piVar7[1])))) {
    if ((param_3 < iVar5) || ((iVar5 == param_3 && (param_4 < uVar6)))) {
      iVar5 = param_3;
      uVar6 = param_4;
    }
    iVar3 = param_4 - 1;
    iVar2 = param_3 + -1 + (uint)(param_4 != 0);
    if (param_3 == 0 && param_4 == 0) {
      iVar2 = 0;
      iVar3 = 0;
    }
    uVar9 = FUN_0002bc4c(param_1,(int)uVar8,iVar2,iVar3);
    if ((int)(uVar9 >> 0x20) != 0) goto LAB_0002c604;
    *piVar7 = param_3;
    piVar7[1] = param_4;
    uVar10 = (**(code **)(*(int *)(iVar4 + 0x2c) + 8))(param_1,6,0);
    uVar9 = uVar10 & 0xffffffff;
    if ((int)(uVar10 >> 0x20) != 0) goto LAB_0002c604;
    uVar9 = (**(code **)(*(int *)(iVar4 + 0x30) + 8))(param_1,param_1[6],1);
    uVar1 = (undefined4)uVar9;
    if ((int)(uVar9 >> 0x20) != 0) goto LAB_0002c604;
    param_1[4] = 0;
    param_1[5] = 0;
  }
  else {
    iVar2 = param_1[4];
    iVar3 = param_1[5];
    param_1[4] = param_3;
    param_1[5] = param_4;
    uVar9 = FUN_0002c014(param_1,0x80000000);
    if ((int)(uVar9 >> 0x20) != 0) {
      param_1[4] = iVar2;
      param_1[5] = iVar3;
      goto LAB_0002c604;
    }
    *piVar7 = param_3;
    piVar7[1] = param_4;
    uVar10 = (**(code **)(*(int *)(iVar4 + 0x2c) + 8))(param_1,6,0);
    uVar1 = (undefined4)uVar10;
    uVar9 = uVar10 & 0xffffffff;
    if ((int)(uVar10 >> 0x20) != 0) goto LAB_0002c604;
  }
  uVar9 = FUN_0002bc4c(param_1,uVar1,iVar5,uVar6);
  if ((int)(uVar9 >> 0x20) != -1) {
    FUN_0002b518(param_1);
    return 0;
  }
LAB_0002c604:
  FUN_0002bc4c(param_1,(int)uVar9,iVar5,uVar6);
  FUN_0002b518(param_1);
  return (int)(uVar9 >> 0x20);
}

