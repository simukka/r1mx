/* 0x000cf150  FUN_000cf150  size=460 bytes */


void FUN_000cf150(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined4 auStack_60 [12];
  char acStack_30 [20];
  
  iVar4 = *(int *)(param_2 + 4);
  uVar5 = *(uint *)(iVar4 + 0x3c);
  uVar1 = FUN_0039b0f0(0xd3bbb4);
  if (uVar5 == 0) {
LAB_000cf234:
    uVar3 = (uint)(uVar5 != uVar1);
    if (uVar1 <= uVar5) goto LAB_000cf1d0;
  }
  else {
    iVar2 = iVar4 + 0x2c;
    if (0xf < *(uint *)(iVar4 + 0x40)) {
      iVar2 = *(int *)(iVar4 + 0x2c);
    }
    uVar3 = uVar1;
    if (uVar5 < uVar1) {
      uVar3 = uVar5;
    }
    uVar3 = FUN_0039ac2c(iVar2,0xd3bbb4,uVar3);
    if (uVar3 == 0) goto LAB_000cf234;
LAB_000cf1d0:
    if (uVar3 == 0) {
      FUN_005f2a1c(0xd3bbb4,acStack_30,0x1a,0x65f87c);
      auStack_60[0] = 8;
      *(char *)(param_1 + 0x44) = acStack_30[0];
      goto joined_r0x000cf204;
    }
  }
  FUN_005f2a1c(0xd3bbcc,acStack_30,0x1a,0x65f87c);
  auStack_60[0] = 9;
  *(char *)(param_1 + 0x45) = acStack_30[0];
joined_r0x000cf204:
  if ((acStack_30[0] != '\0') &&
     (iVar4 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x20),auStack_60,0x28,0xffffffff), iVar4 != 0))
  {
    iVar4 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar4 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(0,3,0x1a,0xd45a4c,0x65f894,0xad9,0xd45f7c,iVar4);
    return;
  }
  return;
}

