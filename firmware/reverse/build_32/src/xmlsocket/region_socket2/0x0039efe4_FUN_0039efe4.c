/* 0x0039efe4  FUN_0039efe4  size=172 bytes */


int FUN_0039efe4(uint param_1)

{
  int iVar1;
  
  FUN_005accf4(uRam010cf3e0,0xffffffff);
  iVar1 = FUN_0045b9e4(uRam00e9c510,param_1,8);
  if (iVar1 == 0) {
    FUN_003cb350(0x3af4c3);
  }
  else {
    FUN_0039acec(iVar1,0,param_1);
    iRam010cf418 = iRam010cf418 + 1;
    iRam010cf424 = param_1 + iRam010cf424;
    if (uRam010cf428 < param_1) {
      uRam010cf428 = param_1;
    }
  }
  FUN_005ad104(uRam010cf3e0);
  return iVar1;
}

