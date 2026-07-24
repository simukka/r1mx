/* 0x00379a14  FUN_00379a14  size=164 bytes */


void FUN_00379a14(int param_1,undefined4 param_2)

{
  int iVar1;
  
  if (param_1 == -1) {
    iVar1 = FUN_0047bae0();
    if (iVar1 != 0) {
      do {
        FUN_0046ea04(iVar1,uRam00e27038,param_2,0);
        iVar1 = FUN_0047bb20(iVar1);
      } while (iVar1 != 0);
      return;
    }
  }
  else {
    FUN_0046ea04(param_1,uRam00e27038,param_2,0);
  }
  return;
}

