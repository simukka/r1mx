/* 0x000f6200  FUN_000f6200  size=128 bytes */


void FUN_000f6200(undefined4 param_1,int param_2,int param_3,uint param_4)

{
  undefined1 *puVar1;
  uint uVar2;
  
  uVar2 = 0;
  if (param_4 != 0) {
    do {
      puVar1 = (undefined1 *)(param_3 + uVar2);
      uVar2 = uVar2 + 1;
      FUN_003cae4c(param_2,0xd49df0,*puVar1);
      param_2 = param_2 + 2;
    } while (uVar2 < param_4);
  }
  return;
}

