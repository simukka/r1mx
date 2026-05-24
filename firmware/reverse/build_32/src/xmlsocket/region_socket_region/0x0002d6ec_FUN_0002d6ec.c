/* 0x0002d6ec  FUN_0002d6ec  size=212 bytes */


int FUN_0002d6ec(undefined4 param_1,undefined4 param_2)

{
  if (iRam00e10860 != -1) {
    return 0;
  }
  iRam00e10860 = FUN_0044fd5c(0x408b0,0x4083c,0x3fd30,0x3c680,0x3d3f0,0x40d14,0x3ed80);
  uRam00e9e55c = param_1;
  uRam00e9e560 = param_2;
  return -(uint)(iRam00e10860 == -1);
}

