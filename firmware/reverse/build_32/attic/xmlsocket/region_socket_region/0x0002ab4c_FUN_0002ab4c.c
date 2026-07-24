/* 0x0002ab4c  FUN_0002ab4c  size=460 bytes */


uint FUN_0002ab4c(int param_1,uint param_2,undefined8 *param_3,int *param_4,uint *param_5,
                 int *param_6,uint *param_7)

{
  uint uVar1;
  int extraout_r4;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined8 uVar6;
  
  uVar3 = *(uint *)(*(int *)(param_1 + 0x10) + 0x60);
  iVar4 = *(int *)(param_1 + 0x18);
  uVar5 = *(uint *)(param_1 + 0x1c);
  iVar2 = ((int)param_2 >> 0x1f) + iVar4 + (uint)CARRY4(param_2,uVar5);
  if ((*(int *)(param_1 + 0x20) < iVar2) ||
     ((*(int *)(param_1 + 0x20) == iVar2 && (*(uint *)(param_1 + 0x24) < param_2 + uVar5)))) {
    param_2 = *(int *)(param_1 + 0x24) - uVar5;
  }
  uVar1 = 0;
  if (0 < (int)param_2) {
    uVar6 = FUN_003cca2c(iVar4,uVar5,0,uVar3);
    *param_3 = uVar6;
    FUN_003cd848(iVar4,uVar5,0,uVar3);
    *param_4 = extraout_r4;
    if (*param_4 == 0) {
      *param_5 = 0;
      uVar5 = *param_5;
    }
    else {
      *param_5 = uVar3 - *param_4;
      uVar5 = *param_5;
    }
    if (uVar5 <= param_2) {
      uVar5 = *param_5;
      *param_6 = 0;
      for (uVar5 = param_2 - uVar5; uVar3 <= uVar5; uVar5 = uVar5 - uVar3) {
        *param_6 = *param_6 + 1;
      }
      *param_7 = uVar5;
      return param_2;
    }
    *param_5 = param_2;
    *param_6 = 0;
    *param_7 = 0;
    uVar1 = param_2;
  }
  return uVar1;
}

