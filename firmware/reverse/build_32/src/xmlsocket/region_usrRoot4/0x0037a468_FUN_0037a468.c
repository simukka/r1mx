/* 0x0037a468  FUN_0037a468  size=372 bytes */


undefined4 FUN_0037a468(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar1 = FUN_0037afd8();
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  iVar1 = FUN_00491ac4(param_1);
  if (iVar1 == -1) {
    FUN_003cb248(uRam00e27048,param_2);
  }
  else {
    if (iVar1 == 0) {
      iVar1 = FUN_005b2184();
    }
    iVar2 = FUN_005b2190(iVar1);
    uVar4 = uRam00e27044;
    if (iVar2 != -1) {
      iVar2 = FUN_005b0954(iVar1);
      if (iVar2 != 0) {
        iVar2 = iVar1;
        if (iVar1 == 0) {
          iVar2 = FUN_005b2184();
        }
        iVar3 = FUN_005b219c(iVar2);
        if (iVar3 == 0) {
          FUN_003cb248(0xd6d2bc,param_2,iVar2);
          return 0xffffffff;
        }
        if ((*(uint *)(iVar3 + 0x98) & 2) != 0) {
          uVar4 = FUN_005b081c(iVar2);
          FUN_003cb248(0xd6d294,param_2,iVar2,uVar4);
          return 0xffffffff;
        }
        uVar4 = FUN_0047bfa8(0,iVar1);
        return uVar4;
      }
      uVar4 = 0xd6d2d8;
    }
    FUN_003cb248(uVar4,param_2,iVar1);
  }
  return 0xffffffff;
}

