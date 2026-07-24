/* 0x00037e40  FUN_00037e40  size=256 bytes */


undefined4 FUN_00037e40(int *param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  
  iVar3 = *param_1;
  iVar7 = *(int *)(iVar3 + 0x30);
  uVar6 = *(uint *)(iVar7 + 0x60);
  if (uVar6 == 0xffffffff) {
    uVar6 = 0;
    uVar4 = 2;
    if (2 < *(uint *)(iVar7 + 0x5c)) {
      do {
        uVar5 = uVar4 + 1;
        iVar2 = (**(code **)(iVar7 + 0x34))(param_1,*(undefined1 *)(iVar7 + 0x54),uVar4);
        if ((iVar2 == 1) && (param_1[0xf] == 1)) {
          return 0xffffffff;
        }
        uVar6 = uVar6 + (*(int *)(iVar7 + 100) == iVar2);
        uVar4 = uVar5;
      } while (uVar5 < *(uint *)(iVar7 + 0x5c));
    }
    *(uint *)(iVar7 + 0x60) = uVar6;
  }
  uVar1 = FUN_003cc7cc((int)((ulonglong)uVar6 * (ulonglong)(uint)*(ushort *)(iVar3 + 0x5e) >> 0x20),
                       uVar6 * *(ushort *)(iVar3 + 0x5e),*(undefined1 *)(iVar3 + 0x84));
  return uVar1;
}

