/* 0x0002b564  FUN_0002b564  size=372 bytes */


undefined4 FUN_0002b564(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = FUN_0002b410(param_1,0);
  uVar2 = 0xffffffff;
  if ((iVar1 != 0) && (*(int *)(iVar1 + 0x24) != 0)) {
    iVar3 = FUN_005accf4(*(undefined4 *)(iVar1 + 0x34),0xffffffff);
    uVar2 = 0xffffffff;
    if (iVar3 != -1) {
      iVar3 = 0;
      if (*(short *)(iVar1 + 0x7c) != 0) {
        iVar5 = 0;
        do {
          while (iVar3 = iVar3 + 1, *(int *)(iVar5 + *(int *)(iVar1 + 0x3c) + 0x44) != 0) {
            (**(code **)(*(int *)(iVar1 + 0x30) + 0x24))(*(int *)(iVar1 + 0x3c) + iVar5);
            iVar4 = *(int *)(iVar5 + *(int *)(iVar1 + 0x3c) + 4);
            iVar5 = iVar5 + 0x48;
            *(byte *)(iVar4 + 8) = *(byte *)(iVar4 + 8) | 0x40;
            if ((int)(uint)*(ushort *)(iVar1 + 0x7c) <= iVar3) goto LAB_0002b634;
          }
          iVar5 = iVar5 + 0x48;
        } while (iVar3 < (int)(uint)*(ushort *)(iVar1 + 0x7c));
      }
LAB_0002b634:
      *(undefined2 *)(iVar1 + 0x7e) = 0;
      (**(code **)(*(int *)(iVar1 + 0x30) + 0x1c))(iVar1);
      (**(code **)(iVar1 + 0xb8))(iVar1,0xcb100010,0xffffffff);
      (**(code **)(iVar1 + 0xb8))(iVar1,0xcb100030,0);
      if (pcRam00e107ec != reset_vector) {
        (*pcRam00e107ec)(iVar1);
      }
      *(undefined4 *)(iVar1 + 0x24) = 0;
      FUN_005ad104(*(undefined4 *)(iVar1 + 0x34));
      uVar2 = 0;
    }
  }
  return uVar2;
}

