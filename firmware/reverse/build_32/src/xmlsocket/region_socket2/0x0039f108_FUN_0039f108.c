/* 0x0039f108  FUN_0039f108  size=112 bytes */


void FUN_0039f108(int param_1)

{
  if (param_1 != 0) {
    FUN_005accf4(uRam010cf3e0,0xffffffff);
    FUN_0045b5e4(uRam00e9c510,param_1);
    iRam010cf420 = iRam010cf420 + 1;
    FUN_005ad104(uRam010cf3e0);
  }
  return;
}

