/* 0x005f1708  FUN_005f1708  size=252 bytes */


void FUN_005f1708(undefined4 *param_1,undefined4 *param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  for (; param_1 != param_2; param_1 = param_1 + 4) {
    if (param_3 != (undefined4 *)0x0) {
      uVar1 = param_1[1];
      uVar3 = param_1[2];
      uVar2 = param_1[3];
      *param_3 = *param_1;
      param_3[1] = uVar1;
      param_3[2] = uVar3;
      param_3[3] = uVar2;
    }
    param_3 = param_3 + 4;
  }
  return;
}

