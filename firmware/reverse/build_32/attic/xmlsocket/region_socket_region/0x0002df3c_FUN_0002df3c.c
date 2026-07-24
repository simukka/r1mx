/* 0x0002df3c  FUN_0002df3c  size=112 bytes */


undefined4 FUN_0002df3c(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_005accf4(*(undefined4 *)(param_1 + 0x168),0xffffffff);
  uVar2 = 0xffffffff;
  if (iVar1 != -1) {
    *(undefined2 *)(param_2 + 0x36) = *(undefined2 *)(param_1 + 0x16c);
    *(undefined2 *)(param_1 + 0x16c) = *(undefined2 *)(param_2 + 0x34);
    FUN_005ad104(*(undefined4 *)(param_1 + 0x164));
    FUN_005ad104(*(undefined4 *)(param_1 + 0x168));
    uVar2 = 0;
  }
  return uVar2;
}

