/* 0x000f63f0  FUN_000f63f0  size=272 bytes */


undefined4 FUN_000f63f0(int param_1,undefined4 param_2)

{
  int iVar1;
  uint uVar2;
  undefined1 auStack_170 [48];
  undefined1 auStack_140 [48];
  undefined1 auStack_110 [80];
  undefined1 auStack_c0 [160];
  
  iVar1 = FUN_0039a414();
  uVar2 = FUN_0039a414();
  uVar2 = iVar1 << 0x10 | uVar2;
  *(uint *)(param_1 + 0x68) = uVar2;
  FUN_003cada0(auStack_140,0x28,0xd5b2d0,uVar2);
  FUN_003cada0(auStack_170,0x28,0xd49de4);
  FUN_000f5e28(param_1,auStack_170,9,*(undefined4 *)(param_1 + 0x68));
  FUN_000f6200(param_1,auStack_110,auStack_170,9);
  iVar1 = FUN_003cada0(auStack_c0,0xa0,0xd49e68,auStack_110,auStack_140);
  FUN_001d9a58(100);
  FUN_000f6334(param_1,param_2,auStack_c0,iVar1 + 1,0);
  return 1;
}

