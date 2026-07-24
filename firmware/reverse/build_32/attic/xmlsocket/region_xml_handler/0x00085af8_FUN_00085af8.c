/* 0x00085af8  FUN_00085af8  size=208 bytes */


undefined4 FUN_00085af8(int param_1)

{
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 auStack_14 [4];
  
  if ((*(char *)(param_1 + 0x69) != '\0') && (*(int *)(param_1 + 0x4c) != 0)) {
    if (*(int *)(param_1 + 0x48) != 0) {
      FUN_000858b0(param_1,&uStack_20,&uStack_1c,&uStack_18,auStack_14);
      FUN_00130910(*(undefined4 *)(param_1 + 0x94),*(undefined4 *)(param_1 + 0x4c),
                   *(undefined4 *)(param_1 + 0x48),*(undefined4 *)(param_1 + 0x54),
                   *(undefined4 *)(param_1 + 0x50),uStack_20,uStack_1c,uStack_18,auStack_14[0]);
      if (*(int *)(param_1 + 0xa0) != 0) {
        FUN_001a8a64(*(int *)(param_1 + 0xa0),2,2,*(undefined4 *)(param_1 + 0x5c),0x3c8,0x31a,
                     *(undefined4 *)(param_1 + 0x54),0x32,*(undefined4 *)(param_1 + 0x54));
      }
    }
  }
  *(undefined1 *)(param_1 + 0x8a) = 0;
  return 1;
}

