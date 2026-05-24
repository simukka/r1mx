/* 0x00075458  FUN_00075458  size=188 bytes */


void FUN_00075458(int param_1)

{
  int iVar1;
  
  iVar1 = param_1 + 0x28;
  if (*(int *)(param_1 + 0x44) != 0) {
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar1 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(3,1,5,0xd3f794,0x65e1d4,0x67f,0xd3f9b8,iVar1,*(int *)(param_1 + 0x44));
    FUN_00074804(param_1);
    iVar1 = FUN_00074c48(param_1);
    if (iVar1 != 0) {
      FUN_000750dc(param_1);
      return;
    }
  }
  return;
}

