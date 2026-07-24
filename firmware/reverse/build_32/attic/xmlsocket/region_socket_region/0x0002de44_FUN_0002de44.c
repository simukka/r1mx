/* 0x0002de44  FUN_0002de44  size=248 bytes */


int FUN_0002de44(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_005accf4(*(undefined4 *)(param_1 + 0x164),0xffffffff);
  iVar2 = 0;
  if (iVar1 != -1) {
    iVar1 = FUN_005accf4(*(undefined4 *)(param_1 + 0x168),0xffffffff);
    if (iVar1 == -1) {
      FUN_005ad104(*(undefined4 *)(param_1 + 0x164));
      iVar2 = 0;
    }
    else if (*(short *)(param_1 + 0x16c) == -1) {
      FUN_005ad104(*(undefined4 *)(param_1 + 0x164));
      FUN_005ad104(*(undefined4 *)(param_1 + 0x168));
      if (iRam00e1085c == 0) {
        iVar2 = 0;
      }
      else {
        FUN_00443f20(0xd37ae8,0,0,0,0,0,0);
        iVar2 = 0;
      }
    }
    else {
      iVar1 = (uint)*(ushort *)(param_1 + 0x16c) * 0x38 + param_1;
      iVar2 = iVar1 + 0x170;
      *(undefined2 *)(param_1 + 0x16c) = *(undefined2 *)(iVar1 + 0x1a6);
      FUN_005ad104(*(undefined4 *)(param_1 + 0x168));
    }
  }
  return iVar2;
}

