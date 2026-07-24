/* 0x003988b0  FUN_003988b0  size=308 bytes */


undefined4 FUN_003988b0(int param_1,undefined4 param_2,int param_3,int param_4)

{
  ushort uVar1;
  int iVar2;
  
  if ((*(int *)(param_1 + 4) != param_1) || (*(char *)(param_1 + 10) != 'f')) {
    return 0xffffffff;
  }
  if ((((param_3 != 0) && (param_3 != 1)) && (param_3 != 2)) || (param_4 < 0)) {
    return 0xffffffff;
  }
  FUN_00396c70(param_1);
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined4 *)(param_1 + 0x24) = 0;
  if ((*(ushort *)(param_1 + 0x18) & 0x80) != 0) {
    FUN_0045b580(*(undefined4 *)(param_1 + 0x1c));
  }
  uVar1 = *(ushort *)(param_1 + 0x18) & 0xff7c;
  *(ushort *)(param_1 + 0x18) = uVar1;
  if (param_3 == 0) {
LAB_003989a0:
    *(undefined4 *)(param_1 + 0xc) = param_2;
    *(undefined4 *)(param_1 + 0x1c) = param_2;
    iVar2 = param_4;
  }
  else {
    if (param_3 == 1) {
      uVar1 = uVar1 | 1;
      *(ushort *)(param_1 + 0x18) = uVar1;
      *(int *)(param_1 + 0x24) = -param_4;
      goto LAB_003989a0;
    }
    if (param_3 != 2) goto LAB_003989b0;
    uVar1 = uVar1 | 2;
    *(ushort *)(param_1 + 0x18) = uVar1;
    *(int *)(param_1 + 0xc) = param_1 + 0x3b;
    *(int *)(param_1 + 0x1c) = param_1 + 0x3b;
    iVar2 = 1;
  }
  *(int *)(param_1 + 0x20) = iVar2;
LAB_003989b0:
  if ((uVar1 & 8) != 0) {
    if ((uVar1 & 3) != 0) {
      param_4 = 0;
    }
    *(int *)(param_1 + 0x14) = param_4;
  }
  return 0;
}

