/* 0x00396980  FUN_00396980  size=20 bytes */


byte FUN_00396980(int param_1)

{
  return *(byte *)(iRam00e272d8 + param_1) & 0x40;
}

