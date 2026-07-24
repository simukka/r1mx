
int FUN_001d9204(undefined4 param_1,uint param_2)

{
  int iVar1;
  
  if (param_2 != 0xffffffff && param_2 != 0) {
    iVar1 = FUN_00009518();
    param_2 = (iVar1 * param_2) / 1000;
    if (param_2 == 0) {
      iVar1 = FUN_005accf4(param_1,1);
      return -(uint)(iVar1 != 0);
    }
  }
  iVar1 = FUN_005accf4(param_1,param_2);
  return -(uint)(iVar1 != 0);
}

