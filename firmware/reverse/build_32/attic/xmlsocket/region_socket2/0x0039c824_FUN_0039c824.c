/* 0x0039c824  FUN_0039c824  size=88 bytes */


undefined4 FUN_0039c824(undefined4 *param_1)

{
  int iVar1;
  undefined4 auStack_18 [5];
  
  iVar1 = FUN_0043cf80(0,auStack_18);
  if (iVar1 == 0) {
    if (param_1 != (undefined4 *)0x0) {
      *param_1 = auStack_18[0];
    }
  }
  else {
    auStack_18[0] = 0xffffffff;
  }
  return auStack_18[0];
}

