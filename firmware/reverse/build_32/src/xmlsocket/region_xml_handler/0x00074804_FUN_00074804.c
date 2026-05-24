/* 0x00074804  FUN_00074804  size=176 bytes */


void FUN_00074804(int param_1)

{
  undefined1 *puVar1;
  int iVar2;
  
  if (*(int *)(param_1 + 0x44) != 0) {
    FUN_0005e784(2,3,0xc,0xd3f794,0x65e120,0x5dc,0xd3f818);
  }
  if (*(int *)(param_1 + 0x48) != -1) {
    FUN_0044f9fc();
  }
  *(undefined4 *)(param_1 + 0x44) = 0;
  *(undefined4 *)(param_1 + 0x48) = 0xffffffff;
  FUN_0021a460(0xffffffff);
  iVar2 = 6;
  puVar1 = (undefined1 *)0xe10c6c;
  do {
    *puVar1 = 0;
    puVar1 = puVar1 + 0x10;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}

