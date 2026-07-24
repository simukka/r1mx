/* 0x003780f4  FUN_003780f4  size=184 bytes */


void FUN_003780f4(int param_1)

{
  int iVar1;
  uint in_MSR;
  int iVar2;
  
  if (param_1 == 1) {
    if ((in_MSR & 0x10) == 0) {
      iVar1 = iRam00e26ebc - iRam0065c600;
      iVar2 = iRam0065c604;
      do {
        iVar1 = iRam0065c600 + iVar1;
        dataCacheBlockFlush(iVar1);
        dataCacheBlockFlush(iVar1 + iRam0065c604 * 0x20);
        iVar2 = iVar2 + -1;
      } while (iVar2 != 0);
      sync(0);
      sync(0);
      FUN_003782d4(0);
      return;
    }
  }
  else if ((in_MSR & 0x20) == 0) {
    instructionSynchronize();
    FUN_003782d4(0);
    return;
  }
  FUN_0036d004();
  return;
}

