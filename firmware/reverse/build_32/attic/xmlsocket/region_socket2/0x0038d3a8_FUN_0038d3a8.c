/* 0x0038d3a8  FUN_0038d3a8  size=380 bytes */


void FUN_0038d3a8(int param_1,int param_2,uint param_3,uint param_4,uint param_5)

{
  uint uVar1;
  int iVar2;
  int *piVar3;
  uint *puVar4;
  uint *puVar5;
  uint *puVar6;
  uint *puVar7;
  uint uVar8;
  
  puVar6 = (uint *)(param_1 + 0x18);
  puVar7 = (uint *)(param_1 + 8);
  piVar3 = (int *)(param_1 + 0x28);
  *(int *)(param_1 + 0x34) = param_1 + 0x2c;
  *(int *)(param_1 + 0x14) = param_1 + 0xc;
  *(int *)(param_1 + 0x24) = param_1 + 0x1c;
  *(undefined4 *)(param_1 + 0x40) = 0;
  *(undefined4 *)(param_1 + 0x50) = 0;
  *(uint **)(param_1 + 0x10) = puVar7;
  *(uint **)(param_1 + 0x20) = puVar6;
  *(int **)(param_1 + 0x30) = piVar3;
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(undefined4 *)(param_1 + 0x1c) = 0;
  *(undefined4 *)(param_1 + 0x2c) = 0;
  *(undefined4 *)(param_1 + 8) = 0;
  *(undefined4 *)(param_1 + 0x18) = 0;
  *(undefined4 *)(param_1 + 0x28) = 0;
  *(undefined4 *)(param_1 + 0x4c) = 0;
  if (param_3 != 0) {
    *(undefined4 *)(param_1 + 0x3c) = 0x20;
    *(uint *)(param_1 + 0x48) = param_5;
    iVar2 = 0x7fffffff;
    if ((param_2 < 0) || (iVar2 = param_2, param_2 != 0)) {
      uVar1 = param_3 + iVar2;
      *(uint *)(param_1 + 0x44) = uVar1;
    }
    else {
      *(undefined4 *)(param_1 + 0x44) = 0;
      iVar2 = FUN_0039b0f0(param_3);
      puVar7 = *(uint **)(param_1 + 0x10);
      uVar1 = param_3 + iVar2;
      puVar6 = *(uint **)(param_1 + 0x20);
      piVar3 = *(int **)(param_1 + 0x30);
      *(uint *)(param_1 + 0x44) = uVar1;
    }
    if (param_4 == 0) {
      *piVar3 = uVar1 - param_3;
    }
    else {
      uVar8 = param_3;
      if ((param_3 <= param_4) && (uVar8 = param_4, uVar1 < param_4)) {
        uVar8 = uVar1;
      }
      puVar5 = *(uint **)(param_1 + 0x14);
      puVar4 = *(uint **)(param_1 + 0x24);
      **(int **)(param_1 + 0x34) = uVar1 - uVar8;
      *puVar5 = uVar8;
      *piVar3 = uVar8 - param_3;
      *puVar4 = uVar8;
    }
    *puVar7 = param_3;
    *puVar6 = param_3;
    return;
  }
  *(undefined4 *)(param_1 + 0x44) = 0;
  *(uint *)(param_1 + 0x48) = param_5 | 4;
  if (param_2 < 0x21) {
    *(undefined4 *)(param_1 + 0x3c) = 0x20;
    return;
  }
  *(int *)(param_1 + 0x3c) = param_2;
  return;
}

