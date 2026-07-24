/* 0x0004e638  FUN_0004e638  size=180 bytes */


void FUN_0004e638(undefined4 param_1,undefined4 *param_2,undefined4 *param_3,uint param_4,
                 uint param_5,int param_6)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  uint uVar8;
  
  iVar3 = ((int)param_5 >> 1) + (uint)((int)param_5 < 0 && (param_5 & 1) != 0);
  iVar2 = ((int)param_4 >> 1) + (uint)((int)param_4 < 0 && (param_4 & 1) != 0);
  iVar5 = iVar2 + iVar3;
  puVar7 = param_2 + (iVar2 - iVar3);
  if (0 < iVar5) {
    uVar8 = iVar5 + 1U >> 1;
    puVar4 = param_3;
    do {
      *puVar4 = *param_2;
      puVar1 = param_2 + 1;
      param_2 = param_2 + 2;
      puVar4[1] = *puVar1;
      puVar4[2] = *puVar7;
      puVar1 = puVar7 + 1;
      puVar7 = puVar7 + 2;
      puVar4[3] = *puVar1;
      puVar4 = puVar4 + 4;
      uVar8 = uVar8 - 1;
    } while (uVar8 != 0);
  }
  if ((param_6 != 0) && (0 < (int)(param_4 + param_5))) {
    uVar8 = param_4 + param_5 + 1 >> 1;
    iVar2 = 0;
    do {
      uVar6 = param_3[iVar2];
      param_3[iVar2] = param_3[iVar2 + 1];
      param_3[iVar2 + 1] = uVar6;
      uVar8 = uVar8 - 1;
      iVar2 = iVar2 + 2;
    } while (uVar8 != 0);
  }
  return;
}

