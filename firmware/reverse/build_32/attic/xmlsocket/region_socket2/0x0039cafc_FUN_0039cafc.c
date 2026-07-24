/* 0x0039cafc  FUN_0039cafc  size=164 bytes */


int FUN_0039cafc(int *param_1)

{
  int iVar1;
  int *piVar2;
  int iStack_8;
  
  iVar1 = FUN_003bce18(&iStack_8,*param_1,param_1[1]);
  if (iVar1 == 0) {
    *(int *)(iStack_8 + 8) = param_1[2];
    *(int *)(iStack_8 + 0xc) = param_1[3];
    *(int *)(iStack_8 + 0x10) = param_1[4];
    *(int *)(iStack_8 + 0x14) = param_1[5];
    *(int *)(iStack_8 + 0x18) = param_1[6];
    iVar1 = *(int *)(*param_1 * 0xc + 0xe27598);
    if (iVar1 != 0) {
      piVar2 = (int *)(iStack_8 + 0x18);
      param_1 = param_1 + 6;
      do {
        param_1 = param_1 + 1;
        piVar2 = piVar2 + 1;
        *piVar2 = *param_1;
        iVar1 = iVar1 + -1;
      } while (iVar1 != 0);
    }
  }
  return iStack_8;
}

