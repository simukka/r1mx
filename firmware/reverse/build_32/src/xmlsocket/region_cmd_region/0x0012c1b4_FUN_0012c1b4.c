/* 0x0012c1b4  FUN_0012c1b4  size=88 bytes */


void FUN_0012c1b4(undefined4 param_1,int param_2)

{
  int iVar1;
  
  FUN_0012bfb0();
  for (iVar1 = *(int *)(param_2 + 0x18); iVar1 != 0; iVar1 = *(int *)(iVar1 + 0x40)) {
    FUN_0012c1b4(param_1,iVar1);
  }
  return;
}

