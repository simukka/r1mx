/* 0x005f1618  FUN_005f1618  size=240 bytes */


void FUN_005f1618(undefined4 *param_1,int param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  for (; param_2 != 0; param_2 = param_2 + -1) {
    if (param_1 != (undefined4 *)0x0) {
      uVar1 = param_3[1];
      uVar3 = param_3[2];
      uVar2 = param_3[3];
      *param_1 = *param_3;
      param_1[1] = uVar1;
      param_1[2] = uVar3;
      param_1[3] = uVar2;
    }
    param_1 = param_1 + 4;
  }
  return;
}

