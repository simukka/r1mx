/* 0x000363dc  FUN_000363dc  size=472 bytes */


undefined4 FUN_000363dc(int *param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  undefined1 uStack_28;
  undefined1 uStack_27;
  undefined1 uStack_26;
  undefined1 uStack_25;
  undefined1 uStack_24;
  undefined1 uStack_23;
  undefined1 uStack_22;
  undefined1 uStack_21;
  
  iVar3 = *param_1;
  iVar1 = *(int *)(iVar3 + 0x30);
  iVar4 = *(int *)(param_1[1] + 0x10);
  if ((iVar4 != 0) && (*(int *)(iVar1 + 0x80) != 0)) {
    iVar5 = *(int *)(iVar3 + 0x50) + iVar4;
    iVar2 = 1;
    if (1 < *(byte *)(iVar3 + 0x62)) {
      do {
        iVar2 = iVar2 + 1;
        uVar6 = (**(code **)(iVar1 + 0x48))(iVar3,param_2,0,iVar4,0,iVar5,0,1);
        param_2 = (undefined4)uVar6;
        if ((int)((ulonglong)uVar6 >> 0x20) != 0) {
          return 0xffffffff;
        }
        iVar5 = iVar5 + *(int *)(iVar3 + 0x50);
      } while (iVar2 < (int)(uint)*(byte *)(iVar3 + 0x62));
    }
    if (((*(uint *)(*param_1 + 0x9c) & 0x80000) != 0) ||
       (iVar4 = 1, (*(uint *)(*param_1 + 0x9c) & 0x20000) != 0)) {
      iVar4 = 2;
    }
    if (*(int *)(iVar3 + 0x74) == 2) {
      uStack_28 = (undefined1)*(undefined4 *)(iVar1 + 0x60);
      uStack_27 = (undefined1)((uint)*(undefined4 *)(iVar1 + 0x60) >> 8);
      uStack_26 = (undefined1)((uint)*(undefined4 *)(iVar1 + 0x60) >> 0x10);
      uStack_25 = (undefined1)((uint)*(undefined4 *)(iVar1 + 0x60) >> 0x18);
      uStack_24 = (undefined1)*(undefined4 *)(iVar1 + 0x78);
      uStack_23 = (undefined1)((uint)*(undefined4 *)(iVar1 + 0x78) >> 8);
      uStack_22 = (undefined1)((uint)*(undefined4 *)(iVar1 + 0x78) >> 0x10);
      uStack_21 = (undefined1)((uint)*(undefined4 *)(iVar1 + 0x78) >> 0x18);
      iVar2 = (**(code **)(iVar1 + 0x44))(iVar3,param_2,0,1,0x1e8,&uStack_28,8,iVar4);
      if (iVar2 != 0) {
        return 0xffffffff;
      }
    }
    if (iVar4 == 2) {
      (**(code **)(iVar1 + 0x4c))(iVar3,0xcb100010,0);
    }
  }
  return 0;
}

