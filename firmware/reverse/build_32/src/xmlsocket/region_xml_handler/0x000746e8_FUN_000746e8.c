/* 0x000746e8  FUN_000746e8  size=216 bytes */


void FUN_000746e8(int param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined1 uStack_18;
  undefined1 uStack_17;
  undefined4 uStack_14;
  int iStack_10;
  
  if (*(int *)(param_1 + 0x58) != -1) {
    uStack_18 = 3;
    uStack_17 = 0x10;
    uStack_14 = 0x84ae0;
    iStack_10 = param_1;
    iVar1 = FUN_0044e510(*(int *)(param_1 + 0x58),param_2,&uStack_18);
    if (iVar1 == -1) {
      puVar2 = (undefined4 *)FUN_00442914();
      uVar3 = 0xd3f7d8;
      if (param_2 != 0x6a02000a) {
        uVar3 = 0xd3f7f8;
      }
      FUN_0005e784(0,3,5,0xd3f794,0x65e0e0,0x2e9,0xd3f7bc,0x65e100,uVar3,*puVar2);
    }
  }
  return;
}

