/* 0x00026ac4  FUN_00026ac4  size=344 bytes */


undefined4 FUN_00026ac4(int param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_40 [12];
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  
  if (6 < iRam00e107b4) {
    FUN_00443f20(0xd36400,*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0,0,0,0);
  }
  iVar3 = 0xb;
  auStack_40[0] = 0;
  iVar2 = 1;
  do {
    auStack_40[iVar2] = 0;
    iVar2 = iVar2 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  uStack_20 = 0;
  uStack_34 = 0;
  uStack_30 = 0;
  uStack_2c = 0;
  uStack_28 = 0;
  uStack_24 = 0;
  iVar2 = 0;
  while( true ) {
    uVar1 = FUN_00026628(param_1,auStack_40);
    uVar1 = uVar1 & 0xf0;
    iVar2 = iVar2 + 1;
    if (((int)(-(uVar1 ^ 0x60) & -uVar1) < 0) || (5 < iVar2)) break;
    if (uVar1 == 0) {
      if (6 < iRam00e107b4) {
        FUN_00443f20(0xd3641c,*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0,0,0,
                     0);
      }
      return 0;
    }
  }
  return 0xffffffff;
}

