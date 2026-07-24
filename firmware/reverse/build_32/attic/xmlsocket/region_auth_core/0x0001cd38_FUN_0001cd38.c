/* 0x0001cd38  FUN_0001cd38  size=312 bytes */


undefined4 FUN_0001cd38(int param_1,int param_2,int param_3)

{
  uint uVar1;
  undefined4 uVar2;
  
  if (param_1 == 0) {
    FUN_0000e4e0(0xd34c58,0xf4);
  }
  else {
    uVar2 = 0xf5;
    if (param_2 != 0) {
      uVar2 = 0xf6;
      if ((*(int *)(param_1 + 0x1c) == 0x11111111) && (uVar2 = 0xf7, -1 < param_3)) {
        uRam00e9c0ec = 0;
        uVar1 = FUN_0000e868(*(int *)(param_1 + 0x14) + 0x1007,0xf7);
        FUN_0000e8d8(*(int *)(param_1 + 0x14) + 0x1007,uVar1 & 0xfd);
        *(int *)(param_1 + 0x2c) = param_3;
        *(int *)(param_1 + 0x30) = param_3;
        *(int *)(param_1 + 0x28) = param_2;
        uVar2 = FUN_0001cbac(param_1);
        return uVar2;
      }
    }
    uRam00e9c0ec = 0;
    FUN_0000e4e0(0xd34c58,uVar2);
  }
  uRam00e9c0ec = 1;
  return 0;
}

