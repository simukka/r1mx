/* 0x000344d4  FUN_000344d4  size=256 bytes */


void FUN_000344d4(int param_1,int param_2)

{
  int extraout_r4;
  int iVar1;
  
  if ((*(int *)(param_1 + 0xd8) != 0) &&
     ((*(int *)(param_2 + 8) != -1 || (*(int *)(param_2 + 0xc) != -1)))) {
    FUN_003cd848(*(undefined4 *)(param_2 + 8),*(undefined4 *)(param_2 + 0xc),0,
                 *(undefined4 *)(param_1 + 0xd8));
    iVar1 = *(int *)(extraout_r4 * 4 + *(int *)(param_1 + 0xd4));
    if (iVar1 == 0) {
      *(undefined4 *)(param_2 + 8) = 0xffffffff;
      *(undefined4 *)(param_2 + 0xc) = 0xffffffff;
      *(undefined4 *)(param_2 + 0x18) = 0;
      *(undefined4 *)(param_2 + 0x14) = 0;
      return;
    }
    if (iVar1 == param_2) {
      *(undefined4 *)(extraout_r4 * 4 + *(int *)(param_1 + 0xd4)) = *(undefined4 *)(param_2 + 0x14);
    }
    else {
      do {
        if (*(int *)(iVar1 + 0x14) == param_2) {
          *(undefined4 *)(iVar1 + 0x14) = *(undefined4 *)(param_2 + 0x14);
          break;
        }
        iVar1 = *(int *)(iVar1 + 0x14);
      } while (iVar1 != 0);
    }
  }
  *(undefined4 *)(param_2 + 8) = 0xffffffff;
  *(undefined4 *)(param_2 + 0xc) = 0xffffffff;
  *(undefined4 *)(param_2 + 0x18) = 0;
  *(undefined4 *)(param_2 + 0x14) = 0;
  return;
}

