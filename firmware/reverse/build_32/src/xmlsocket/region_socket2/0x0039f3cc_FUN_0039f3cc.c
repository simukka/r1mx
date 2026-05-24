/* 0x0039f3cc  FUN_0039f3cc  size=52 bytes */


undefined4 FUN_0039f3cc(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  if ((iRam00e9c6a4 != 0) || (uVar1 = param_1, param_1 < 0x1001)) {
    uVar2 = 1;
    uVar1 = uRam00e9c5ec;
  }
  uRam00e9c5ec = uVar1;
  return uVar2;
}

