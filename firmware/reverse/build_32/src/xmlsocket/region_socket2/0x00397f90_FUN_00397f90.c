/* 0x00397f90  FUN_00397f90  size=224 bytes */


undefined1 * FUN_00397f90(undefined1 *param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  uint uVar3;
  byte *pbVar4;
  undefined1 *puVar5;
  int iVar6;
  
  puVar5 = param_1;
  while( true ) {
    piVar1 = (int *)FUN_00398df4();
    iVar6 = *(int *)(*piVar1 + 4);
    piVar1 = (int *)FUN_00398df4();
    if (*piVar1 != iVar6) break;
    piVar1 = (int *)FUN_00398df4();
    if (*(char *)(*piVar1 + 10) != 'f') break;
    piVar1 = (int *)FUN_00398df4();
    iVar6 = *(int *)(*piVar1 + 0x10) + -1;
    *(int *)(*piVar1 + 0x10) = iVar6;
    if (iVar6 < 0) {
      puVar2 = (undefined4 *)FUN_00398df4();
      uVar3 = FUN_00398758(*puVar2);
    }
    else {
      piVar1 = (int *)FUN_00398df4();
      pbVar4 = *(byte **)(*piVar1 + 0xc);
      *(byte **)(*piVar1 + 0xc) = pbVar4 + 1;
      uVar3 = (uint)*pbVar4;
    }
    if (uVar3 == 10) goto LAB_00398050;
    if (uVar3 == 0xffffffff) break;
    *puVar5 = (char)uVar3;
    puVar5 = puVar5 + 1;
  }
  if (puVar5 == param_1) {
    param_1 = (undefined1 *)0x0;
  }
  else {
LAB_00398050:
    *puVar5 = 0;
  }
  return param_1;
}

