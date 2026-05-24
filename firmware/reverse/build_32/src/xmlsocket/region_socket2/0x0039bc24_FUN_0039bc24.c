/* 0x0039bc24  FUN_0039bc24  size=244 bytes */


int FUN_0039bc24(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_28 [28];
  
  FUN_0039bad0();
  iVar3 = param_1[1];
  iVar2 = param_1[2];
  iVar4 = *param_1;
  iVar1 = FUN_0039b780(param_1[5],param_1[4],param_1[3]);
  param_1[7] = iVar1 + -1;
  if (param_1[5] + 0x76c < 0x7b2) {
    iVar2 = -1;
  }
  else {
    iVar1 = FUN_0039b74c(param_1[5] + -0x46);
    param_1[6] = (iVar1 + 4) % 7;
    iVar2 = iVar4 + iVar3 * 0x3c + iVar2 * 0xe10 + iVar1 * 0x15180;
    iVar1 = FUN_0039be54(param_1,uRam00e2758c);
    param_1[8] = iVar1;
    if (iVar1 != 0) {
      iVar2 = iVar2 + -0xe10;
      FUN_0039bad0(param_1);
    }
    FUN_0039c120(auStack_28,2,uRam00e2758c);
    iVar1 = FUN_00399bcc(auStack_28);
    iVar2 = iVar2 + iVar1 * 0x3c;
  }
  return iVar2;
}

