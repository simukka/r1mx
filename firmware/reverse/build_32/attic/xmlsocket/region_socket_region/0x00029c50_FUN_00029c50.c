/* 0x00029c50  FUN_00029c50  size=360 bytes */


undefined8 FUN_00029c50(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  if ((*(ushort *)(param_1 + 0xac) & 0x400) == 0) {
    if ((*(ushort *)(param_1 + 0x62) & 0x200) == 0) {
      uVar2 = (*(short *)(param_1 + 2) + -1) * (int)*(short *)(param_1 + 6) *
              (int)*(short *)(param_1 + 0xc);
      uVar1 = (int)uVar2 >> 0x1f;
    }
    else {
      uVar1 = 0;
      uVar2 = CONCAT22(*(undefined2 *)(param_1 + 0x7a),*(undefined2 *)(param_1 + 0x78));
    }
  }
  else {
    uVar2 = CONCAT22(*(undefined2 *)(param_1 + 0xca),*(undefined2 *)(param_1 + 200)) |
            (uint)*(ushort *)(param_1 + 0xcc) << 0x18;
    uVar1 = (uint)(ushort)(*(ushort *)(param_1 + 0xcc) >> 8 | *(ushort *)(param_1 + 0xce));
  }
  return CONCAT44(uVar2,uVar1);
}

