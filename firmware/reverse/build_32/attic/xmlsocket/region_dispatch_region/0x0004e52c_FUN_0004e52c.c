/* 0x0004e52c  FUN_0004e52c  size=268 bytes */


undefined4 FUN_0004e52c(undefined4 param_1,undefined4 *param_2,undefined4 *param_3)

{
  int iVar1;
  undefined4 *puVar2;
  int aiStack_410 [4];
  undefined4 uStack_400;
  undefined4 uStack_3fc;
  
  *param_2 = 0;
  *param_3 = 0;
  iVar1 = FUN_0004e474(param_1,aiStack_410);
  if (iVar1 != 0) {
    puVar2 = (undefined4 *)FUN_00442914();
    FUN_0005e784(0,3,0x11,0xd3c31c,0x65d094,0x2b1,0xd3c37c,0x65d094,*puVar2,0x2b2);
    return 0xffffffff;
  }
  if (aiStack_410[0] != 0x5243414c) {
    return 0xffffffff;
  }
  *param_2 = uStack_400;
  *param_3 = uStack_3fc;
  return 0;
}

