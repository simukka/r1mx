/* 0x0037b0a4  FUN_0037b0a4  size=320 bytes */


int * FUN_0037b0a4(int param_1,int param_2,int param_3,uint param_4,int param_5,uint param_6,
                  int param_7,int param_8)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  
  iVar1 = FUN_0037afd8();
  piVar3 = (int *)0x0;
  if (iVar1 == 0) {
    piVar2 = (int *)FUN_0037daac(0);
    iVar1 = iRam00e9c3e0;
    piVar3 = (int *)0x0;
    if (piVar2 != (int *)0x0) {
      piVar2[6] = param_3;
      piVar2[3] = param_1;
      piVar2[8] = param_5;
      piVar2[5] = iVar1;
      piVar2[7] = param_4;
      piVar2[9] = param_6;
      if ((param_6 & 1) != 0) {
        piVar2[10] = param_7;
        piVar2[0xb] = param_8;
      }
      if ((param_4 & 0x10) == 0) {
        piVar2[4] = param_2;
      }
      FUN_005b17d0(0);
      *piVar2 = (int)piRam00e9c5c0;
      piRam00e9c5c0 = piVar2;
      piVar2[1] = 0xe9c5c0;
      *(int **)(*piVar2 + 4) = piVar2;
      FUN_005b1894();
      piVar3 = piVar2;
      if ((pcRam00e9c5f8 != reset_vector) && ((piVar2[7] & 0x40000000U) == 0)) {
        (*pcRam00e9c5f8)(0x10,piVar2);
      }
    }
  }
  return piVar3;
}

