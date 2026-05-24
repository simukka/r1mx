/* 0x003914dc  FUN_003914dc  size=176 bytes */


undefined4 FUN_003914dc(void)

{
  undefined4 uVar1;
  int *piVar2;
  undefined4 uStack_38;
  
  uVar1 = FUN_00245cd8(4);
  FUN_0064c4a4(uVar1);
  FUN_00247c78(uVar1,0xe0a148,0x64a150);
  piVar2 = (int *)FUN_002463b8();
  if ((undefined4 *)*piVar2 == (undefined4 *)0x0) {
    uStack_38 = 0;
  }
  else {
    uStack_38 = *(undefined4 *)*piVar2;
  }
  return uStack_38;
}

