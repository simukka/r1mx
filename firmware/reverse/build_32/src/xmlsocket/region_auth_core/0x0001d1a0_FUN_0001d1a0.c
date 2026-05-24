/* 0x0001d1a0  FUN_0001d1a0  size=168 bytes */


undefined4 FUN_0001d1a0(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == 0) {
    FUN_0000e4e0(0xd34cac,0x89);
    uVar2 = 0;
    uRam00e9c0ec = 1;
  }
  else {
    uRam00e9c0ec = 0;
    iVar1 = FUN_0001d15c(param_2);
    uVar2 = 2;
    if (iVar1 != 0) {
      *(undefined4 *)(iVar1 + 0xc) = 0x4b00;
      uVar2 = FUN_0001ca48(param_1,iVar1,*(undefined4 *)(iVar1 + 4));
      return uVar2;
    }
  }
  return uVar2;
}

