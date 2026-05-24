/* 0x003970e8  FUN_003970e8  size=184 bytes */


int FUN_003970e8(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint auStack_18 [2];
  
  iVar1 = FUN_00396fdc(param_2,auStack_18);
  if (iVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = FUN_00398b98();
    if (iVar2 == 0) {
      iVar2 = 0;
    }
    else {
      iVar3 = FUN_0044f4cc(param_1,auStack_18[0],0x1b6);
      if (iVar3 < 0) {
        *(undefined2 *)(iVar2 + 0x18) = 0;
        FUN_00398c40(iVar2);
        iVar2 = 0;
      }
      else {
        *(short *)(iVar2 + 0x1a) = (short)iVar3;
        *(short *)(iVar2 + 0x18) = (short)iVar1;
        if ((auStack_18[0] & 8) != 0) {
          FUN_00398aac(iVar2,0,2);
        }
      }
    }
  }
  return iVar2;
}

