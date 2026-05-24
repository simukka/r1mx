/* 0x0039b0a4  thunk_FUN_0039afa8  size=4 bytes */


undefined4 thunk_FUN_0039afa8(int param_1,int param_2)

{
  undefined4 uStack_18;
  int iStack_14;
  undefined4 uStack_10;
  
  if (param_2 == 0) {
    return 0xffffffff;
  }
  if (param_1 == 0) {
    FUN_0039af30(param_2,0x3ab0e0);
  }
  else {
    if ((pcRam00e9c3f4 != reset_vector) && (iRam00e9c678 != 0)) {
      (*pcRam00e9c3f4)(iRam00e9c678,0,param_1,0,0,&uStack_18);
      (*pcRam00e9c0ac)(uStack_18,&uStack_10);
      (*pcRam00e9c21c)(uStack_18,&iStack_14);
      if (iStack_14 == param_1) {
        FUN_0039b1d4(param_2,uStack_10,0x100);
        return 0;
      }
    }
    FUN_003cae4c(param_2,0x3ab0e3,param_1);
  }
  return 0;
}

