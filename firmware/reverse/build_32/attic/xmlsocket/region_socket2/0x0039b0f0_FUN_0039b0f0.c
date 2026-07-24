/* 0x0039b0f0  FUN_0039b0f0  size=40 bytes */


char * FUN_0039b0f0(char *param_1)

{
  char cVar1;
  char *pcVar2;
  
  pcVar2 = param_1 + 1;
  cVar1 = *param_1;
  while (cVar1 != '\0') {
    param_1 = param_1 + 1;
    cVar1 = *param_1;
  }
  return param_1 + (1 - (int)pcVar2);
}

