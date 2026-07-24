/* 0x00074b20  FUN_00074b20  size=296 bytes */


void FUN_00074b20(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  param_2 = param_2 * 0x10;
  iVar1 = FUN_0044f4cc(*(undefined4 *)(param_2 + 0xe10c60),2,0);
  *(int *)(param_1 + 0x48) = iVar1;
  iVar2 = param_1 + 0x28;
  if (iVar1 != -1) {
    FUN_0005e784(2,3,0xc,0xd3f794,0x65e17c,0x5c5,0xd3f868,*(undefined4 *)(param_2 + 0xe10c60),iVar1)
    ;
    *(undefined4 *)(param_1 + 0x44) = *(undefined4 *)(param_2 + 0xe10c60);
    FUN_0021a460(*(undefined4 *)(param_1 + 0x48));
    *(undefined1 *)(param_2 + 0xe10c6c) = 1;
    return;
  }
  if (0xf < *(uint *)(param_1 + 0x3c)) {
    iVar2 = *(int *)(param_1 + 0x28);
  }
  FUN_0005e784(0,3,5,0xd3f794,0x65e17c,0x5bf,0xd3f87c,iVar2,*(undefined4 *)(param_2 + 0xe10c60));
  return;
}

