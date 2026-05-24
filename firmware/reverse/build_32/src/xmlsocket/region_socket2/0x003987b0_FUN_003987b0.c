/* 0x003987b0  FUN_003987b0  size=84 bytes */


void FUN_003987b0(int param_1,int param_2)

{
  undefined4 uVar1;
  
  if ((*(int *)(param_1 + 4) == param_1) && (*(char *)(param_1 + 10) == 'f')) {
    if (param_2 == 0) {
      uVar1 = 2;
    }
    else {
      uVar1 = 0;
    }
    FUN_003988b0(param_1,param_2,uVar1,0x400);
  }
  return;
}

