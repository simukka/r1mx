/* 0x0002b410  FUN_0002b410  size=188 bytes */


uint FUN_0002b410(uint param_1,uint *param_2)

{
  uint uVar1;
  uint auStack_10 [2];
  
  if (param_2 == (uint *)0x0) {
    param_2 = auStack_10;
  }
  *param_2 = 0;
  if ((param_1 == 0) ||
     (((((uVar1 = FUN_004501d8(param_1,param_2), uVar1 == 0 || (*param_2 == param_1)) ||
        ((uVar1 & 3) != 0)) || (*(int *)(uVar1 + 0x20) != -0x205368dd)) &&
      (((param_1 & 3) != 0 || (uVar1 = param_1, *(int *)(param_1 + 0x20) != -0x205368dd)))))) {
    FUN_00442990(0x38000a);
    uVar1 = 0;
  }
  return uVar1;
}

