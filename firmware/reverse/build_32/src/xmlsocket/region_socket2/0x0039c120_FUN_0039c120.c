/* 0x0039c120  FUN_0039c120  size=308 bytes */


void FUN_0039c120(undefined1 *param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_0044259c(0x3ac817);
  if ((iVar1 == 0) || (iVar2 = FUN_0039ad64(iVar1,0x3ac816), iVar2 == 0)) {
    param_3 = param_3 + param_2 * 4;
    iVar1 = FUN_0039ad64(*(undefined4 *)(param_3 + 0xac),0x3ac816);
    if (iVar1 == 0) {
      *param_1 = 0;
    }
    else {
      FUN_0039af30(param_1,*(undefined4 *)(param_3 + 0xac));
    }
  }
  else {
    iVar2 = FUN_0039b228(iVar1,&LAB_003ac820);
    if (param_2 == 0) {
      FUN_0039af30(param_1,iVar1);
    }
    else {
      iVar1 = iVar2 + 1;
      iVar2 = FUN_0039b228(iVar1,&LAB_003ac820);
      if (param_2 == 1) {
        FUN_0039af30(param_1,iVar1);
      }
      else {
        iVar1 = iVar2 + 1;
        iVar2 = FUN_0039b228(iVar1,&LAB_003ac820);
        if (param_2 != 2) {
          return;
        }
        FUN_0039af30(param_1,iVar1);
        if (iVar2 == 0) {
          return;
        }
      }
    }
    param_1[iVar2 - iVar1] = 0;
  }
  return;
}

