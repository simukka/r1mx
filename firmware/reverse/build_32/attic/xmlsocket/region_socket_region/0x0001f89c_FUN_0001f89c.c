/* 0x0001f89c  FUN_0001f89c  size=84 bytes */


undefined4 FUN_0001f89c(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = *(int *)(param_1 + 0x34) * 0x430;
  uVar2 = 0xffffffff;
  if ((*(int *)(iVar1 + 0x108e9e4) != 0) && (uVar2 = 0, *(int *)(iVar1 + 0x108e9e8) != 0)) {
    *(undefined4 *)(param_1 + 0x30) = 1;
    *(undefined4 *)(iVar1 + 0x108e9e8) = 0;
  }
  return uVar2;
}

