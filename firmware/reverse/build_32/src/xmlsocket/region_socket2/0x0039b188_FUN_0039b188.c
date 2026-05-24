/* 0x0039b188  FUN_0039b188  size=76 bytes */


int FUN_0039b188(byte *param_1,byte *param_2,int param_3)

{
  uint uVar1;
  
  if (param_3 == 0) {
    return 0;
  }
  do {
    uVar1 = (uint)*param_1;
    param_1 = param_1 + 1;
    if (uVar1 != *param_2) {
      return uVar1 - *param_2;
    }
  } while ((uVar1 != 0) && (param_3 = param_3 + -1, param_2 = param_2 + 1, param_3 != 0));
  return 0;
}

