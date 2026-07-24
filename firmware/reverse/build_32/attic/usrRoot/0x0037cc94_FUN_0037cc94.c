/* 0x0037cc94  FUN_0037cc94  size=504B */


int FUN_0037cc94(undefined4 param_1,int param_2,int *param_3)

{
  code *pcVar1;
  int iVar2;
  int *piVar3;
  undefined4 *puVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int aiStack_20 [2];
  
  iVar6 = 0;
  iVar2 = 0x501;
  if (*(int *)(param_2 + 4) != 0) {
    if (*(int *)(param_2 + 4) == 1) {
      piVar3 = *(int **)(param_2 + 8);
    }
    else {
      piVar3 = *(int **)(param_2 + 8);
      iVar6 = piVar3[1];
    }
    iVar8 = *(int *)(param_2 + 0xc);
    iVar7 = *piVar3;
    iVar2 = FUN_0037c964(iVar8);
    if (iVar2 == 0) {
      if ((*(int *)(param_2 + 0x18) == 0) || (*(int *)(param_2 + 0x18) == 4)) {
        *(undefined4 *)(param_2 + 0x18) = 6;
      }
      if (iVar8 == 0) {
        piVar3 = (int *)FUN_0037daac();
        iVar2 = 0x50b;
        if (piVar3 != (int *)0x0) {
          uVar5 = *(uint *)(param_2 + 0x18);
          iVar2 = 0x501;
          if ((uVar5 & 0x10) == 0) {
            piVar3[7] = 0x40000000;
            piVar3[9] = uVar5;
            iVar2 = *(int *)(param_2 + 0x24);
            piVar3[10] = *(int *)(param_2 + 0x20);
            piVar3[0xb] = iVar2;
            piVar3[7] = 0x40800000;
            if ((uVar5 & 4) != 0) {
              piVar3[9] = uVar5 & 0xfffffffb | 8;
            }
            iVar8 = FUN_0037dbd4(0,iVar7,aiStack_20);
            iVar2 = 0x502;
            if (iVar8 == 0) {
              *piVar3 = (int)piRam00e9c5c0;
              piRam00e9c5c0 = piVar3;
              piVar3[6] = -1;
              iVar2 = *piVar3;
              piVar3[5] = 0;
              piVar3[8] = iVar6;
              piVar3[1] = 0xe9c5c0;
              *param_3 = piVar3[2];
              piVar3[3] = iVar7;
              piVar3[4] = aiStack_20[0];
              *(int **)(iVar2 + 4) = piVar3;
              return 0;
            }
          }
        }
      }
      else {
        puVar4 = *(undefined4 **)(iVar8 * 4 + 0x108e678);
        iVar2 = 0x514;
        if (puVar4 != (undefined4 *)0x0) {
          pcVar1 = (code *)*puVar4;
          iVar2 = 0x50d;
          if ((pcVar1 != reset_vector) &&
             (iVar2 = (*pcVar1)(param_2 + 0xc,param_2 + 0x18,iVar7,iVar6,0,param_3), iVar2 == 0)) {
            return 0;
          }
        }
      }
    }
  }
  return iVar2;
}

