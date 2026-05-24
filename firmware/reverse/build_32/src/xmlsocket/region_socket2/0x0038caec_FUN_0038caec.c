/* 0x0038caec  FUN_0038caec  size=176 bytes */


void FUN_0038caec(int param_1)

{
  uint uVar1;
  
  if ((*(uint *)(param_1 + 0x48) & 9) != 1) {
LAB_0038cb10:
    *(undefined4 *)(param_1 + 0x44) = 0;
    *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) & 0xfffffff6;
    return;
  }
  if (*(code **)(param_1 + 0x50) == reset_vector) {
    if (**(int **)(param_1 + 0x10) == 0) goto LAB_0038cb10;
    FUN_00245be8();
    uVar1 = *(uint *)(param_1 + 0x48);
  }
  else {
    (**(code **)(param_1 + 0x50))(**(undefined4 **)(param_1 + 0x10));
    uVar1 = *(uint *)(param_1 + 0x48);
  }
  *(undefined4 *)(param_1 + 0x44) = 0;
  *(uint *)(param_1 + 0x48) = uVar1 & 0xfffffff6;
  return;
}

