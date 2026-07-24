/* 0x000f5e68  FUN_000f5e68  size=76 bytes */


char * FUN_000f5e68(undefined4 param_1,char *param_2)

{
  char cVar1;
  int iVar2;
  
  cVar1 = *param_2;
  iVar2 = 0;
  if (cVar1 == '\0') {
    cVar1 = *param_2;
  }
  else {
    do {
      if (cVar1 == '\"') break;
      iVar2 = iVar2 + 1;
      cVar1 = param_2[iVar2];
    } while (cVar1 != '\0');
  }
  param_2 = param_2 + iVar2;
  if (cVar1 == '\0') {
    param_2 = (char *)0x0;
  }
  return param_2;
}

