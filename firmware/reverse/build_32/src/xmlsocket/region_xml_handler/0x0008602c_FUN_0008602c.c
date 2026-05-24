/* 0x0008602c  FUN_0008602c  size=84 bytes */


void FUN_0008602c(undefined4 param_1,int param_2,int param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  if (0 < param_3) {
    do {
      while( true ) {
        iVar1 = iVar2 * 4;
        if (param_4 < *(uint *)(iVar1 + param_2)) break;
        iVar2 = iVar2 + 1;
        *(uint *)(iVar1 + param_2) = (*(uint *)(iVar1 + param_2) * 0x3c) / param_4;
        param_3 = param_3 + -1;
        if (param_3 == 0) {
          return;
        }
      }
      *(undefined4 *)(iVar1 + param_2) = 0x3c;
      iVar2 = iVar2 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}

