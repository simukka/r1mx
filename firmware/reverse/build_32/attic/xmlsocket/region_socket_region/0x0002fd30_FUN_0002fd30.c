/* 0x0002fd30  FUN_0002fd30  size=1068 bytes */


int * FUN_0002fd30(int param_1,int param_2,uint param_3,uint param_4)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 extraout_r4;
  int iVar8;
  int *piVar9;
  int iVar10;
  int iVar11;
  
  piVar9 = (int *)0x0;
  bVar2 = false;
  bVar3 = true;
  if (((param_1 == 0) || (*(int *)(param_1 + 0x20) != -0x205368dd)) || ((param_3 & 3) == 3)) {
    FUN_00442990(0x38000a);
    return (int *)0xffffffff;
  }
  param_3 = param_3 + 1;
  if ((param_2 == 0) || (uVar4 = FUN_0039b0f0(param_2), 0x400 < uVar4)) {
    FUN_00442990(0x380019);
    return (int *)0xffffffff;
  }
  iVar5 = FUN_005accf4(*(undefined4 *)(param_1 + 0x34),0xffffffff);
  if (iVar5 == -1) {
    return (int *)0xffffffff;
  }
  iVar5 = FUN_005b804c(*(undefined4 *)(param_1 + 0x28),0xbd000006,0);
  if (iVar5 != 0 && iVar5 != 0x23) {
    FUN_00442990();
    FUN_005ad104(*(undefined4 *)(param_1 + 0x34));
    return (int *)0xffffffff;
  }
  if ((*(int *)(param_1 + 0x24) == 0) && (iVar5 = FUN_0002ed24(param_1), iVar5 == -1)) {
    FUN_005ad104(*(undefined4 *)(param_1 + 0x34));
LAB_0002ffd4:
    uVar4 = param_3;
    if (bVar2) {
LAB_00030048:
      FUN_0002b518(piVar9);
    }
  }
  else {
    if ((param_4 & 0xf000) == 0x4000) {
      uVar4 = param_3 & 0xfffffbff;
      iVar5 = 0x4000;
      if ((param_3 & 0x200) != 0) {
        uVar4 = uVar4 | 0x800;
      }
    }
    else {
      param_4 = 0x8000;
      iVar5 = 0x8000;
      uVar4 = param_3;
    }
    piVar9 = (int *)FUN_0002baf4(param_1);
    param_3 = uVar4;
    if (piVar9 == (int *)0x0) {
LAB_000300cc:
      FUN_005ad104(*(undefined4 *)(param_1 + 0x34));
      goto LAB_0002ffd4;
    }
    uVar6 = FUN_00442920();
    FUN_00442990(0);
    iVar7 = (*(code *)**(undefined4 **)(param_1 + 0x2c))(piVar9,param_2,uVar4,param_4);
    if (iVar7 == -1) {
      iVar5 = FUN_00442920();
      if (iVar5 == 0) {
        FUN_00442990(0x380003);
      }
      goto LAB_000300cc;
    }
    FUN_00442990(uVar6);
    iVar11 = *piVar9;
    iVar7 = piVar9[1];
    iVar10 = *(int *)(iVar11 + 0x40);
    FUN_005accf4(*(undefined4 *)(iVar11 + 0x34),0xffffffff);
    iVar8 = 0;
    bVar1 = *(short *)(iVar11 + 0x7c) != 0;
    while (bVar1) {
      iVar8 = iVar8 + 1;
      if (((((*(short *)(iVar10 + 0x40) != 0) && (piVar9[1] != iVar10)) &&
           (-1 < *(char *)(iVar10 + 8))) &&
          (((*(byte *)(iVar10 + 8) & 0x40) == 0 &&
           (*(int *)(iVar10 + 0x18) == *(int *)(iVar7 + 0x18))))) &&
         (*(int *)(iVar10 + 0x1c) == *(int *)(iVar7 + 0x1c))) {
        memset(piVar9[1],0x48);
        piVar9[1] = iVar10;
        *(short *)(iVar10 + 0x40) = *(short *)(iVar10 + 0x40) + 1;
        break;
      }
      iVar10 = iVar10 + 0x48;
      bVar1 = iVar8 < (int)(uint)*(ushort *)(iVar11 + 0x7c);
    }
    FUN_005ad104(*(undefined4 *)(iVar11 + 0x34));
    if (((*(byte *)(piVar9[1] + 0x42) & 1) != 0) && ((uVar4 & 2) != 0)) {
      FUN_00442990(0x380011);
      goto LAB_000300cc;
    }
    piVar9[0x10] = uVar4;
    FUN_005ad104(*(undefined4 *)(param_1 + 0x34));
    if ((((uVar4 & 0x200) != 0) && (iVar5 != 0x4000)) && ((*(byte *)(piVar9[1] + 0x42) & 0x10) != 0)
       ) {
      FUN_00442990(0x380009);
      goto LAB_0002ffe4;
    }
    if ((uVar4 & 0x10400) == 0) {
LAB_0002ffd0:
      bVar3 = false;
      goto LAB_0002ffd4;
    }
    FUN_0002b4cc(piVar9,0xffffffff);
    bVar2 = true;
    uVar6 = 0x38000a;
    if (piVar9[0x11] == 0) {
LAB_00030044:
      FUN_00442990(uVar6);
      goto LAB_00030048;
    }
    if ((*(char *)(piVar9[1] + 8) < '\0') || ((*(byte *)(piVar9[1] + 8) & 0x40) != 0)) {
      uVar6 = 0x380003;
      goto LAB_00030044;
    }
    if ((uVar4 & 0x400) == 0) {
LAB_0003005c:
      if ((uVar4 & 0x10000) != 0) {
        (**(code **)(*(int *)(param_1 + 0x30) + 4))(piVar9);
      }
      goto LAB_0002ffd0;
    }
    iVar7 = piVar9[0x10];
    piVar9[0x10] = 3;
    iVar5 = FUN_0002c3e8(piVar9,extraout_r4,0,0);
    piVar9[0x10] = iVar7;
    if (iVar5 != -1) goto LAB_0003005c;
    FUN_0002b518(piVar9);
  }
  if (!bVar3) {
    if ((uVar4 & 0x2000) != 0) {
      FUN_0002ed80(piVar9,0x15,0xffffffff);
      return piVar9;
    }
    return piVar9;
  }
LAB_0002ffe4:
  if (piVar9 != (int *)0x0) {
    FUN_0002ba90(piVar9);
  }
  return (int *)0xffffffff;
}

