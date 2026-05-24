/* 0x00398c40  FUN_00398c40  size=92 bytes */


undefined4 FUN_00398c40(int param_1)

{
  undefined4 uVar1;
  
  if ((*(int *)(param_1 + 4) == param_1) && (*(char *)(param_1 + 10) == 'f')) {
    FUN_00442e64();
    FUN_0045b580(param_1);
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

