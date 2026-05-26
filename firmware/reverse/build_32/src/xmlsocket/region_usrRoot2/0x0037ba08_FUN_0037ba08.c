/* 0x0037ba08  FUN_0037ba08  size=268 bytes */


int FUN_0037ba08(int param_1,int param_2)

{
  bool bVar1;
  int iVar2;
  
  if (((pcRam00e9c578 == reset_vector) || (pcRam00e9c020 == reset_vector || param_2 == 0)) ||
     (param_2 == iRam00e3a790)) {
    return param_1;
  }
  if (param_1 != param_2) {
    if (iRam00e9c05c == 1) {
      iVar2 = (*pcRam00e9c020)(param_2);
      if (iVar2 == -1) {
        return param_1;
      }
      if ((*(uint *)(param_2 + 100) & 4) != 0) {
        return param_1;
      }
      if (pcRam00e29404 == reset_vector) {
        return param_2;
      }
      iVar2 = (*pcRam00e29404)(*(undefined4 *)(param_2 + 0x44));
      bVar1 = iVar2 == -1;
    }
    else {
      iVar2 = (*pcRam00e9c578)(param_2,0);
      bVar1 = iVar2 == 0;
    }
    if (bVar1) {
      return param_1;
    }
  }
  return param_2;
}

