/* 0x00398aac  FUN_00398aac  size=84 bytes */


void FUN_00398aac(int param_1)

{
  int iVar1;
  
  iVar1 = FUN_0044e6d0((int)*(short *)(param_1 + 0x1a));
  if (iVar1 == -1) {
    *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) & 0xefff;
  }
  else {
    *(int *)(param_1 + 0x48) = iVar1;
    *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) | 0x1000;
  }
  return;
}

