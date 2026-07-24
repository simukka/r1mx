/* 0x00398a48  FUN_00398a48  size=100 bytes */


void FUN_00398a48(int param_1,undefined4 param_2,undefined4 param_3)

{
  if ((*(ushort *)(param_1 + 0x18) & 0x100) != 0) {
    FUN_0044e6d0((int)*(short *)(param_1 + 0x1a),0,2);
  }
  *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) & 0xefff;
  FUN_0044e334((int)*(short *)(param_1 + 0x1a),param_2,param_3);
  return;
}

