/* 0x0039abf8  FUN_0039abf8  size=52 bytes */


char * FUN_0039abf8(char *param_1,char param_2,int param_3)

{
  while( true ) {
    if (param_3 == 0) {
      return (char *)0x0;
    }
    if (*param_1 == param_2) break;
    param_3 = param_3 + -1;
    param_1 = param_1 + 1;
  }
  return param_1;
}

