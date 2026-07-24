/* 0x00026628  FUN_00026628  size=1180 bytes */


uint FUN_00026628(int param_1,int param_2)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  undefined1 auStack_98 [12];
  undefined1 **ppuStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined1 auStack_68 [2];
  byte bStack_66;
  undefined1 uStack_5c;
  undefined1 *apuStack_48 [5];
  
  iVar10 = *(int *)(param_1 + 0x38);
  iVar6 = *(int *)(param_1 + 0x34) * 0x430;
  iVar8 = iVar10 * 600 + iVar6 + 0x108e6a0;
  iVar11 = 0;
  if (*(int *)(param_2 + 0x10) == 0) {
    *(undefined4 *)(param_2 + 0x1c) = 0;
    *(undefined4 *)(param_2 + 0x18) = 0;
  }
  else {
    if (*(int *)(param_2 + 0x18) == 0) {
      return 0xffffffff;
    }
    if (*(uint *)(param_2 + 0x18) < 0xffff) {
      if (*(uint *)(param_2 + 0x18) < *(uint *)(param_2 + 0x10)) {
        *(uint *)(param_2 + 0x18) = *(uint *)(param_2 + 0x18) & 0xfffffffe;
      }
    }
    else {
      *(undefined4 *)(param_2 + 0x18) = 0xfffe;
    }
  }
  iVar9 = iVar6 + 0x108e964;
  FUN_005accf4(iVar9,0xffffffff);
LAB_000266e8:
  do {
    iVar3 = FUN_00025ce4(param_1,param_2);
    if (iVar3 == 0) {
      if ((*(byte *)(param_1 + 0x59) & 1) == 0) {
LAB_000269d4:
        FUN_005ad104(iVar9);
        return 0;
      }
      uVar4 = FUN_0000a05c(*(undefined4 *)(iVar6 + 0x108ea08));
      uVar1 = uVar4 & 0xf0;
      if (uVar1 == 0x40) {
        uVar2 = 0xf;
LAB_0002673c:
        *(undefined4 *)(param_1 + 0x54) = uVar2;
      }
      else {
        if (0x40 < uVar1) {
          if (uVar1 == 0x70) {
            uVar2 = 0x12;
          }
          else if (uVar1 < 0x71) {
            if (uVar1 == 0x50) {
              uVar2 = 0x10;
            }
            else {
              if (uVar1 != 0x60) goto LAB_00026738;
              uVar2 = 0x11;
            }
          }
          else if (uVar1 == 0xb0) {
            uVar2 = 0x13;
          }
          else {
            if (uVar1 != 0xe0) goto LAB_00026738;
            uVar2 = 0x14;
          }
          goto LAB_0002673c;
        }
        if (uVar1 == 0x10) {
          if (*(uint *)(param_1 + 0x48) <= *(uint *)(param_1 + 0x44)) goto LAB_000269d4;
          uVar2 = 0xc;
          goto LAB_0002673c;
        }
        if (0x10 < uVar1) {
          if (uVar1 == 0x20) {
            uVar2 = 0xd;
          }
          else {
            if (uVar1 != 0x30) goto LAB_00026738;
            uVar2 = 0xe;
          }
          goto LAB_0002673c;
        }
        if (uVar1 != 0) {
LAB_00026738:
          uVar2 = 0;
          goto LAB_0002673c;
        }
        *(undefined4 *)(param_1 + 0x54) = 0xb;
      }
      if (8 < iRam00e107b4) {
        uVar2 = FUN_0000a05c(*(undefined4 *)(iVar6 + 0x108ea20));
        FUN_00443f20(0xd36330,*(undefined4 *)(param_1 + 0x34),iVar10,
                     *(undefined4 *)(*(int *)(param_1 + 0x54) * 4 + 0xe10740),
                     *(undefined1 *)(param_1 + 0x59),uVar2,uVar4);
      }
      if (uVar4 == 0) goto LAB_000268f0;
      if ((uVar4 & 0xf0) == 0x60) {
        *(undefined1 *)(iVar8 + 0x234) = 4;
        *(undefined4 *)(param_1 + 0x30) = 1;
        goto LAB_0002683c;
      }
      iVar3 = *(int *)(param_1 + 0x34) * 0x430;
      apuStack_48[0] = auStack_68;
      if (6 < iRam00e107b4) {
        FUN_00443f20(0xd36370,*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),0,0,0,
                     0);
      }
      iVar12 = 3;
      auStack_98[0] = 3;
      iVar7 = 1;
      do {
        auStack_98[iVar7] = 0;
        iVar7 = iVar7 + 1;
        iVar12 = iVar12 + -1;
      } while (iVar12 != 0);
      iVar12 = 7;
      auStack_98[4] = 0x12;
      iVar7 = 5;
      do {
        auStack_98[iVar7] = 0;
        iVar7 = iVar7 + 1;
        iVar12 = iVar12 + -1;
      } while (iVar12 != 0);
      ppuStack_8c = apuStack_48;
      uStack_84 = 2;
      uStack_80 = 0x12;
      uStack_78 = 0;
      uStack_88 = 0x12;
      uStack_7c = 0;
      iVar7 = FUN_00025ce4(param_1,auStack_98);
      if (iVar7 == 0) {
        if ((*(byte *)(param_1 + 0x59) & 1) == 0) {
          memset(apuStack_48[0],0x12 - ((int)apuStack_48[0] - (int)auStack_68));
          if (8 < iRam00e107b4) {
            FUN_00443f20(0xd363c4,*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),
                         bStack_66 & 0xf,uStack_5c,0,0);
          }
          iVar11 = iVar11 + 1;
          if (iVar11 < iRam00e107c4) {
            *(undefined1 *)(iVar8 + 0x234) = 0;
            *(undefined4 *)(param_1 + 0x30) = 0;
            *(undefined4 *)(param_1 + 0x54) = 0;
            goto LAB_000266e8;
          }
        }
        else if (8 < iRam00e107b4) {
          uVar2 = FUN_0000a05c(*(undefined4 *)(iVar3 + 0x108ea20));
          uVar5 = FUN_0000a05c(*(undefined4 *)(iVar3 + 0x108ea08));
          FUN_00443f20(0xd36388,*(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),
                       *(undefined1 *)(param_1 + 0x59),uVar2,uVar5,0);
        }
      }
      if ((uVar4 & 0xf0) == 0x60) goto LAB_0002683c;
    }
    else {
LAB_000268f0:
      uVar4 = 0xff;
    }
    FUN_0002410c(*(undefined4 *)(param_1 + 0x34),iVar10);
    iVar11 = iVar11 + 1;
    if (iRam00e107c4 <= iVar11) {
LAB_0002683c:
      FUN_005ad104(iVar9);
      FUN_00442990(5);
      return uVar4;
    }
  } while( true );
}

