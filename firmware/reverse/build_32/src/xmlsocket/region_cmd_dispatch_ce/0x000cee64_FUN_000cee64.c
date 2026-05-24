/* 0x000cee64  FUN_000cee64  size=156 bytes */


void FUN_000cee64(int param_1,undefined4 param_2,undefined4 param_3,undefined1 param_4)

{
  int iVar1;
  undefined4 auStack_38 [2];
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined1 uStack_28;
  
  auStack_38[0] = 4;
  uStack_30 = param_2;
  uStack_2c = param_3;
  uStack_28 = param_4;
  iVar1 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x20),auStack_38,0x28,0xffffffff);
  if (iVar1 != 0) {
    iVar1 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar1 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(0,3,0x1a,0xd45a4c,0x65f84c,0x8ce,0xd45fdc,iVar1);
  }
  return;
}

