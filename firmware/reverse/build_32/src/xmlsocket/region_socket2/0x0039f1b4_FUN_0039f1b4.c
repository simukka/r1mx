/* 0x0039f1b4  FUN_0039f1b4  size=176 bytes */


int FUN_0039f1b4(uint param_1)

{
  int iVar1;
  
  iVar1 = 0;
  if (pcRam010cf3e8 == reset_vector) {
    pcRam010cf3e8 = (code *)0x3af178;
  }
  if (param_1 != 0) {
    FUN_005accf4(uRam010cf3e0,0xffffffff);
    iVar1 = (*pcRam010cf3e8)(param_1);
    if (iVar1 != 0) {
      iRam010cf3f0 = iRam010cf3f0 + 1;
      iRam010cf3fc = param_1 + iRam010cf3fc;
      if (uRam010cf400 < param_1) {
        uRam010cf400 = param_1;
      }
    }
    FUN_005ad104(uRam010cf3e0);
  }
  return iVar1;
}

