/* 0x00034758  FUN_00034758  size=220 bytes */


undefined4
FUN_00034758(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5,
            undefined4 param_6)

{
  int iVar1;
  undefined4 uVar2;
  
  FUN_00031fa4(param_1,0xcb100030,0);
  *(undefined4 *)(param_2 + 8) = param_3;
  *(undefined4 *)(param_2 + 0xc) = param_4;
  *(undefined4 *)(param_2 + 0x10) = param_5;
  *(undefined4 *)(param_2 + 0x20) = param_6;
  *(undefined4 *)(param_2 + 0x24) = 0x44734;
  *(undefined4 *)(param_2 + 0x28) = *(undefined4 *)(param_2 + 0x30);
  *(undefined4 *)(param_2 + 0x2c) = 0;
  *(undefined4 *)(param_2 + 0x1c) = 0;
  *(undefined4 *)(param_2 + 0x18) = 0;
  FUN_005b80c8(*(undefined4 *)(param_1 + 0x28),param_2);
  iVar1 = FUN_005accf4(*(undefined4 *)(param_2 + 0x28),0xffffffff);
  uVar2 = 0xffffffff;
  if ((iVar1 == 0) && (*(int *)(param_2 + 0x18) == 0)) {
    uVar2 = *(undefined4 *)(param_2 + 0x1c);
  }
  return uVar2;
}

