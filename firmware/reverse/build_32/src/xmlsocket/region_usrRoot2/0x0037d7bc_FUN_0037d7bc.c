/* 0x0037d7bc  FUN_0037d7bc  size=192 bytes */


undefined4 FUN_0037d7bc(int param_1,int param_2)

{
  uint uVar1;
  int *piVar2;
  
  if (piRam00e9c5c0 != (int *)0xe9c5c0) {
    piVar2 = piRam00e9c5c0;
    do {
      if (piVar2[3] == param_1) {
        uVar1 = piVar2[7];
        if (((((uVar1 & 0x200000) != 0) && (piVar2[6] == param_2)) ||
            (((uVar1 >> 0x12 & 1) != 0 && (piVar2[6] == *(int *)(param_2 + 0x94))))) ||
           (((uVar1 >> 0x16 & 1 & (uint)(param_2 != -1)) != 0 ||
            ((uVar1 >> 0x17 & 1 & (uint)(param_2 == -1)) != 0)))) {
          return 0;
        }
      }
      piVar2 = (int *)*piVar2;
    } while (piVar2 != (int *)0xe9c5c0);
  }
  return 0xffffffff;
}

