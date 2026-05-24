/* 0x00074944  FUN_00074944  size=172 bytes */


void FUN_00074944(int param_1,int param_2,int param_3)

{
  int iVar1;
  int aiStack_18 [3];
  undefined1 uStack_c;
  
  if (param_2 == 0xd) {
    uStack_c = param_3 != 0;
  }
  aiStack_18[0] = param_2;
  iVar1 = FUN_001d8fc0(*(undefined4 *)(param_1 + 0x20),aiStack_18,0x10,0);
  if (iVar1 != 0) {
    iVar1 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar1 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(0,3,5,0xd3f794,0x65e158,0x6a6,0xd3f844,iVar1);
  }
  return;
}

