/* 0x0002bc4c  FUN_0002bc4c  size=968 bytes */


undefined4 FUN_0002bc4c(int *param_1,undefined4 param_2,uint param_3,uint param_4)

{
  uint uVar1;
  uint extraout_r4;
  int extraout_r4_00;
  int extraout_r4_01;
  int extraout_r4_02;
  int extraout_r4_03;
  uint extraout_r4_04;
  uint *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  
  uVar5 = *(undefined4 *)param_1[1];
  uVar6 = ((undefined4 *)param_1[1])[1];
  param_1[4] = 0;
  param_1[5] = 0;
  uVar4 = 0xffffffff;
  if (((param_1[2] == param_3) && (param_1[3] == param_4)) && (param_1[6] != 0)) {
    return 0;
  }
  if ((*(byte *)(param_1[1] + 0x42) & 0x10) == 0) {
    puVar2 = (uint *)param_1[1];
    if ((int)*puVar2 < (int)param_3) goto LAB_0002be90;
LAB_0002bcd4:
    if ((*puVar2 == param_3) && (puVar2[1] < param_4)) goto LAB_0002be90;
  }
  else {
    puVar3 = (undefined4 *)param_1[1];
    *puVar3 = 0x7fffffff;
    puVar3[1] = 0xffffffff;
    puVar2 = (uint *)param_1[1];
    if ((int)param_3 <= (int)*puVar2) goto LAB_0002bcd4;
LAB_0002be90:
    param_1[4] = param_3;
    param_1[5] = param_4;
    if (param_1[6] != 0) {
      return 0;
    }
    param_3 = param_1[2];
    param_4 = param_1[3];
  }
  if (((param_1[6] != 0) && (param_1[2] != 0 || param_1[3] != 0)) && (param_1[9] == 0)) {
    param_1[9] = 1;
    param_1[6] = param_1[6] + -1;
    uVar1 = param_1[9] << (*(byte *)(*param_1 + 0x84) & 0x3f);
    param_1[2] = param_1[2] - (uint)((uint)param_1[3] < uVar1);
    param_1[3] = param_1[3] - uVar1;
  }
  iVar7 = *(int *)param_1[1];
  uVar8 = ((int *)param_1[1])[1];
  uVar1 = (uint)(iVar7 != 0 || uVar8 != 0);
  uVar9 = uVar8 - uVar1;
  uVar1 = iVar7 - (uint)(uVar8 < uVar1);
  if (((int)param_3 < (int)uVar1) || ((uVar1 == param_3 && (param_4 < uVar9)))) {
    uVar1 = param_3;
    uVar9 = param_4;
  }
  if (param_1[6] == 0) {
    FUN_003cc82c(uVar1,uVar9,*(undefined1 *)(*param_1 + 0x84));
    iVar7 = -1;
    uVar8 = extraout_r4;
LAB_0002bdb8:
    iVar7 = (**(code **)(*(int *)(*param_1 + 0x30) + 0xc))(param_1,iVar7,uVar8);
    if (iVar7 == -1) goto LAB_0002be24;
  }
  else if (((int)uVar1 < param_1[2]) || ((param_1[2] == uVar1 && (uVar9 < (uint)param_1[3])))) {
    FUN_003cc82c(uVar1,uVar9,*(undefined1 *)(*param_1 + 0x84));
    FUN_003cc82c(param_1[2],param_1[3],*(undefined1 *)(*param_1 + 0x84));
    uVar8 = extraout_r4_03 - extraout_r4_02;
    if (((uint)param_1[6] < uVar8) || (param_1[6] - uVar8 < (uint)param_1[7])) {
      FUN_003cc82c(uVar1,uVar9,*(undefined1 *)(*param_1 + 0x84));
      iVar7 = -1;
      param_1[8] = 0;
      uVar8 = extraout_r4_04;
      goto LAB_0002bdb8;
    }
    param_1[9] = param_1[9] + uVar8;
    param_1[6] = param_1[6] - uVar8;
  }
  else {
    FUN_003cc82c(param_1[2],param_1[3],*(undefined1 *)(*param_1 + 0x84));
    FUN_003cc82c(uVar1,uVar9,*(undefined1 *)(*param_1 + 0x84));
    uVar8 = extraout_r4_01 - extraout_r4_00;
    if ((uint)param_1[9] <= uVar8) {
      iVar7 = param_1[6];
      goto LAB_0002bdb8;
    }
    param_1[9] = param_1[9] - uVar8;
    param_1[6] = param_1[6] + uVar8;
  }
  param_1[2] = param_3;
  uVar4 = 0;
  param_1[3] = param_4;
  if (((uVar1 != param_3) || (uVar9 != param_4)) &&
     (uVar1 = *(ushort *)(*param_1 + 0x5c) - 1,
     ((int)uVar1 >> 0x1f & param_3) == 0 && (uVar1 & param_4) == 0)) {
    param_1[9] = param_1[9] + -1;
    param_1[6] = param_1[6] + 1;
  }
LAB_0002be24:
  puVar3 = (undefined4 *)param_1[1];
  *puVar3 = uVar5;
  puVar3[1] = uVar6;
  return uVar4;
}

