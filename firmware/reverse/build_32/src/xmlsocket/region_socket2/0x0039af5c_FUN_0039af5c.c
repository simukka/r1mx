/* 0x0039af5c  FUN_0039af5c  size=76 bytes */


char * FUN_0039af5c(char *param_1,char *param_2)

{
  char cVar1;
  char cVar2;
  char *pcVar3;
  char *pcVar4;
  
  cVar1 = *param_1;
  pcVar3 = param_1;
  while (cVar1 != '\0') {
    pcVar4 = param_2;
    while (cVar2 = *pcVar4, cVar2 != '\0') {
      pcVar4 = pcVar4 + 1;
      if (cVar1 == cVar2) goto LAB_0039afa0;
    }
    cVar1 = pcVar3[1];
    pcVar3 = pcVar3 + 1;
  }
LAB_0039afa0:
  return pcVar3 + (1 - (int)(param_1 + 1));
}

