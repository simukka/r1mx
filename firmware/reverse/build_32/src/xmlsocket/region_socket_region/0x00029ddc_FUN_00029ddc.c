/* 0x00029ddc  FUN_00029ddc  size=96 bytes */


undefined4 FUN_00029ddc(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = FUN_005b804c(*(undefined4 *)(*(int *)(param_1 + 0x10) + 0x28),0x15,0);
  uVar1 = 0;
  if (iVar2 != 0x23 && iVar2 != 0) {
    FUN_00442990();
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

