/* 0x000374e8  FUN_000374e8  size=252 bytes */


undefined4 FUN_000374e8(int *param_1,uint param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar4 = *(int *)(*param_1 + 0x30);
  uVar1 = param_2;
  while( true ) {
    if ((param_2 + param_3) - 1 <= uVar1) {
      iVar2 = (**(code **)(iVar4 + 0x38))
                        (param_1,*(undefined1 *)(iVar4 + 0x54),uVar1,*(undefined4 *)(iVar4 + 0x70));
      uVar3 = 0xffffffff;
      if (iVar2 == 0) {
        uVar3 = 0;
        *(int *)(iVar4 + 0x60) = *(int *)(iVar4 + 0x60) + -1;
      }
      return uVar3;
    }
    iVar2 = (**(code **)(iVar4 + 0x38))(param_1,*(undefined1 *)(iVar4 + 0x54),uVar1,uVar1 + 1);
    if (iVar2 != 0) break;
    *(int *)(iVar4 + 0x60) = *(int *)(iVar4 + 0x60) + -1;
    uVar1 = uVar1 + 1;
  }
  return 0xffffffff;
}

