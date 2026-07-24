/* 0x0012d53c  FUN_0012d53c  size=128 bytes */


void FUN_0012d53c(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_118 [260];
  
  FUN_003cada0(auStack_118,0x100,0xd4c0d4,param_3);
  uVar1 = FUN_0039b0f0(auStack_118);
  iVar2 = FUN_0044e334(param_2,auStack_118,uVar1);
  *(int *)(param_1 + 40000) = *(int *)(param_1 + 40000) + iVar2;
  return;
}

