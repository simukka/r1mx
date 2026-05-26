/* 0x005b1a30  FUN_005b1a30_usrAppInit  size=344 bytes */


undefined4 FUN_005b1a30(void)

{
  int iVar1;
  
  iVar1 = iRam00e9c3e0;
  if (*(int *)(iRam00e9c3e0 + 0x7c) != 0) {
    *(int *)(iRam00e9c3e0 + 0x7c) = *(int *)(iRam00e9c3e0 + 0x7c) + -1;
  }
  if (iRam00e29390 != 0) {
    if ((uRam00e9c3d0 & 0x10000001) == 0x10000001) {
      (*pcRam00e9c184)(0x3a);
    }
    if ((uRam00e9bffc & 0x10000001) == 0x10000001) {
      (*pcRam00e9bf80)(0x3a,0,0,0,0,0,0,0);
    }
    if (iRam00e29390 != 0) {
      if ((uRam00e9c3d0 & 0x10000003) == 0x10000003) {
        (*pcRam00e9c060)(0x26b,iVar1);
      }
      if ((uRam00e9bffc & 0x10000010) == 0x10000010) {
        (*pcRam00e9bf80)(0x26b,1,0,iVar1,0,0,0,0);
      }
    }
  }
  return 0;
}

