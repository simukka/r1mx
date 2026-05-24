/* 0x00396930  FUN_00396930  size=20 bytes */


byte FUN_00396930(int param_1)

{
  return *(byte *)(iRam00e272d8 + param_1) & 0x1f;
}

