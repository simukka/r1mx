/* 0x00033f0c  FUN_00033f0c  size=144 bytes */


void FUN_00033f0c(int param_1)

{
  if ((*(int *)(param_1 + 0xbc) != 0) && (*(int *)(param_1 + 0xc0) != 0)) {
    *(undefined4 *)(param_1 + 0xb0) = 0x45da4;
    *(undefined4 *)(param_1 + 0xb4) = 0x454ec;
    *(undefined4 *)(param_1 + 0xac) = 0x45a68;
    *(undefined4 *)(param_1 + 0xb8) = 0x4521c;
    *(undefined4 *)(*(int *)(param_1 + 0x30) + 0x44) = 0x45a68;
    *(undefined4 *)(*(int *)(param_1 + 0x30) + 0x48) = 0x44ee4;
    *(undefined4 *)(*(int *)(param_1 + 0x30) + 0x4c) = 0x4521c;
    *(undefined4 *)(*(int *)(param_1 + 0x2c) + 0x20) = 0x45a68;
    *(undefined4 *)(*(int *)(param_1 + 0x2c) + 0x24) = 0x4521c;
    *(undefined4 *)(param_1 + 0x130) = 0;
    *(undefined4 *)(param_1 + 0x134) = 0;
  }
  return;
}

