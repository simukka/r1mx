/* 0x0037ac3c  FUN_0037ac3c  size=220 bytes */


undefined4 FUN_0037ac3c(uint param_1,int param_2,int *param_3)

{
  int iVar1;
  
  if (param_1 == 0x200000) {
    iVar1 = FUN_005b2190(param_2);
    if (iVar1 == 0) {
      *param_3 = *(int *)(param_2 + 0x94);
      return 0;
    }
  }
  else if (param_1 < 0x200001) {
    if (((param_1 == 0x40000) && (pcRam00e9c020 != reset_vector)) &&
       (iVar1 = (*pcRam00e9c020)(param_2), iVar1 != -1)) {
      *param_3 = param_2;
      return 0;
    }
  }
  else if (param_1 == 0x400000) {
    *param_3 = 0;
    return 0;
  }
  return 0xffffffff;
}

