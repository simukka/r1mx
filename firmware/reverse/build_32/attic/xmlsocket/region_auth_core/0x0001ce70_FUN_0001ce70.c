/* 0x0001ce70  FUN_0001ce70  size=360 bytes */


uint FUN_0001ce70(int param_1)

{
  bool bVar1;
  byte bVar2;
  undefined1 uVar3;
  uint uVar4;
  
  uVar4 = 0;
  if (*(int *)(param_1 + 0x3c) != 0) {
    do {
      bVar2 = FUN_0000e868(*(int *)(param_1 + 0x14) + 0x1017);
      if ((bVar2 & 0x10) == 0) {
        if ((bVar2 & 1) == 0) break;
        uVar3 = FUN_0000e868(*(int *)(param_1 + 0x14) + 0x1003);
        *(undefined1 *)(uVar4 + *(int *)(param_1 + 0x34)) = uVar3;
        uVar4 = uVar4 + 1;
        *(byte *)(param_1 + 0x24) = bVar2 | *(byte *)(param_1 + 0x24);
        if ((bVar2 & 2) != 0) {
          *(short *)(param_1 + 0xc) = *(short *)(param_1 + 0xc) + 1;
        }
        if ((bVar2 & 4) != 0) {
          *(short *)(param_1 + 0xe) = *(short *)(param_1 + 0xe) + 1;
        }
        if ((bVar2 & 8) != 0) {
          *(short *)(param_1 + 0x10) = *(short *)(param_1 + 0x10) + 1;
        }
        bVar1 = uVar4 < *(uint *)(param_1 + 0x3c);
      }
      else {
        FUN_0000e868(*(int *)(param_1 + 0x14) + 0x1003);
        *(byte *)(param_1 + 0x24) = bVar2 | *(byte *)(param_1 + 0x24);
        if ((bVar2 & 2) != 0) {
          *(short *)(param_1 + 0xc) = *(short *)(param_1 + 0xc) + 1;
        }
        if ((bVar2 & 4) != 0) {
          *(short *)(param_1 + 0xe) = *(short *)(param_1 + 0xe) + 1;
        }
        if ((bVar2 & 8) != 0) {
          *(short *)(param_1 + 0x10) = *(short *)(param_1 + 0x10) + 1;
        }
        *(short *)(param_1 + 0x12) = *(short *)(param_1 + 0x12) + 1;
        bVar1 = uVar4 < *(uint *)(param_1 + 0x3c);
      }
    } while (bVar1);
  }
  *(uint *)(param_1 + 0x34) = *(int *)(param_1 + 0x34) + uVar4;
  *(uint *)(param_1 + 0x3c) = *(int *)(param_1 + 0x3c) - uVar4;
  *(short *)(param_1 + 10) = *(short *)(param_1 + 10) + (short)uVar4;
  return uVar4;
}

