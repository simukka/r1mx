/* 0x000f7a4c  FUN_000f7a4c  size=332 bytes */


undefined4 FUN_000f7a4c(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_000f5f7c(param_1,param_2,*(undefined4 *)(param_1 + 0x68));
  iVar2 = param_1 + 0x28;
  if (iVar1 == 0) {
    FUN_000f5d98(param_1);
    iVar1 = param_1 + 0x28;
    if (0xf < *(uint *)(param_1 + 0x3c)) {
      iVar1 = *(int *)(param_1 + 0x28);
    }
    FUN_0005e784(0,3,0x1f,0xd49df8,0x661850,0x408,0xd49fd4,iVar1);
    return 0;
  }
  if (0xf < *(uint *)(param_1 + 0x3c)) {
    iVar2 = *(int *)(param_1 + 0x28);
  }
  FUN_0005e784(2,3,0x1f,0xd49df8,0x661850,0x3fe,0xd49fb4,iVar2);
  FUN_000f6ed0(param_1);
  iVar1 = param_1 + 0x28;
  if (0xf < *(uint *)(param_1 + 0x3c)) {
    iVar1 = *(int *)(param_1 + 0x28);
  }
  FUN_0005e784(2,3,0x1f,0xd49df8,0x661850,0x401,0xd49ff0,iVar1);
  return 3;
}

