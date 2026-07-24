/* 0x0039b118  FUN_0039b118  size=112 bytes */


void FUN_0039b118(char *param_1,char *param_2,int param_3)

{
  char cVar1;
  
  if (param_3 == 0) {
    return;
  }
  cVar1 = *param_1;
  while (cVar1 != '\0') {
    param_1 = param_1 + 1;
    cVar1 = *param_1;
  }
  cVar1 = *param_2;
  *param_1 = cVar1;
  while (param_1 = param_1 + 1, cVar1 != '\0') {
    param_2 = param_2 + 1;
    param_3 = param_3 + -1;
    if (param_3 == 0) goto LAB_0039b17c;
    cVar1 = *param_2;
    *param_1 = cVar1;
  }
  if (param_3 != 0) {
    return;
  }
LAB_0039b17c:
  *param_1 = '\0';
  return;
}

