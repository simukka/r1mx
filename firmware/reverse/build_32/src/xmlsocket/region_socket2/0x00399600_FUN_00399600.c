/* 0x00399600  FUN_00399600  size=240 bytes */


undefined4 FUN_00399600(int param_1)

{
  ushort uVar1;
  undefined4 uVar2;
  
  uVar1 = *(ushort *)(param_1 + 0x18);
  if ((uVar1 & 8) == 0) {
    if ((uVar1 & 0x10) == 0) {
      return 0xffffffff;
    }
    if ((uVar1 & 4) != 0) {
      if (*(int *)(param_1 + 0x28) != 0) {
        if (param_1 + 0x38 != *(int *)(param_1 + 0x28)) {
          FUN_0045b580();
        }
        *(undefined4 *)(param_1 + 0x28) = 0;
      }
      *(undefined4 *)(param_1 + 0x10) = 0;
      *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) & 0xffdb;
      *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_1 + 0x1c);
    }
    *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) | 8;
  }
  if (*(int *)(param_1 + 0x1c) == 0) {
    FUN_003980b8(param_1);
  }
  if ((*(ushort *)(param_1 + 0x18) & 1) == 0) {
    if ((*(ushort *)(param_1 + 0x18) & 2) == 0) {
      uVar2 = *(undefined4 *)(param_1 + 0x20);
    }
    else {
      uVar2 = 0;
    }
    *(undefined4 *)(param_1 + 0x14) = uVar2;
  }
  else {
    *(undefined4 *)(param_1 + 0x14) = 0;
    *(int *)(param_1 + 0x24) = -*(int *)(param_1 + 0x20);
  }
  return 0;
}

