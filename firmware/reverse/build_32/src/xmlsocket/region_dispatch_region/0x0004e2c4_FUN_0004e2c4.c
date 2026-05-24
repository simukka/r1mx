/* 0x0004e2c4  FUN_0004e2c4  size=372 bytes */


int FUN_0004e2c4(int *param_1,int param_2,uint *param_3)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  
  if (param_2 == 0x5502) {
    iVar4 = 0;
    FUN_001d9204(*(undefined4 *)(*param_1 + 8),0xffffffff);
    param_1[1] = (int)param_3;
    uVar1 = *(undefined4 *)(*param_1 + 8);
  }
  else {
    if (0x5502 < param_2) {
      if (param_2 == 0x5503) {
        FUN_001d9204(*(undefined4 *)(*param_1 + 8),0xffffffff);
        piVar6 = (int *)*param_1;
        uVar3 = *param_3;
        if (((uint)piVar6[1] < uVar3) || ((uVar3 & 3) != 0)) {
          iVar4 = piVar6[2];
          iVar5 = -1;
        }
        else {
          iVar4 = *piVar6;
          iVar5 = 0;
          uVar2 = FUN_000000dc(iVar4 + uVar3);
          FUN_000000e8(iVar4 + uVar3,uVar2 & ~param_3[1] | param_3[1] & param_3[2]);
          iVar4 = *(int *)(*param_1 + 8);
        }
        FUN_001d92bc(iVar4);
        return iVar5;
      }
      if (param_2 == 0x5504) {
        FUN_001d9204(*(undefined4 *)(*param_1 + 8),0xffffffff);
        iVar4 = *(int *)(*param_1 + 0xc);
        FUN_001d92bc(*(undefined4 *)(*param_1 + 8));
        return iVar4;
      }
      return -1;
    }
    if (param_2 != 0x5501) {
      return -1;
    }
    FUN_001d9204(*(undefined4 *)(*param_1 + 8),0xffffffff);
    iVar4 = param_1[1];
    uVar1 = *(undefined4 *)(*param_1 + 8);
  }
  FUN_001d92bc(uVar1);
  return iVar4;
}

