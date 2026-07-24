/* 0x000f5eb4  FUN_000f5eb4  size=188 bytes */


void FUN_000f5eb4(undefined4 param_1,int param_2,int param_3,int param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  iVar2 = 0;
  iVar3 = 0;
  if (param_4 != 0) {
    uVar5 = param_4 + 1U >> 1;
    do {
      while( true ) {
        uVar4 = (uint)*(byte *)(param_3 + iVar3);
        bVar1 = *(byte *)(param_3 + iVar3 + 1);
        if (uVar4 < 0x41) break;
        uVar4 = (uVar4 & 0x4f) - 0x37 & 0xff;
        if (0x40 < bVar1) goto LAB_000f5ef0;
LAB_000f5f44:
        *(byte *)(param_2 + iVar2) = (byte)(uVar4 << 4) | bVar1 - 0x30;
        iVar3 = iVar3 + 2;
        iVar2 = iVar2 + 1;
        uVar5 = uVar5 - 1;
        if (uVar5 == 0) goto LAB_000f5f60;
      }
      uVar4 = uVar4 - 0x30 & 0xff;
      if (bVar1 < 0x41) goto LAB_000f5f44;
LAB_000f5ef0:
      *(byte *)(param_2 + iVar2) = (byte)(uVar4 << 4) | (bVar1 & 0x4f) - 0x37;
      iVar3 = iVar3 + 2;
      iVar2 = iVar2 + 1;
      uVar5 = uVar5 - 1;
    } while (uVar5 != 0);
  }
LAB_000f5f60:
  *(undefined1 *)(param_2 + iVar2) = 0;
  return;
}

