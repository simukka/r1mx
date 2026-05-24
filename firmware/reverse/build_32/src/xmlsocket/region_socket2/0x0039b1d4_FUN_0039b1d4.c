/* 0x0039b1d4  FUN_0039b1d4  size=84 bytes */


void FUN_0039b1d4(char *param_1,char *param_2,int param_3)

{
  char cVar1;
  
  if (param_3 == 0) {
    return;
  }
  do {
    cVar1 = *param_2;
    param_3 = param_3 + -1;
    *param_1 = cVar1;
    if (cVar1 == '\0') {
      if (param_3 != 0) {
        do {
          param_1 = param_1 + 1;
          *param_1 = '\0';
          param_3 = param_3 + -1;
        } while (param_3 != 0);
        return;
      }
      return;
    }
    param_2 = param_2 + 1;
    param_1 = param_1 + 1;
  } while (param_3 != 0);
  return;
}

