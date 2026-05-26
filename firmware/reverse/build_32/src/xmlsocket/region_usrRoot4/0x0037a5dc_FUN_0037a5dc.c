/* 0x0037a5dc  FUN_0037a5dc  size=576 bytes */


undefined4 FUN_0037a5dc(int param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_d8 [176];
  undefined1 auStack_28 [20];
  
  iVar1 = FUN_005b2190();
  if (iVar1 == 0) {
    if (param_2 == 1) {
      iVar1 = FUN_005b0750(param_1,auStack_d8);
      if (iVar1 != 0) goto LAB_0037a710;
      iVar1 = FUN_005b831c(auStack_d8);
      if (iVar1 == 0) {
        FUN_003cb248(0xd6ce88,param_5);
        return 0xffffffff;
      }
      iVar1 = FUN_0037b4f0(iVar1,param_1,0x8200000,0,6,0,0,auStack_28);
      if (iVar1 != 0) {
LAB_0037a77c:
        FUN_003cb248(uRam00e27050,param_5);
        return 0xffffffff;
      }
    }
    else {
      if (param_2 != 0) {
        if (param_2 == 2) {
          if (param_3 != 0) {
            FUN_005b846c(param_1,param_3,param_4);
          }
          uVar3 = uRam00e2704c;
          *(uint *)(param_1 + 0x268) = *(uint *)(param_1 + 0x268) | 0x20;
          FUN_0046ea04(0,uVar3,param_1,0);
          iVar1 = FUN_0037b740(param_1,0,0);
          if (iVar1 == 0) {
            return 0;
          }
        }
        else {
          if (param_2 != 3) {
            return 0;
          }
          iVar1 = FUN_005b84c0(param_1);
          iVar2 = FUN_005b842c();
          if (iVar2 == 0) {
            uVar3 = FUN_0037a5dc(param_1,2,0,0,param_5);
            return uVar3;
          }
          iVar2 = FUN_005b8314(iVar1);
          iVar1 = FUN_0037b4f0(iVar2 * 4 + iVar1,param_1,0x8200000,0,6,0,0,auStack_28);
          if (iVar1 != 0) goto LAB_0037a77c;
          FUN_0046ea04(0,uRam00e2704c,param_1,0);
          iVar1 = FUN_0037b618(param_1);
          if (iVar1 != -1) {
            return 0;
          }
        }
        FUN_0046eb64(0,uRam00e2704c,0);
        goto LAB_0037a710;
      }
      if (param_3 != 0) {
        FUN_005b846c(param_1,param_3,param_4);
      }
    }
    iVar1 = FUN_0037b618(param_1);
    if (iVar1 == 0) {
      return 0;
    }
  }
LAB_0037a710:
  FUN_003cb248(uRam00e27044,param_5,param_1);
  return 0xffffffff;
}

