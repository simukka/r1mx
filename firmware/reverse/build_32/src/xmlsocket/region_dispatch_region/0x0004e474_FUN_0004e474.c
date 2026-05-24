/* 0x0004e474  FUN_0004e474  size=184 bytes */


undefined4 FUN_0004e474(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 *puVar2;
  
  FUN_0039acec(param_2,0,0x400);
  iVar1 = FUN_0000d350(0xd3a900,param_2,0x400,0);
  if (iVar1 == 0) {
    return 0;
  }
  puVar2 = (undefined4 *)FUN_00442914();
  FUN_0005e784(0,3,0x11,0xd3c31c,0x65d088,0x44f,0xd3c348,0x65d088,*puVar2);
  return 0xffffffff;
}

