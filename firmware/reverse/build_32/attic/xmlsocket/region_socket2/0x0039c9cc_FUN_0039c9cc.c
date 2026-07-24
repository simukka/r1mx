/* 0x0039c9cc  FUN_0039c9cc  size=152 bytes */


uint FUN_0039c9cc(void)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = puRam00e9c6a4;
  uVar2 = 0;
  uVar3 = *puRam00e9c6a4;
  if (uVar3 != 0) {
    do {
      if (*(int *)(puRam00e9c6a4[1] + uVar2 * 4) == 0) break;
      uVar2 = uVar2 + 1;
    } while (uVar2 < uVar3);
  }
  if (uVar3 == uVar2) {
    uVar2 = FUN_0039f264(puRam00e9c6a4[1],uVar3 * 4 + 4);
    puVar1[1] = uVar2;
    uVar2 = *puRam00e9c6a4;
    *puRam00e9c6a4 = uVar2 + 1;
  }
  return uVar2;
}

