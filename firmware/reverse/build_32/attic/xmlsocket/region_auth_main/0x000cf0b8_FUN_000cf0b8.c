/* 0x000cf0b8  FUN_000cf0b8  size=76 bytes */


void FUN_000cf0b8(void)

{
  int iVar1;
  int iVar2;
  undefined4 auStack_38 [6];
  
  iVar2 = FUN_0005e938();
  auStack_38[0] = 0x15;
  iVar1 = FUN_001d8fc0(*(undefined4 *)(iVar2 + 0x20),auStack_38,0x28,0xffffffff);
  if (iVar1 != 0) {
    iVar1 = iVar2 + 0x28;
    if (0xf < *(uint *)(iVar2 + 0x3c)) {
      iVar1 = *(int *)(iVar2 + 0x28);
    }
    FUN_0005e784(0,3,0x1a,0xd45a4c,0x65f858,0x8a9,0xd46004,iVar1);
  }
  return;
}

