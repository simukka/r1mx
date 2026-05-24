/* 0x00086100  FUN_00086100  size=44 bytes */


void FUN_00086100(undefined4 param_1,int param_2,int param_3)

{
  do {
    param_3 = param_3 + -1;
    if (param_3 < 0) {
      return;
    }
  } while (*(int *)(param_2 + param_3 * 4) == 0);
  return;
}

