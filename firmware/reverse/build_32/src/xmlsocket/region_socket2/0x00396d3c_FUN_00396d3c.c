/* 0x00396d3c  FUN_00396d3c  size=112 bytes */


undefined4 FUN_00396d3c(int param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  
  if ((*(int *)(param_1 + 4) == param_1) && (*(char *)(param_1 + 10) == 'f')) {
    if ((param_1 == 0) || ((*(ushort *)(param_1 + 0x18) & 8) == 0)) {
      puVar1 = (undefined4 *)FUN_00442914();
      *puVar1 = 9;
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = FUN_00396c70();
    }
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

