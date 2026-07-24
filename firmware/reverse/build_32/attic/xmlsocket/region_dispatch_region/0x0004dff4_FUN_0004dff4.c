/* 0x0004dff4  FUN_0004dff4  size=84 bytes */


undefined4 FUN_0004dff4(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  uVar1 = FUN_001d91b4();
  param_1[1] = param_3;
  param_1[2] = uVar1;
  *param_1 = param_2;
  return 0;
}

