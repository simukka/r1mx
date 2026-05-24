/* 0x0039ca64  FUN_0039ca64  size=152 bytes */


undefined4 FUN_0039ca64(undefined4 *param_1,uint *param_2)

{
  int iVar1;
  undefined4 *puVar2;
  uint uVar3;
  
  uVar3 = 0;
  if (*puRam00e9c6a4 != 0) {
    do {
      puVar2 = *(undefined4 **)(puRam00e9c6a4[1] + uVar3 * 4);
      if ((puVar2 != (undefined4 *)0x0) && (iVar1 = FUN_0039ad64(*puVar2,*param_1), iVar1 == 0)) {
        *param_2 = uVar3;
        return 1;
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < *puRam00e9c6a4);
  }
  return 0;
}

