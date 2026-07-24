/* 0x005f0b34  FUN_005f0b34  size=420 bytes */


/* WARNING: Removing unreachable block (ram,0x005f0b84) */
/* WARNING: Removing unreachable block (ram,0x005f0cd0) */

int FUN_005f0b34(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  *(undefined1 *)(param_1 + 4) = 0;
  *(undefined4 *)(param_1 + 0x14) = 0;
  iVar5 = *(int *)(param_2 + 0x38);
  *(undefined4 *)(param_1 + 0x18) = 0xf;
  iVar4 = param_1 + 4;
  if (param_1 == param_2 + 0x24) {
    iVar2 = *(int *)(param_1 + 0x14) - iVar5;
    iVar1 = -1;
    if ((iVar2 == -1) || (iVar1 = iVar2, iVar2 != 0)) {
      iVar2 = iVar4;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        iVar2 = *(int *)(param_1 + 4);
      }
      iVar3 = iVar4;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        iVar3 = *(int *)(param_1 + 4);
      }
      FUN_0039acb0(iVar2 + iVar5,iVar3 + iVar5 + iVar1,(*(int *)(param_1 + 0x14) - iVar5) - iVar1);
      iVar1 = *(int *)(param_1 + 0x14) - iVar1;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        iVar4 = *(int *)(param_1 + 4);
      }
      *(int *)(param_1 + 0x14) = iVar1;
      *(undefined1 *)(iVar4 + iVar1) = 0;
      return param_1;
    }
  }
  else {
    iVar1 = FUN_005f0030(param_1,iVar5,0);
    if (iVar1 != 0) {
      iVar1 = iVar4;
      if (0xf < *(uint *)(param_1 + 0x18)) {
        iVar1 = *(int *)(param_1 + 4);
      }
      iVar2 = param_2 + 0x28;
      if (0xf < *(uint *)(param_2 + 0x3c)) {
        iVar2 = *(int *)(param_2 + 0x28);
      }
      FUN_0039ac74(iVar1,iVar2,iVar5);
      if (0xf < *(uint *)(param_1 + 0x18)) {
        iVar4 = *(int *)(param_1 + 4);
      }
      *(int *)(param_1 + 0x14) = iVar5;
      *(undefined1 *)(iVar4 + iVar5) = 0;
    }
  }
  return param_1;
}

