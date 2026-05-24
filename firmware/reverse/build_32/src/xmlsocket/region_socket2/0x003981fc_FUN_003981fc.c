/* 0x003981fc  FUN_003981fc  size=120 bytes */


void FUN_003981fc(char *param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  
  if ((param_1 != (char *)0x0) && (*param_1 != '\0')) {
    puVar1 = (undefined4 *)FUN_00398e8c();
    FUN_0039995c(*puVar1,0x3a8274,param_1);
  }
  puVar1 = (undefined4 *)FUN_00442914();
  uVar2 = FUN_0039b0a8(*puVar1);
  puVar1 = (undefined4 *)FUN_00398e8c();
  FUN_0039995c(*puVar1,0x3a8279,uVar2);
  return;
}

