/* 0x0039e678  FUN_0039e678  size=208 bytes */


void FUN_0039e678(undefined4 param_1,int *param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 auStack_20 [3];
  
  FUN_0039cd58(0x3b9400,&uStack_24);
  iVar1 = FUN_003bd1a8(&uStack_28,uStack_24,1,0);
  if (iVar1 == 0) {
    iVar1 = *param_2;
    while (iVar1 != 0) {
      uVar2 = (*(code *)*param_2)();
      FUN_003bd41c(uStack_28,uVar2,0x14);
      param_2 = param_2 + 1;
      iVar1 = *param_2;
    }
    uVar2 = FUN_0039b0f0(param_1);
    FUN_003bd41c(uStack_28,param_1,uVar2);
    auStack_20[0] = 0x14;
    FUN_003bd894(uStack_28,param_3,auStack_20);
    FUN_003bd274(uStack_28);
  }
  return;
}

