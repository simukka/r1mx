/* 0x000ceccc  FUN_000ceccc  size=148 bytes */


void FUN_000ceccc(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 auStack_38 [5];
  undefined4 uStack_24;
  
  auStack_38[0] = 0xb;
  uStack_24 = param_2;
  iVar1 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x20),auStack_38,0x28,0xffffffff);
  if (iVar1 != 0) {
    iVar1 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar1 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(0,3,0x1a,0xd45a4c,0x65f82c,0x94e,0xd45fac,iVar1);
  }
  return;
}

