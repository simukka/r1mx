/* 0x0039ad64  FUN_0039ad64  size=52 bytes */


int FUN_0039ad64(byte *param_1,byte *param_2)

{
  uint uVar1;
  
  do {
    uVar1 = (uint)*param_1;
    param_1 = param_1 + 1;
    if (uVar1 != *param_2) {
      return uVar1 - *param_2;
    }
    param_2 = param_2 + 1;
  } while (uVar1 != 0);
  return 0;
}

