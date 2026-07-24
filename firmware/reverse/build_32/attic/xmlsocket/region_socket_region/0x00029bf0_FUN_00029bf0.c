/* 0x00029bf0  FUN_00029bf0  size=96 bytes */


void FUN_00029bf0(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0x14;
  iVar1 = 0;
  do {
    while ((*(byte *)((uint)*(byte *)(param_1 + 0x14 + iVar1) + iRam00e272d8) & 0x1f) == 0) {
      *(undefined1 *)(param_2 + iVar1) = 0x58;
      iVar1 = iVar1 + 1;
      iVar2 = iVar2 + -1;
      if (iVar2 == 0) goto LAB_00029c40;
    }
    *(undefined1 *)(param_2 + iVar1) = *(undefined1 *)(param_1 + 0x14 + iVar1);
    iVar1 = iVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
LAB_00029c40:
  *(undefined1 *)(param_2 + 0x14) = 0;
  return;
}

