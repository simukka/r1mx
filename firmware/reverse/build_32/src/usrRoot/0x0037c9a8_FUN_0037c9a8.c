/* 0x0037c9a8  FUN_0037c9a8  size=284B */


int FUN_0037c9a8(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  code *pcVar3;
  int iVar4;
  
  iVar4 = *param_2;
  iVar1 = FUN_0037c964(iVar4);
  if (iVar1 == 0) {
    if (iVar4 != 0) {
      iVar4 = *(int *)(iVar4 * 4 + 0x108e678);
      iVar1 = 0x514;
      if (iVar4 != 0) {
        pcVar3 = *(code **)(iVar4 + 4);
        iVar1 = 0x50d;
        if (pcVar3 != reset_vector) {
          uVar2 = 0;
          if (0 < param_2[1]) {
            uVar2 = *(undefined4 *)param_2[2];
          }
          iVar1 = (*pcVar3)(uVar2,param_2[3],param_2[4]);
        }
      }
      return iVar1;
    }
    if ((param_2[3] == 0) && (param_2[4] == 0)) {
      uRam00fbfa7c = 1;
    }
    else {
      iRam00fbfa84 = param_2[4];
      iRam00fbfa80 = param_2[3];
      uRam00fbfa7c = 4;
    }
    iVar1 = 0;
    uRam00e3a72c = 1;
  }
  return iVar1;
}

