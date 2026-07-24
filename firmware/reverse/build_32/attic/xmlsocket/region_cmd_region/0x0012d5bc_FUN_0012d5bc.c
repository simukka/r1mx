/* 0x0012d5bc  FUN_0012d5bc  size=224 bytes */


void FUN_0012d5bc(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_158 [256];
  undefined1 auStack_58 [48];
  undefined4 auStack_28 [4];
  
  auStack_28[0] = FUN_0039c824(0);
  FUN_0039b9a0(auStack_28,auStack_58);
  FUN_0039c808(auStack_158,0x100,0xd4c0f4,auStack_58);
  iVar1 = FUN_0044e334(param_2,0xd4c10c,0x16);
  *(int *)(param_1 + 40000) = *(int *)(param_1 + 40000) + iVar1;
  uVar2 = FUN_0039b0f0(auStack_158);
  iVar1 = FUN_0044e334(param_2,auStack_158,uVar2);
  *(int *)(param_1 + 40000) = *(int *)(param_1 + 40000) + iVar1;
  iVar1 = FUN_0044e334(param_2,0xd4c10c,0x16);
  *(int *)(param_1 + 40000) = *(int *)(param_1 + 40000) + iVar1;
  return;
}

