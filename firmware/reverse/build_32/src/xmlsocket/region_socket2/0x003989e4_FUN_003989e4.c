/* 0x003989e4  FUN_003989e4  size=100 bytes */


int FUN_003989e4(int param_1)

{
  int iVar1;
  
  iVar1 = FUN_0044e144((int)*(short *)(param_1 + 0x1a));
  if (iVar1 < 0) {
    *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) & 0xefff;
  }
  else {
    *(int *)(param_1 + 0x48) = iVar1 + *(int *)(param_1 + 0x48);
  }
  return iVar1;
}

