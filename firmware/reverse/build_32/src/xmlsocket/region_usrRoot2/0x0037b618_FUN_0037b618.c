/* 0x0037b618  FUN_0037b618  size=180 bytes */


uint FUN_0037b618(int param_1)

{
  int iVar1;
  
  iVar1 = FUN_005b2190();
  if ((iVar1 == 0) && (iVar1 = FUN_005b0954(param_1), iVar1 != 0)) {
    FUN_005b17d0();
    iVar1 = FUN_0037d7bc(*(undefined4 *)(param_1 + 0x24c),param_1);
    if ((iVar1 == 0) || (iVar1 = FUN_0037d7bc(*(undefined4 *)(param_1 + 0x278),param_1), iVar1 == 0)
       ) {
      *(uint *)(param_1 + 0x268) = *(uint *)(param_1 + 0x268) | 2;
    }
    FUN_005b1894();
    iVar1 = FUN_005b13bc(param_1);
    return ~-(uint)(iVar1 == 0) & 0x505;
  }
  return 0x505;
}

