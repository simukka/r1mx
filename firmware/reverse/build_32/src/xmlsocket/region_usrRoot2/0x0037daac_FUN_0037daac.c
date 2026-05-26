/* 0x0037daac  FUN_0037daac  size=296 bytes */


int * FUN_0037daac(void)

{
  code *pcVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  
  if (iRam00e9c0f4 == 0xe9c0f4) {
    if ((pcRam00e9c4b8 != reset_vector) && (iVar2 = (*pcRam00e9c4b8)(), iVar2 != 0)) {
      return (int *)0x0;
    }
    piVar3 = (int *)FUN_00459f78(1,0x30);
  }
  else {
    if ((pcRam00e9c4b8 == reset_vector) ||
       (iVar2 = (*pcRam00e9c4b8)(), pcVar1 = pcRam00e9c4b8, piVar3 = piRam00e9c0f8, iVar2 == 0)) {
      FUN_005b17d0();
      pcVar1 = pcRam00e9c4b8;
      piVar3 = piRam00e9c0f8;
      piVar4 = (int *)piRam00e9c0f8[1];
      *piVar4 = *piRam00e9c0f8;
      *(int **)(*piVar3 + 4) = piVar4;
    }
    else {
      piVar4 = (int *)piRam00e9c0f8[1];
      *piVar4 = *piRam00e9c0f8;
      *(int **)(*piVar3 + 4) = piVar4;
    }
    if ((pcVar1 == reset_vector) || (iVar2 = (*pcVar1)(), iVar2 == 0)) {
      FUN_005b1894();
    }
  }
  if (piVar3 != (int *)0x0) {
    iVar2 = iRam00e27088 + 1;
    piVar3[2] = iRam00e27088;
    iRam00e27088 = iVar2;
  }
  return piVar3;
}

