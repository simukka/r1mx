/* 0x0003083c  FUN_0003083c  size=116 bytes */


undefined4 FUN_0003083c(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0002fd30(param_1,param_2,1,0);
  uVar3 = 0xffffffff;
  if (iVar1 != -1) {
    uVar3 = FUN_0002c92c();
    uVar2 = FUN_00442920();
    FUN_0002c680(iVar1);
    FUN_00442990(uVar2);
  }
  return uVar3;
}

