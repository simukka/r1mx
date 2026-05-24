/* 0x003999ec  FUN_003999ec  size=224 bytes */


undefined4
FUN_003999ec(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5
            ,undefined4 param_6,undefined4 param_7,undefined4 param_8)

{
  undefined4 uVar1;
  int iStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  int iStack_18;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined1 uStack_12;
  undefined1 *puStack_10;
  int *piStack_c;
  
  if ((*(int *)(param_1 + 4) == param_1) && (*(char *)(param_1 + 10) == 'f')) {
    puStack_10 = &stack0x00000008;
    piStack_c = &iStack_38;
    uStack_14 = 2;
    uStack_13 = 0;
    uStack_12 = 0xd;
    iStack_38 = param_1;
    uStack_34 = param_2;
    uStack_30 = param_3;
    uStack_2c = param_4;
    uStack_28 = param_5;
    uStack_24 = param_6;
    uStack_20 = param_7;
    uStack_1c = param_8;
    uVar1 = FUN_003c9b64(param_2,0x3a6dac,param_1,&iStack_18,&uStack_14);
    if (iStack_18 != -1) {
      FUN_00399384(iStack_18,param_1);
    }
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

