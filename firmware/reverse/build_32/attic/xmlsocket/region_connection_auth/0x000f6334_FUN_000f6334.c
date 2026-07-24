/* 0x000f6334  FUN_000f6334  size=188 bytes */


void FUN_000f6334(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = FUN_0039b0f0(param_3);
  iVar1 = FUN_00359c78(0,param_3,iVar1 + 1);
  iVar3 = param_1 + 0x28;
  if (-1 < iVar1) {
    return;
  }
  if (0xf < *(uint *)(param_1 + 0x3c)) {
    iVar3 = *(int *)(param_1 + 0x28);
  }
  uVar2 = FUN_00442920();
  FUN_0005e784(0,3,8,0xd49df8,0x661678,0x54e,0xd49e44,iVar3,uVar2);
  return;
}

