/* 0x0001ef88  FUN_0001ef88  size=1324 bytes */


void FUN_0001ef88(undefined4 *param_1)

{
  ushort uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  
  iVar7 = param_1[0xe];
  iVar9 = (param_1[0xd] + param_1[0xe]) * 0x14;
  iVar10 = param_1[0xd] * 0x430 + 0x108e6a0;
  iVar11 = iVar7 * 600 + iVar10;
  uVar8 = param_1[0x10];
  if (8 < iRam00e107b4) {
    FUN_00443f20(0xd35178,param_1[0xd],param_1[0xe],param_1,0,0,0);
  }
  if ((*(char *)(iVar11 + 0x234) == '\0') || (*(char *)(iVar11 + 0x234) == '\x04')) {
    if (*(char *)(iVar11 + 0x236) == '\x01') {
      if (8 < iRam00e107b4) {
        FUN_00443f20(0xd35260,param_1[0xd],param_1[0xe],0,0,0,0);
      }
      if (*(short *)(iVar11 + 0x208) == 1) {
        iVar10 = *(int *)(iVar11 + 0x248);
        uVar12 = *(uint *)(iVar11 + 0x24c) - param_1[0xf];
        iVar7 = ((int)param_1[0xf] >> 0x1f) + (uint)(*(uint *)(iVar11 + 0x24c) < (uint)param_1[0xf])
        ;
        if (4 < iRam00e107b4) {
          uVar2 = 0xd35280;
          if (param_1[0xd] == 0) {
            uVar2 = 0xdf7e38;
          }
          uVar3 = 0xd3528c;
          if (param_1[0xe] == 0) {
            uVar3 = 0xd35294;
          }
          uVar4 = 0xd3529c;
          if (iVar10 != iVar7) {
            uVar4 = 0xd352b0;
          }
          FUN_00443f20(0xd352d0,uVar2,uVar3,*(undefined4 *)(iVar11 + 0x248),
                       *(undefined4 *)(iVar11 + 0x24c),uVar4,0);
        }
        if (iVar10 != iVar7) {
          uVar12 = 0xffffffff;
        }
      }
      else if ((((*(short *)(iVar11 + 0x206) == 1) && (*(int *)(iVar11 + 0x244) != 0)) &&
               (iRam00e1072c != 1)) &&
              ((uint)(*(int *)(iVar9 + 0xe0bb24) * *(int *)(iVar9 + 0xe0bb28) *
                     *(int *)(iVar9 + 0xe0bb2c)) < *(uint *)(iVar11 + 0x244))) {
        uVar12 = *(int *)(iVar11 + 0x244) - param_1[0xf];
      }
      else {
        uVar12 = *(int *)(iVar9 + 0xe0bb24) * *(int *)(iVar9 + 0xe0bb28) *
                 *(int *)(iVar9 + 0xe0bb2c) - param_1[0xf];
        if (8 < iRam00e107b4) {
          FUN_00443f20(0xd3533c,param_1[0xd],param_1[0xe],*(int *)(iVar9 + 0xe0bb24),
                       *(undefined4 *)(iVar9 + 0xe0bb28),*(undefined4 *)(iVar9 + 0xe0bb2c),0);
        }
      }
      if (uVar8 == 0) {
        uVar8 = uVar12;
      }
      if (uVar12 < uVar8) {
        uVar8 = uVar12;
      }
      param_1[6] = uVar8;
      param_1[7] = *(undefined4 *)(iVar9 + 0xe0bb30);
      param_1[8] = *(undefined4 *)(iVar9 + 0xe0bb2c);
      param_1[9] = *(undefined4 *)(iVar9 + 0xe0bb28);
      param_1[5] = 1;
      param_1[10] = 1;
      param_1[0xb] = 2;
      param_1[0xc] = 1;
      *param_1 = 0x35a78;
      param_1[1] = 0x35a68;
      param_1[2] = 0x376f8;
      param_1[3] = 0x2fb68;
      param_1[4] = 0x2f89c;
      iVar7 = iRam00e107b4;
    }
    else if (*(char *)(iVar11 + 0x236) == '\x02') {
      if (8 < iRam00e107b4) {
        FUN_00443f20(0xd35318,param_1[0xd],param_1[0xe],0,0,0,0);
      }
      param_1[6] = 0;
      param_1[7] = 0x800;
      param_1[8] = 100;
      param_1[9] = 1;
      uVar1 = *(ushort *)(iVar7 * 600 + iVar10);
      if ((uVar1 & 0x80) == 0) {
        param_1[5] = uVar1 & 0x80;
      }
      else {
        param_1[5] = 1;
      }
      param_1[10] = 1;
      param_1[0xb] = 0;
      param_1[0xc] = 1;
      *param_1 = 0x3708c;
      param_1[1] = 0x2ef78;
      param_1[2] = 0x34374;
      param_1[3] = 0x36f04;
      param_1[4] = 0x36dbc;
      iVar7 = iRam00e107b4;
    }
    else {
      if (8 < iRam00e107b4) {
        FUN_00443f20(0xd35238,param_1[0xd],param_1[0xe],0,0,0,0);
      }
      param_1[6] = 0;
      param_1[7] = 0x200;
      param_1[8] = 0;
      param_1[9] = 0;
      param_1[5] = 1;
      param_1[10] = 1;
      param_1[0xb] = 2;
      iVar7 = iRam00e107b4;
      param_1[0xc] = 1;
      *param_1 = 0x2ef78;
      param_1[1] = 0x2ef78;
      param_1[2] = 0x2ef78;
      param_1[3] = 0x2fb68;
      param_1[4] = 0x2ef78;
    }
    if (iVar7 < 3) {
      return;
    }
    uVar3 = param_1[6];
    uVar4 = param_1[7];
    uVar5 = param_1[8];
    uVar6 = param_1[9];
    uVar2 = 0xd351a4;
  }
  else {
    if (iRam00e107b4 < 7) {
      return;
    }
    uVar3 = param_1[0xd];
    uVar4 = param_1[0xe];
    uVar2 = 0xd35150;
    uVar5 = 0;
    uVar6 = 0;
  }
  FUN_00443f20(uVar2,uVar3,uVar4,uVar5,uVar6,0,0);
  return;
}

