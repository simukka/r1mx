/* 0x00027a48  FUN_00027a48  size=140 bytes */


int FUN_00027a48(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar2 = FUN_005accf4(param_1 + 0x2c4,0xffffffff);
  iVar1 = 0;
  if (iVar2 != -1) {
    iVar1 = *(int *)(param_1 + 0x424);
    if (iVar1 != 0) {
      *(undefined4 *)(param_1 + 0x424) = *(undefined4 *)(iVar1 + 0x2c);
      *(undefined4 *)(iVar1 + 0x2c) = 0;
      if (*(int *)(param_1 + 0x424) == 0) {
        *(undefined4 *)(param_1 + 0x428) = 0;
      }
    }
    FUN_005ad104(param_1 + 0x2c4);
  }
  return iVar1;
}

