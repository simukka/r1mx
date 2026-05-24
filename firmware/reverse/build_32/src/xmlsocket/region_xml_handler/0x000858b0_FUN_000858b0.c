/* 0x000858b0  FUN_000858b0  size=584 bytes */


void FUN_000858b0(int param_1,uint *param_2,uint *param_3,uint *param_4,uint *param_5)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uStack_28;
  uint uStack_24;
  uint uStack_20;
  uint uStack_1c;
  
  FUN_00192348(&uStack_28);
  if (*(char *)(param_1 + 0x98) == '\0') {
    *param_2 = 0xffffffff;
    cVar1 = *(char *)(param_1 + 0x99);
  }
  else {
    uVar3 = *(uint *)(param_1 + 0x44);
    iVar4 = uStack_28 * ((int)uVar3 >> 0x1f) +
            (int)((ulonglong)uStack_28 * (ulonglong)uVar3 >> 0x20);
    cVar1 = *(char *)(param_1 + 0x99);
    uVar2 = (uint)(iVar4 >> 0x1f) >> 9;
    *param_2 = (iVar4 + (uint)CARRY4(uStack_28 * uVar3,uVar2)) * 0x200 |
               uStack_28 * uVar3 + uVar2 >> 0x17;
  }
  if (cVar1 == '\0') {
    *param_3 = 0xffffffff;
    cVar1 = *(char *)(param_1 + 0x9a);
  }
  else {
    uVar3 = *(uint *)(param_1 + 0x44);
    iVar4 = uStack_24 * ((int)uVar3 >> 0x1f) +
            (int)((ulonglong)uStack_24 * (ulonglong)uVar3 >> 0x20);
    cVar1 = *(char *)(param_1 + 0x9a);
    uVar2 = (uint)(iVar4 >> 0x1f) >> 9;
    *param_3 = (iVar4 + (uint)CARRY4(uStack_24 * uVar3,uVar2)) * 0x200 |
               uStack_24 * uVar3 + uVar2 >> 0x17;
  }
  if (cVar1 == '\0') {
    *param_4 = 0xffffffff;
    cVar1 = *(char *)(param_1 + 0x9b);
  }
  else {
    uVar3 = *(uint *)(param_1 + 0x44);
    iVar4 = uStack_20 * ((int)uVar3 >> 0x1f) +
            (int)((ulonglong)uStack_20 * (ulonglong)uVar3 >> 0x20);
    cVar1 = *(char *)(param_1 + 0x9b);
    uVar2 = (uint)(iVar4 >> 0x1f) >> 9;
    *param_4 = (iVar4 + (uint)CARRY4(uStack_20 * uVar3,uVar2)) * 0x200 |
               uStack_20 * uVar3 + uVar2 >> 0x17;
  }
  if (cVar1 == '\0') {
    *param_5 = 0xffffffff;
    return;
  }
  uVar3 = *(uint *)(param_1 + 0x44);
  iVar4 = uStack_1c * ((int)uVar3 >> 0x1f) + (int)((ulonglong)uStack_1c * (ulonglong)uVar3 >> 0x20);
  uVar2 = (uint)(iVar4 >> 0x1f) >> 9;
  *param_5 = (iVar4 + (uint)CARRY4(uStack_1c * uVar3,uVar2)) * 0x200 |
             uStack_1c * uVar3 + uVar2 >> 0x17;
  return;
}

