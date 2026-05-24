/* 0x0039b2bc  FUN_0039b2bc  size=108 bytes */


char * FUN_0039b2bc(char *param_1,char *param_2)

{
  char cVar1;
  char cVar2;
  char *pcVar3;
  char *pcVar4;
  char *pcVar5;
  
  if (*param_2 == '\0') {
    return param_1;
  }
  do {
    do {
      pcVar4 = param_1;
      param_1 = pcVar4 + 1;
      if (*pcVar4 == '\0') {
        return (char *)0x0;
      }
      pcVar5 = param_1;
      pcVar3 = param_2;
    } while (*pcVar4 != *param_2);
    do {
      cVar1 = pcVar3[1];
      if (cVar1 == '\0') {
        return pcVar4;
      }
      cVar2 = *pcVar5;
      pcVar5 = pcVar5 + 1;
      pcVar3 = pcVar3 + 1;
    } while (cVar2 == cVar1);
  } while( true );
}

