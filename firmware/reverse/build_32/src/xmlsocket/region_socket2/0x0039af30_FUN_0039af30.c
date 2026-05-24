/* 0x0039af30  FUN_0039af30  size=44 bytes */


char * FUN_0039af30(char *param_1,char *param_2)

{
  char *pcVar1;
  char cVar2;
  
  cVar2 = *param_2;
  *param_1 = cVar2;
  pcVar1 = param_1;
  while (cVar2 != '\0') {
    param_2 = param_2 + 1;
    cVar2 = *param_2;
    pcVar1 = pcVar1 + 1;
    *pcVar1 = cVar2;
  }
  return param_1;
}

