/* 0x0001e6fc  FUN_0001e6fc  size=212 bytes */


int FUN_0001e6fc(int param_1)

{
  ushort uVar2;
  int iVar1;
  int iVar3;
  
  iVar3 = param_1 + 0x24;
  if (param_1 == 0) {
    FUN_0000e4e0(0xd34ed8,0xdb);
    uRam00e9c0ec = 1;
    return 0;
  }
  uRam00e9c0ec = 0;
  uVar2 = FUN_0001dc3c(iVar3);
  iVar1 = FUN_0001dd8c(iVar3,uVar2 | 0x100);
  if (iVar1 != 0) {
    return iVar1;
  }
  FUN_00443634(*(undefined4 *)(param_1 + 0x20),0x2d6e0,iVar3);
  FUN_0036fb08(*(undefined4 *)(param_1 + 0x20));
  return 0;
}

