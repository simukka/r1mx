/* 0x0037dfc8  FUN_0037dfc8  size=224 bytes */


void FUN_0037dfc8(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  puRam0108e684 = (undefined4 *)FUN_00459f78(1,0x10);
  if (puRam0108e684 != (undefined4 *)0x0) {
    puVar2 = (undefined4 *)FUN_00459f78(1,0x10);
    puVar1 = puRam0108e684;
    puRam0108e688 = puVar2;
    if (puVar2 != (undefined4 *)0x0) {
      uRam00e27068 = 0x38e0a8;
      puRam0108e684[2] = 0x38b6cc;
      puVar1[1] = &LAB_0038b740;
      puVar1[3] = 0x38b618;
      *puVar1 = 0x38e36c;
      *puVar2 = 0x38e36c;
      FUN_0037d660();
      uRam00fbfaf4 = 0xfbfaf0;
      uRam00fbfaf0 = 0xfbfaf0;
      FUN_0059b19c(0xfbfad8,0x38e1f8,0x38e330,0xfbfad8);
    }
  }
  return;
}

