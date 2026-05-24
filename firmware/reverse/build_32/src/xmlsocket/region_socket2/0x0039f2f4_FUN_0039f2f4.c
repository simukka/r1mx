/* 0x0039f2f4  FUN_0039f2f4  size=136 bytes */


void FUN_0039f2f4(int param_1)

{
  if (pcRam010cf3ec == reset_vector) {
    pcRam010cf3ec = (code *)0x46b580;
  }
  if (param_1 != 0) {
    FUN_005accf4(uRam010cf3e0,0xffffffff);
    (*pcRam010cf3ec)(param_1);
    iRam010cf3f8 = iRam010cf3f8 + 1;
    FUN_005ad104(uRam010cf3e0);
  }
  return;
}

