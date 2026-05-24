/* 0x0039b5c8  FUN_0039b5c8  size=108 bytes */


int FUN_0039b5c8(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_0039b0f0();
    iVar1 = FUN_0045b974(iVar1 + 1);
    if (iVar1 == 0) {
      iVar1 = 0;
    }
    else {
      FUN_0039af30(iVar1,param_1);
    }
  }
  return iVar1;
}

