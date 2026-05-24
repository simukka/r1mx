/* 0x000cf024  FUN_000cf024  size=144 bytes */


void FUN_000cf024(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 auStack_38 [8];
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  auStack_38[0] = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  iVar1 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x20),auStack_38,0x28,0xffffffff);
  if (iVar1 != 0) {
    iVar1 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar1 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(0,3,0x1a,0xd45a4c,0x65f858,0x8a9,0xd46004,iVar1);
  }
  return;
}

