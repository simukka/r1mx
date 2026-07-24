/* 0x0039a81c  FUN_0039a81c  size=140 bytes */


undefined4 FUN_0039a81c(uint param_1)

{
  undefined4 uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  
  if (param_1 < 5) {
    uVar1 = *(undefined4 *)(param_1 * 8 + 0xe27430);
  }
  else {
    if ((param_1 & 1) == 0) {
      uVar3 = FUN_0039a81c(param_1 >> 1);
      uVar2 = FUN_0039a81c(param_1 >> 1);
    }
    else {
      uVar2 = FUN_0039a81c(param_1 - 1);
      uVar3 = 0x4024000000000000;
    }
    uVar1 = FUN_00373704((int)((ulonglong)uVar2 >> 0x20),(int)uVar2,(int)((ulonglong)uVar3 >> 0x20),
                         (int)uVar3);
  }
  return uVar1;
}

