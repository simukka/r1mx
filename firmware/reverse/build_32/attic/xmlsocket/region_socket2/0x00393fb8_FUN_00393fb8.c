/* 0x00393fb8  FUN_00393fb8  size=160 bytes */


undefined4 FUN_00393fb8(uint param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  iVar1 = iRam0108b7b8;
  uVar4 = ~(iRam0108b7b8 - 1U);
  iVar2 = FUN_0000d87c();
  if (((param_1 < ((iVar2 + iVar1) - 1U & uVar4)) && ((uVar4 & 0xe0ba40) <= param_1)) ||
     ((param_1 < (iVar1 + 0xe0ba2fU & uVar4) && ((uVar4 & 0x10000) <= param_1)))) {
    uVar3 = 1;
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

