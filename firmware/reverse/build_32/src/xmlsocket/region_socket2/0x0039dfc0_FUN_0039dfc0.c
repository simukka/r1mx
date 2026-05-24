/* 0x0039dfc0  FUN_0039dfc0  size=84 bytes */


void FUN_0039dfc0(int param_1,int param_2)

{
  int *piVar1;
  
  if (param_2 != 0) {
    piVar1 = (int *)(param_1 + -4);
    do {
      piVar1 = piVar1 + 1;
      if (*piVar1 != 0) {
        FUN_003bcf98();
      }
      param_2 = param_2 + -1;
    } while (param_2 != 0);
  }
  return;
}

