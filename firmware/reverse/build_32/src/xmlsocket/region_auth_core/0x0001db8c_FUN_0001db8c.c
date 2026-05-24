/* 0x0001db8c  FUN_0001db8c  size=176 bytes */


undefined4 FUN_0001db8c(int param_1)

{
  undefined4 uVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = param_1 + 0x1007;
  uVar1 = FUN_0000e868(iVar4);
  iVar5 = param_1 + 0x100f;
  FUN_0000e8d8(iVar4,0);
  uVar2 = FUN_0000e868(iVar5);
  FUN_0000e8d8(iVar5,(uVar2 | 0xffffff80) & 0xff);
  uVar3 = FUN_0000e868(param_1 + 0x100b);
  FUN_0000e8d8(iVar5,uVar2);
  FUN_0000e8d8(iVar4,uVar1);
  return uVar3;
}

