/* 0x0039ad28  FUN_0039ad28  size=60 bytes */


char * FUN_0039ad28(char *param_1,char param_2)

{
  char cVar1;
  
  cVar1 = *param_1;
  while( true ) {
    if (cVar1 == param_2) {
      return param_1;
    }
    if (*param_1 == '\0') break;
    param_1 = param_1 + 1;
    cVar1 = *param_1;
  }
  return (char *)0x0;
}

