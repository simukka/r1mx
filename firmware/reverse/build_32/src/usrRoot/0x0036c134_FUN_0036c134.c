/* 0x0036c134  FUN_0036c134  size=200 bytes */


void FUN_0036c134(int param_1,undefined4 param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 auStack_10 [3];
  
  uVar1 = 0;
  if (param_3 != 0) {
    uVar1 = *(undefined4 *)(param_3 + 0x44);
  }
  if (param_1 != 0) {
    auStack_10[0] = param_2;
    if (pcRam00e293d8 == reset_vector) {
      FUN_0039ac74(param_1,auStack_10,4);
    }
    else {
      iVar2 = (*pcRam00e293d8)(uVar1,auStack_10,param_1,4);
      if (iVar2 != 0) {
        return;
      }
    }
    if (pcRam00e2932c != reset_vector) {
      (*pcRam00e2932c)(param_1,4);
      return;
    }
  }
  return;
}

