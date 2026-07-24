/* 0x000869b4  FUN_000869b4  size=292 bytes */


void FUN_000869b4(int param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (param_3 == 4) {
    FUN_0013068c(*(undefined4 *)(param_1 + 0x90),*(undefined4 *)(param_1 + 0x58),0x76c00,0x500,0x40)
    ;
    iVar1 = 0x1db00;
    iVar3 = *(int *)(param_1 + 0x58);
    iVar2 = 0;
    do {
      *(undefined4 *)(iVar3 + iVar2 * 4) = 0xc0000000;
      iVar2 = iVar2 + 1;
      iVar1 = iVar1 + -1;
    } while (iVar1 != 0);
    *(undefined4 *)(param_1 + 0x8c) = 4;
  }
  else {
    if ((param_3 < 4) || (8 < param_3)) {
      return;
    }
    FUN_0013068c(*(undefined4 *)(param_1 + 0x90),*(undefined4 *)(param_1 + 0x60),0x16000,0x160,0x40)
    ;
    iVar3 = 0x5800;
    iVar2 = *(int *)(param_1 + 0x60);
    iVar1 = 0;
    do {
      *(undefined4 *)(iVar2 + iVar1 * 4) = 0xc0000000;
      iVar1 = iVar1 + 1;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    *(int *)(param_1 + 0x8c) = param_3;
  }
  FUN_0039acec(param_1 + 0x68e8,0,0x6800);
  FUN_0039acec(param_1 + 0xe8,0,0x6800);
  FUN_00086864(param_1);
  return;
}

