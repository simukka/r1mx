/* 0x0039b228  FUN_0039b228  size=72 bytes */


char * FUN_0039b228(char *param_1,char *param_2)

{
  char cVar1;
  char cVar2;
  char *pcVar3;
  
  cVar1 = *param_1;
  do {
    if (cVar1 == '\0') {
      return (char *)0x0;
    }
    pcVar3 = param_2;
    while (cVar2 = *pcVar3, cVar2 != '\0') {
      pcVar3 = pcVar3 + 1;
      if (cVar2 == cVar1) {
        return param_1;
      }
    }
    cVar1 = param_1[1];
    param_1 = param_1 + 1;
  } while( true );
}

