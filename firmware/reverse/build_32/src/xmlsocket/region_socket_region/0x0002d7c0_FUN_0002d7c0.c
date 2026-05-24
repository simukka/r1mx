/* 0x0002d7c0  FUN_0002d7c0  size=144 bytes */


undefined4 FUN_0002d7c0(int param_1)

{
  undefined4 *puVar1;
  
  if (iRam00e2942c < 1) {
    if ((param_1 != 0) && (*(int *)(param_1 + 0x20) == -0x205368dd)) {
      FUN_004514b4();
      return 0;
    }
    FUN_00442990(0x38000a);
  }
  else {
    puVar1 = (undefined4 *)FUN_00442914();
    *puVar1 = 0x430001;
  }
  return 0xffffffff;
}

