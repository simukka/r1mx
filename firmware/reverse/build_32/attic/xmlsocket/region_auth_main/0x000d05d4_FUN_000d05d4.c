/* 0x000d05d4  FUN_000d05d4  size=116 bytes */


undefined4 FUN_000d05d4(void)

{
  int unaff_r30;
  int unaff_r31;
  char cStack00000008;
  
  FUN_005f2a1c(0xd3bbcc,&stack0x00000008,0x1a,0x65f988);
  if (cStack00000008 == '\0') {
    *(undefined4 *)(unaff_r30 + 0x7c) = *(undefined4 *)(unaff_r31 + 0x14);
  }
  else {
    func_0x000cd6a4(unaff_r30,0xd459c0,*(undefined4 *)(unaff_r31 + 0x14));
    *(undefined4 *)(unaff_r30 + 0x7c) = *(undefined4 *)(unaff_r31 + 0x14);
  }
  return 1;
}

