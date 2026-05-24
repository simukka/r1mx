/* 0x0002a0f0  FUN_0002a0f0  size=156 bytes */


undefined4 FUN_0002a0f0(int param_1)

{
  int iVar1;
  int iVar2;
  
  FUN_005accf4(uRam00e9e554,0xffffffff);
  iVar1 = FUN_0049783c(0xe9e53c);
  while( true ) {
    if (iVar1 == 0) {
      FUN_005ad104(uRam00e9e554);
      return 0;
    }
    if ((*(int *)(iVar1 + 0x10) == param_1) && (iVar2 = FUN_00029ddc(iVar1), iVar2 != 0)) break;
    iVar1 = FUN_004978e4(iVar1);
  }
  return 0xffffffff;
}

