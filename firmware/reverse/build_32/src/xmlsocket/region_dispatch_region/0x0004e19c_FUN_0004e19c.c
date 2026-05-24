/* 0x0004e19c  FUN_0004e19c  size=296 bytes */


int FUN_0004e19c(int *param_1,undefined4 *param_2,uint param_3)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  
  if (3 < (int)param_3) {
    uVar1 = param_1[1];
    uVar3 = *(uint *)(*param_1 + 4);
    param_1[1] = uVar1 & 0xfffffffc;
    if (((uVar1 & 0xfffffffc) + param_3 <= uVar3) && ((param_3 & 3) == 0)) {
      FUN_001d9204(*(undefined4 *)(*param_1 + 8),0xffffffff);
      iVar4 = 0;
      iVar5 = param_1[1] + *(int *)*param_1;
      if ((int)param_3 < 1) {
        iVar4 = ((int *)*param_1)[2];
        param_1[1] = param_1[1] + param_3;
        FUN_001d92bc(iVar4);
        iVar4 = 0;
      }
      else {
        do {
          iVar4 = iVar4 + 4;
          FUN_000000e8(iVar5,*param_2);
          iVar5 = iVar5 + 4;
          param_2 = param_2 + 1;
        } while (iVar4 < (int)param_3);
        uVar2 = *(undefined4 *)(*param_1 + 8);
        param_1[1] = param_1[1] + param_3;
        FUN_001d92bc(uVar2);
      }
      return iVar4;
    }
  }
  return -1;
}

