/* 0x0002c680  FUN_0002c680  size=684 bytes */


undefined4 FUN_0002c680(int *param_1)

{
  char cVar1;
  bool bVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  int *piVar9;
  undefined8 uVar10;
  
  uVar7 = 0xffffffff;
  bVar2 = false;
  if (((param_1 == (int *)0x0 || param_1 == (int *)0xffffffff) || (param_1[0x11] == 0)) ||
     (*(int *)(*param_1 + 0x20) != -0x205368dd)) {
    FUN_00442990(0x38000a);
    return 0xffffffff;
  }
  iVar8 = *param_1;
  piVar9 = (int *)param_1[1];
  uVar10 = FUN_0002b4cc(param_1,0xffffffff);
  uVar3 = (undefined4)uVar10;
  if ((int)((ulonglong)uVar10 >> 0x20) == -1) {
    return 0xffffffff;
  }
  if ((*(byte *)(piVar9 + 2) & 0x40) == 0) {
    *(short *)(iVar8 + 0x7e) = *(short *)(iVar8 + 0x7e) + -1;
    if (*(char *)(piVar9 + 2) < '\0') {
      puVar4 = (undefined4 *)FUN_00442914(0xffffffff);
      bVar2 = true;
      *puVar4 = 0x380016;
    }
    else if ((*(byte *)((int)piVar9 + 0x42) & 0x10) == 0) {
      if (*(int *)(iVar8 + 0x94) == 0) {
        *(undefined1 *)(param_1 + 0xb) = 0;
      }
      if ((*(char *)(param_1 + 0xb) != '\0') || (*(char *)((int)param_1 + 0x2d) != '\0')) {
        cVar1 = *(char *)(param_1 + 0xb);
        uVar3 = FUN_0039c824(0);
        uVar10 = (**(code **)(*(int *)(iVar8 + 0x2c) + 8))
                           (param_1,(-(cVar1 == '\0') & 2U) + 4,uVar3);
        uVar3 = (undefined4)uVar10;
        if ((int)((ulonglong)uVar10 >> 0x20) == -1) goto LAB_0002c810;
        *(undefined1 *)(param_1 + 0xb) = 0;
      }
      if ((*(char *)((int)param_1 + 0x2d) != '\0') ||
         (((*(byte *)(piVar9 + 2) & 0x20) != 0 && (*(short *)(piVar9 + 0x10) == 1)))) {
        if (*(short *)(piVar9 + 0x10) == 1) {
          iVar5 = 0;
          iVar6 = 0;
          if (*piVar9 != 0 || piVar9[1] != 0) {
            iVar6 = piVar9[1] + -1;
            iVar5 = *piVar9 + -1 + (uint)(piVar9[1] != 0);
          }
          iVar5 = FUN_0002bc4c(param_1,uVar3,iVar5,iVar6);
          if (iVar5 == -1) goto LAB_0002c810;
          if (param_1[6] != 0) {
            (**(code **)(*(int *)(iVar8 + 0x30) + 8))(param_1,param_1[6],1);
            *(byte *)(piVar9 + 2) = *(byte *)(piVar9 + 2) & 0xdf;
          }
        }
        bVar2 = true;
        *(undefined1 *)((int)param_1 + 0x2d) = 0;
      }
      uVar7 = 0;
      if (!bVar2) goto LAB_0002c810;
    }
    else {
      bVar2 = true;
      uVar7 = 0;
    }
    (**(code **)(*(int *)(iVar8 + 0x30) + 0x24))(param_1);
  }
  else {
    FUN_00442990(0x380015);
  }
LAB_0002c810:
  FUN_0002b518(param_1);
  FUN_0002ba90(param_1);
  if ((*(short *)(iVar8 + 0x7e) == 0) || (bVar2)) {
    (**(code **)(iVar8 + 0xb8))(iVar8,0xcb100010,0);
  }
  return uVar7;
}

