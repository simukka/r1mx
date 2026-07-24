/* 0x00378050  FUN_00378050  size=164 bytes */


undefined4 FUN_00378050(int param_1)

{
  undefined4 in_r0;
  undefined4 uVar1;
  int iVar2;
  uint in_MSR;
  int iVar3;
  int in_DCCR;
  int in_ICCR;
  
  if (param_1 == 1) {
    if ((in_MSR & 0x10) != 0) goto LAB_003782b4;
    if (in_DCCR != iRam00e26a08) {
      iVar2 = 0;
      iVar3 = iRam0065c604;
      do {
        dataCacheCongruenceClassInvalidate(iVar2);
        iVar2 = iVar2 + iRam0065c600;
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
      instructionSynchronize();
      uVar1 = FUN_003782d4(iVar2,uRam00e26a0c);
      return uVar1;
    }
  }
  else {
    if ((in_MSR & 0x20) != 0) {
LAB_003782b4:
      uVar1 = FUN_0036d004();
      return uVar1;
    }
    if (in_ICCR != iRam00e26a04) {
      instructionCacheCongruenceClassInvalidate(in_r0);
      instructionSynchronize();
      uVar1 = FUN_003782d4();
      return uVar1;
    }
  }
  sync(0);
  return 0;
}

