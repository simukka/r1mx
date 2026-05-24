/* 0x0039e64c  FUN_0039e64c  size=44 bytes */


bool FUN_0039e64c(int param_1,uint param_2,undefined4 *param_3)

{
  *param_3 = 0;
  if (param_2 < 5) {
    *param_3 = *(undefined4 *)(param_1 + param_2 * 4 + 4);
  }
  return param_2 < 5;
}

