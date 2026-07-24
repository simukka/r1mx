/* 0x000886a4  FUN_000886a4  size=56 bytes */


uint FUN_000886a4(undefined4 param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = param_3;
  do {
    uVar1 = uVar1 + 1;
    if (0x3ff < uVar1) {
      return param_3;
    }
  } while (*(int *)(param_2 + uVar1 * 4) == 0);
  return uVar1;
}

