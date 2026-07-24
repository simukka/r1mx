/* 0x00034310  FUN_00034310  size=276 bytes */


int FUN_00034310(int param_1,undefined4 param_2,int param_3,int param_4)

{
  int *piVar1;
  int iVar2;
  int extraout_r4;
  
  if (*(int *)(param_1 + 0xd8) == 0) {
    piVar1 = *(int **)(param_1 + 0xc4);
    while (piVar1 != (int *)0x0) {
      if (piVar1[2] == param_3) {
        if (piVar1[3] == param_4) {
          return (int)piVar1;
        }
        piVar1 = (int *)*piVar1;
      }
      else {
        piVar1 = (int *)*piVar1;
      }
    }
    piVar1 = *(int **)(param_1 + 0xcc);
    while (piVar1 != (int *)0x0) {
      if (piVar1[2] == param_3) {
        if (piVar1[3] == param_4) {
          return (int)piVar1;
        }
        piVar1 = (int *)*piVar1;
      }
      else {
        piVar1 = (int *)*piVar1;
      }
    }
  }
  else {
    FUN_003cd848(param_3,param_4,0,*(undefined4 *)(param_1 + 0xd8));
    iVar2 = *(int *)(extraout_r4 * 4 + *(int *)(param_1 + 0xd4));
    while (iVar2 != 0) {
      if (*(int *)(iVar2 + 8) == param_3) {
        if (*(int *)(iVar2 + 0xc) == param_4) {
          return iVar2;
        }
        iVar2 = *(int *)(iVar2 + 0x14);
      }
      else {
        iVar2 = *(int *)(iVar2 + 0x14);
      }
    }
  }
  return 0;
}

