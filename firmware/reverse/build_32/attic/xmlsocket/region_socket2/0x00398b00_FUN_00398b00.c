/* 0x00398b00  FUN_00398b00  size=88 bytes */


undefined4 FUN_00398b00(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = (int)*(short *)(param_1 + 0x1a);
  uVar2 = 0;
  if (((iVar1 < 0) || (2 < iVar1)) && (iVar1 = FUN_0044f9fc(iVar1), iVar1 < 0)) {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

