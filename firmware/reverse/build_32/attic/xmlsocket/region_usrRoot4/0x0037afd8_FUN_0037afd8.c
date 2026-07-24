/* 0x0037afd8  FUN_0037afd8  size=204 bytes */


undefined4 FUN_0037afd8(void)

{
  if (iRam00e27070 != 0) {
    return 0;
  }
  FUN_0037d660();
  FUN_005bb0cc();
  if (iRam00e27074 == 0) {
    FUN_0044b204(0x38be04);
    FUN_0044b408(0x38b940);
    FUN_005b0744(0x38c528);
    iRam00e27074 = 1;
  }
  iRam00e27070 = 1;
  puRam00e9c490 = &LAB_0038ad18;
  uRam00e27080 = 0x38bf78;
  return 0;
}

