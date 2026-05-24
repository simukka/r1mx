/* 0x00398534  FUN_00398534  size=56 bytes */


undefined4 FUN_00398534(int param_1)

{
  undefined4 uVar1;
  
  if ((*(ushort *)(param_1 + 0x18) & 9) == 9) {
    uVar1 = FUN_00396c70();
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

