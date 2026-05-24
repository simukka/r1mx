/* 0x0001d15c  FUN_0001d15c  size=68 bytes */


ushort * FUN_0001d15c(uint param_1)

{
  ushort *puVar1;
  int iVar2;
  
  puVar1 = (ushort *)0xe10600;
  iVar2 = 0;
  do {
    iVar2 = iVar2 + 1;
    if (*puVar1 == param_1) {
      return puVar1;
    }
    puVar1 = puVar1 + 8;
  } while (iVar2 < 2);
  return (ushort *)0x0;
}

