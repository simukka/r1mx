/* 0x0006fd54  FUN_0006fd54  size=180 bytes */


void FUN_0006fd54(int param_1,int param_2)

{
  int iVar1;
  
  if (param_2 != 0) {
    iVar1 = FUN_0006f06c();
    if (iVar1 != 0) {
      FUN_005f3808(param_1 + 0xd8,0,0xffffffff);
      FUN_0005e784(3,0x20,6,0xd3e720,0x65dff0,0x528,0xd3f4a4,0x65e004);
    }
    FUN_0006acc0(param_1);
    return;
  }
  FUN_005f3808(param_1 + 0xd8,0,0xffffffff);
  return;
}

