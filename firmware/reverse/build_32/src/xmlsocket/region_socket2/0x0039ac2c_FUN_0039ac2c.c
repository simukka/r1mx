/* 0x0039ac2c  FUN_0039ac2c  size=72 bytes */


int FUN_0039ac2c(byte *param_1,byte *param_2,int param_3)

{
  if (param_3 == 0) {
    return 0;
  }
  do {
    if (*param_1 != *param_2) {
      return (uint)*param_1 - (uint)*param_2;
    }
    param_3 = param_3 + -1;
    param_1 = param_1 + 1;
    param_2 = param_2 + 1;
  } while (param_3 != 0);
  return 0;
}

