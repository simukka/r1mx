/* 0x00033e2c  FUN_00033e2c  size=140 bytes */


undefined4 FUN_00033e2c(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0002b410(param_1,0);
  if (iVar1 == 0) {
    FUN_003cb350(0xd38704,param_1);
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = FUN_005accf4(*(undefined4 *)(iVar1 + 0x138),0xffffffff);
    uVar3 = 0xffffffff;
    if (iVar2 == 0) {
      *(undefined4 *)(iVar1 + 0x124) = param_2;
      FUN_005ad104(*(undefined4 *)(iVar1 + 0x138));
      uVar3 = *(undefined4 *)(iVar1 + 0x124);
    }
  }
  return uVar3;
}

