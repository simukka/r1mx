/* 0x0037af04  FUN_0037af04  size=212 bytes */


undefined4 FUN_0037af04(int param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int *piVar4;
  
  iVar2 = FUN_005b2190();
  if (iVar2 == 0) {
    FUN_005b17d0();
    piVar4 = (int *)iRam00e9c5c0;
    while (piVar1 = piVar4, piVar1 != (int *)0xe9c5c0) {
      piVar4 = (int *)*piVar1;
      if (((((piVar1[7] & 0x8000000U) != 0) && (((uint)piVar1[7] >> 0x15 & 1) != 0)) &&
          (piVar1[6] == param_1)) && (piVar1[3] == param_2)) {
        FUN_0037d91c();
      }
    }
    FUN_005b1894();
    uVar3 = 0;
  }
  else {
    FUN_003cb248(0xd6d340,param_1);
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

