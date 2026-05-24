/* 0x000345d4  FUN_000345d4  size=180 bytes */


void FUN_000345d4(int param_1,undefined4 param_2,int param_3,uint param_4)

{
  int *piVar1;
  
  piVar1 = *(int **)(param_1 + 0xc4);
  while (piVar1 != (int *)0x0) {
    if ((piVar1[2] == -1) && (piVar1[3] == -1)) {
      piVar1 = (int *)*piVar1;
    }
    else {
      if ((param_3 <= piVar1[2]) && ((piVar1[2] != param_3 || (param_4 <= (uint)piVar1[3])))) {
        FUN_000344d4(param_1,piVar1);
      }
      piVar1 = (int *)*piVar1;
    }
  }
  return;
}

