/* 0x0007bad0  FUN_0007bad0  size=552 bytes */


void FUN_0007bad0(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  uVar6 = 0xd3fdfc;
  FUN_0005e784(2,2,1,0xd3fdd0,0x65e3b4,0x4a2,0xd3fe04,0x65e3b4,0xd3fdfc);
  iVar1 = FUN_001a7504(0xd3fe20);
  if (iVar1 == -1) {
    iVar1 = 0x400000;
    FUN_0005e784(0,3,1,0xd3fdd0,0x65e3b4,0x4a9,0xd3ff08,0x65e3b4,uVar6);
  }
  iVar2 = FUN_001a7504(0xd3fe28);
  if (iVar2 == -1) {
    iVar2 = 0x1000000;
    FUN_0005e784(0,3,1,0xd3fdd0,0x65e3b4,0x4b3,0xd3fed4,0x65e3b4,uVar6);
  }
  iVar1 = FUN_0043bf50(0x200,iVar2 * 2 + iVar1 + 0x40000,0,0xd3fdfc);
  *(int *)(param_1 + 0x4c) = iVar1;
  if (iVar1 == 0) {
    uVar5 = 0xd3fe34;
    uVar3 = 3;
    uVar4 = 0x4bb;
    uVar6 = 0;
  }
  else {
    FUN_0005e784(2,2,1,0xd3fdd0,0x65e3b4,0x4c2,0xd3fe60,0x65e3b4,0xd3fdfc);
    iVar1 = FUN_00033a44(0xd3fdfc,6,0);
    if (iVar1 != 0) {
      FUN_0005e784(0,3,1,0xd3fdd0,0x65e3b4,0x4c6,0xd3fe80,0x65e3b4,0xd3fdfc);
      return;
    }
    uVar5 = 0xd3feac;
    uVar6 = 2;
    uVar3 = 2;
    uVar4 = 0x4cc;
  }
  FUN_0005e784(uVar6,uVar3,1,0xd3fdd0,0x65e3b4,uVar4,uVar5,0x65e3b4,0xd3fdfc);
  return;
}

