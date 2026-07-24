/* 0x000f6280  FUN_000f6280  size=148 bytes */


void FUN_000f6280(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 auStack_118 [2];
  undefined4 uStack_110;
  
  auStack_118[0] = 5;
  uStack_110 = param_2;
  iVar1 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x20),auStack_118,0x10c,0);
  if (iVar1 != 0) {
    iVar1 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar1 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(0,3,0x1f,0xd49df8,0x661664,0x56d,0xd49e1c,iVar1);
  }
  return;
}

