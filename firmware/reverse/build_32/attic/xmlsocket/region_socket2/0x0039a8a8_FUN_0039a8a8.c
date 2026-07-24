/* 0x0039a8a8  FUN_0039a8a8  size=224 bytes */


uint FUN_0039a8a8(uint *param_1,int param_2,int param_3)

{
  undefined4 *puVar1;
  uint uVar2;
  uint uVar3;
  undefined8 uVar4;
  
  if (param_2 < 0x135) {
    if (param_2 < -0x134) {
      puVar1 = (undefined4 *)FUN_00442914();
      *puVar1 = 0x26;
      uVar2 = 0;
    }
    else {
      uVar3 = param_1[1];
      uVar2 = *param_1;
      if (param_3 != 0) {
        uVar2 = uVar2 ^ 0x80000000;
      }
      if (param_2 != 0) {
        if (param_2 < 0) {
          FUN_00399ba8();
          uVar4 = FUN_0039a81c();
          uVar2 = FUN_003739c0(uVar2,uVar3,(int)((ulonglong)uVar4 >> 0x20),(int)uVar4);
        }
        else {
          uVar4 = FUN_0039a81c(param_2);
          uVar2 = FUN_00373704((int)((ulonglong)uVar4 >> 0x20),(int)uVar4,uVar2,uVar3);
        }
      }
    }
  }
  else {
    puVar1 = (undefined4 *)FUN_00442914();
    *puVar1 = 0x26;
    if (param_3 == 0) {
      uVar2 = 0x7fef0000;
    }
    else {
      uVar2 = 0xffef0000;
    }
    uVar2 = uVar2 | 0xffff;
  }
  return uVar2;
}

