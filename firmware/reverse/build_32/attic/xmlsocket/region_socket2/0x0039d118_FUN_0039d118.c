/* 0x0039d118  FUN_0039d118  size=332 bytes */


undefined4 FUN_0039d118(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  if (iRam00e9c6a4 == 0) {
    if (iRam00e9c60c == 0) {
      iRam00e9c60c = 0x4b;
    }
    FUN_0039acec(0x10cf3e0,0,0x54);
    uRam010cf3e0 = FUN_005ab360(0,1);
    iRam00e9c6a4 = FUN_0039edf0();
    if (iRam00e9c6a4 != 0) {
      if (iRam00e9c0c8 == 0) {
        iRam00e9c0c8 = 10;
      }
      FUN_0039dba0(0xe9c250,0xe8,iRam00e9c0c8,iRam00e9c0c8 << 1,0,0);
      FUN_0039d0a4();
      iVar1 = FUN_005b0860(0x3ad43c);
      if (iVar1 == -1) {
        uVar2 = FUN_005af79c(0x3ad43c,iRam00e9c60c,0,20000,0x3cde84,0,0,0,0,0,0,0,0,0,0);
        *(undefined4 *)(iRam00e9c6a4 + 8) = uVar2;
        FUN_0039f834(100);
      }
    }
  }
  else {
    uVar3 = 2;
  }
  return uVar3;
}

