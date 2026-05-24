/* 0x0012d1ec  FUN_0012d1ec  size=368 bytes */


undefined4 FUN_0012d1ec(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined2 uStack_18;
  undefined1 uStack_16;
  
  memset(&uStack_20,0xb);
  iVar1 = FUN_0044f4cc(0xd4155c,0x601,0);
  if (-1 < iVar1) {
    iVar2 = FUN_0044e334();
    if (iVar2 != 0xd) {
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd4bfb0,0x662834);
    }
    *(undefined4 *)(param_1 + 40000) = 0x17;
    uStack_18 = 0;
    uStack_16 = 0;
    uStack_20 = 0;
    uStack_1c = 0;
    FUN_003cada0(&uStack_20,0xb,0xd4bfd4,9,0x17);
    uVar4 = FUN_0039b0f0(&uStack_20);
    iVar2 = FUN_0044e334(iVar1,&uStack_20,uVar4);
    iVar5 = FUN_0039b0f0(&uStack_20);
    if (iVar2 != iVar5) {
      puVar3 = (undefined4 *)FUN_00398e40();
      FUN_0039995c(*puVar3,0xd4bfdc,0x662834);
    }
    FUN_0044f9fc(iVar1);
    return 1;
  }
  puVar3 = (undefined4 *)FUN_00398e40(iVar1,0xd4bfa0,0xd);
  FUN_0039995c(*puVar3,0xd4bffc,0xd4155c);
  return 0;
}

