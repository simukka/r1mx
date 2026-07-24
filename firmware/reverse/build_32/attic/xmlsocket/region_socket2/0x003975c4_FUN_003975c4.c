/* 0x003975c4  FUN_003975c4  size=956 bytes */


undefined4 FUN_003975c4(int param_1,uint param_2,int param_3)

{
  bool bVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  ushort uVar6;
  uint uVar5;
  int iVar7;
  uint uVar8;
  undefined1 auStack_68 [8];
  uint uStack_60;
  int iStack_4c;
  undefined4 uStack_3c;
  
  if ((*(int *)(param_1 + 4) != param_1) || (*(char *)(param_1 + 10) != 'f')) {
    return 0xffffffff;
  }
  if (param_3 == 0) {
LAB_003976b0:
    iVar7 = 0;
    bVar1 = false;
  }
  else {
    if (param_3 != 1) {
      if (param_3 != 2) {
        puVar2 = (undefined4 *)FUN_00442914();
        *puVar2 = 0x16;
        return 0xffffffff;
      }
      goto LAB_003976b0;
    }
    if ((*(ushort *)(param_1 + 0x18) & 0x1000) == 0) {
      iVar7 = FUN_00398aac(param_1,0,1);
      if (iVar7 == -1) {
        return 0xffffffff;
      }
    }
    else {
      iVar7 = *(int *)(param_1 + 0x48);
    }
    if ((*(ushort *)(param_1 + 0x18) & 4) == 0) {
      if (((*(ushort *)(param_1 + 0x18) & 8) != 0) && (*(int *)(param_1 + 0xc) != 0)) {
        iVar7 = iVar7 + (*(int *)(param_1 + 0xc) - *(int *)(param_1 + 0x1c));
      }
    }
    else {
      iVar7 = iVar7 - *(int *)(param_1 + 0x10);
      if (*(int *)(param_1 + 0x28) != 0) {
        iVar7 = iVar7 - *(int *)(param_1 + 0x34);
      }
    }
    param_2 = param_2 + iVar7;
    param_3 = 0;
    bVar1 = true;
  }
  if (*(int *)(param_1 + 0x1c) == 0) {
    FUN_003980b8(param_1);
  }
  if ((*(ushort *)(param_1 + 0x18) & 0x81a) == 0) {
    iVar3 = FUN_0044e510((int)*(short *)(param_1 + 0x1a),0x40,auStack_68);
    uVar6 = *(ushort *)(param_1 + 0x18);
    if ((uVar6 & 0x400) == 0) {
      if (((*(short *)(param_1 + 0x1a) < 0) || (iVar3 != 0)) || ((uStack_60 & 0xf000) != 0x8000)) {
        *(ushort *)(param_1 + 0x18) = uVar6 | 0x800;
        goto LAB_003978f4;
      }
      uVar6 = uVar6 | 0x400;
      *(ushort *)(param_1 + 0x18) = uVar6;
      *(undefined4 *)(param_1 + 0x44) = uStack_3c;
    }
    uVar5 = param_2;
    if (param_3 != 0) {
      if (iVar3 != 0) goto LAB_003978f4;
      uVar5 = iStack_4c + param_2;
    }
    if (bVar1) {
LAB_003977c0:
      if (*(int *)(param_1 + 0x28) == 0) goto LAB_003977d8;
      iVar3 = *(int *)(param_1 + 0x30);
      iVar4 = 0x34;
    }
    else {
      if ((uVar6 & 0x1000) == 0) {
        iVar7 = FUN_00398aac(param_1,0,1);
        if (iVar7 == -1) goto LAB_003978f4;
      }
      else {
        iVar7 = *(int *)(param_1 + 0x48);
      }
      iVar7 = iVar7 - *(int *)(param_1 + 0x10);
      if (*(int *)(param_1 + 0x28) != 0) {
        iVar7 = iVar7 - *(int *)(param_1 + 0x34);
        goto LAB_003977c0;
      }
LAB_003977d8:
      iVar3 = *(int *)(param_1 + 0xc);
      iVar4 = 0x10;
    }
    iVar3 = iVar3 - *(int *)(param_1 + 0x1c);
    iVar7 = iVar7 - iVar3;
    iVar3 = iVar3 + *(int *)(param_1 + iVar4);
    if ((((*(ushort *)(param_1 + 0x18) & 0x2000) == 0) && (iVar7 <= (int)uVar5)) &&
       (uVar5 < (uint)(iVar7 + iVar3))) {
      *(uint *)(param_1 + 0x10) = iVar3 - (uVar5 - iVar7);
      iVar3 = *(int *)(param_1 + 0x28);
      *(uint *)(param_1 + 0xc) = *(int *)(param_1 + 0x1c) + (uVar5 - iVar7);
      if (iVar3 != 0) {
        if (param_1 + 0x38 != iVar3) {
          FUN_0045b580(iVar3);
        }
        *(undefined4 *)(param_1 + 0x28) = 0;
      }
      goto LAB_0039795c;
    }
    uVar8 = uVar5 & ~(*(int *)(param_1 + 0x44) - 1U);
    iVar7 = FUN_00398aac(param_1,uVar8,0);
    if (iVar7 != -1) {
      iVar7 = *(int *)(param_1 + 0x28);
      *(undefined4 *)(param_1 + 0x10) = 0;
      if (iVar7 != 0) {
        if (param_1 + 0x38 != iVar7) {
          FUN_0045b580(iVar7);
        }
        *(undefined4 *)(param_1 + 0x28) = 0;
      }
      uVar5 = uVar5 - uVar8;
      *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) & 0xffdf;
      if (uVar5 == 0) {
        return 0;
      }
      iVar7 = FUN_0039856c(param_1);
      if ((iVar7 == 0) && (uVar5 <= *(uint *)(param_1 + 0x10))) {
        *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) - uVar5;
        *(uint *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + uVar5;
        return 0;
      }
    }
  }
LAB_003978f4:
  iVar7 = FUN_00396c70(param_1);
  if ((iVar7 != 0) || (iVar7 = FUN_00398aac(param_1,param_2,param_3), iVar7 == -1)) {
    return 0xffffffff;
  }
  iVar7 = *(int *)(param_1 + 0x28);
  if (iVar7 != 0) {
    if (param_1 + 0x38 != iVar7) {
      FUN_0045b580(iVar7);
    }
    *(undefined4 *)(param_1 + 0x28) = 0;
  }
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_1 + 0x1c);
LAB_0039795c:
  *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) & 0xffdf;
  return 0;
}

