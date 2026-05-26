/* 0x0037cbd4  FUN_0037cbd4  size=192B */


int FUN_0037cbd4(undefined4 param_1,int *param_2)

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
        pcVar3 = *(code **)(iVar4 + 8);
        iVar1 = 0x50d;
        if (pcVar3 != reset_vector) {
          uVar2 = 0;
          if (0 < param_2[1]) {
            uVar2 = *(undefined4 *)param_2[2];
          }
          iVar1 = (*pcVar3)(uVar2);
        }
      }
      return iVar1;
    }
    iVar1 = 0;
    uRam00e3a72c = 0;
  }
  return iVar1;
}

