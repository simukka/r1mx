/* 0x0037c964  FUN_0037c964  size=68 bytes */


undefined4 FUN_0037c964(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0x503;
  if (param_1 == 0) {
    if ((uRam00e9c084 & 2) != 0) {
      uVar1 = 0;
    }
  }
  else if ((uRam00e9c084 & 2) == 0) {
    uVar1 = 0;
  }
  return uVar1;
}

