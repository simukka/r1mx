/* 0x0012bfb0  FUN_0012bfb0  size=516 bytes */


void FUN_0012bfb0(int param_1,int *param_2)

{
  uint uVar1;
  int *piVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar1 = uRam00ea099c;
  if (param_2 == (int *)0x0) {
    return;
  }
  if (param_2[5] != 1) {
    return;
  }
  uVar5 = param_2[0xd];
  uVar4 = 0xea098c;
  if (0xf < uRam00ea09a0) {
    uVar4 = uRam00ea098c;
  }
  if (uVar5 == 0) {
LAB_0012c070:
    uVar3 = (uint)(uVar5 != uVar1);
    if (uVar5 < uVar1) {
      uVar3 = 0xffffffff;
    }
  }
  else {
    piVar2 = param_2 + 9;
    if (0xf < (uint)param_2[0xe]) {
      piVar2 = (int *)param_2[9];
    }
    uVar3 = uRam00ea099c;
    if (uVar5 < uRam00ea099c) {
      uVar3 = uVar5;
    }
    uVar3 = FUN_0039ac2c(piVar2,uVar4,uVar3);
    if (uVar3 == 0) goto LAB_0012c070;
  }
  uVar1 = uRam00ea0980;
  if (uVar3 == 0) {
    uVar4 = (**(code **)(*param_2 + 0x2c))(param_2);
    *(undefined4 *)(param_1 + 0x38) = uVar4;
    FUN_001213cc(param_1);
    FUN_0012bd1c(param_1);
    return;
  }
  uVar5 = param_2[0xd];
  uVar4 = 0xea0970;
  if (0xf < uRam00ea0984) {
    uVar4 = uRam00ea0970;
  }
  if (uVar5 != 0) {
    piVar2 = param_2 + 9;
    if (0xf < (uint)param_2[0xe]) {
      piVar2 = (int *)param_2[9];
    }
    uVar3 = uRam00ea0980;
    if (uVar5 < uRam00ea0980) {
      uVar3 = uVar5;
    }
    uVar3 = FUN_0039ac2c(piVar2,uVar4,uVar3);
    if (uVar3 != 0) goto LAB_0012c0e8;
  }
  uVar3 = (uint)(uVar5 != uVar1);
  if (uVar5 < uVar1) {
    uVar3 = 0xffffffff;
  }
LAB_0012c0e8:
  if (uVar3 != 0) {
    return;
  }
  uVar4 = (**(code **)(*param_2 + 0x2c))(param_2);
  *(undefined4 *)(param_1 + 0x38) = uVar4;
  FUN_001213cc(param_1);
  FUN_001214f4(param_1);
  return;
}

