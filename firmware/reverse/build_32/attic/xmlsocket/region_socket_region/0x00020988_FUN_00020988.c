/* 0x00020988  FUN_00020988  size=1060 bytes */


undefined4 FUN_00020988(int param_1,int param_2,uint param_3,uint param_4,uint param_5)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  
  iVar5 = param_1 * 0x430;
  iVar1 = (param_1 + param_2) * 0x14;
  iVar7 = 0;
  if (0 < iRam00e107b4) {
    FUN_00443f20(0xd357fc,param_1,param_2,param_3,param_4,param_5,0);
  }
  uVar2 = FUN_0000a6ec(param_1,0);
  iVar3 = -1;
  if ((uVar2 & 0xf0f) != 0x103) {
    return 0xffffffff;
  }
  uVar2 = param_2 << 4;
  uVar6 = uVar2 | 0xffffffa0;
  do {
    if ((param_3 == 8) || (iVar3 = FUN_00020390(param_1,0x40), param_3 != 0xb0)) {
      if ((int)param_3 < 0xb1) {
        if (param_3 == 0x70) {
          FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea20),
                       (uVar2 | param_5 & 0xf | 0xffffffa0) & 0xff);
          FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea18),param_4 & 0xff);
          iVar3 = FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea1c),param_4 >> 8 & 0xff);
        }
        else if ((int)param_3 < 0x71) {
          if (param_3 == 0x10) {
LAB_00020d54:
            iVar3 = FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea20),uVar6 & 0xff);
          }
        }
        else {
          if (param_3 == 0x90) goto LAB_00020d54;
          if (param_3 == 0x91) {
            FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea20),
                         (uVar2 | *(int *)(iVar1 + 0xe0bb28) - 1U & 0xf | 0xffffffa0) & 0xff);
            FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea18),*(uint *)(iVar1 + 0xe0bb24) & 0xff);
            FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea1c),*(uint *)(iVar1 + 0xe0bb24) >> 8 & 0xff)
            ;
            iVar3 = FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea10),
                                 *(uint *)(iVar1 + 0xe0bb2c) & 0xff);
          }
        }
      }
      else if ((int)param_3 < 0xe4) {
        if ((0xe1 < (int)param_3) || (param_3 == 0xc6)) {
          FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea20),uVar6 & 0xff);
          uVar4 = *(undefined4 *)(iVar5 + 0x108ea10);
LAB_00020bcc:
          iVar3 = FUN_0000a07c(uVar4,param_4 & 0xff);
        }
      }
      else {
        if (param_3 == 0xe5) goto LAB_00020d54;
        if (param_3 == 0xef) {
          FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea20),uVar6 & 0xff);
          FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea10),param_5 & 0xff);
          uVar4 = *(undefined4 *)(iVar5 + 0x108ea0c);
          goto LAB_00020bcc;
        }
      }
    }
    else {
      FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea20),uVar6 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea0c),param_4 & 0xff);
      FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea18),0x4f);
      iVar3 = FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea1c),0xc2);
      if (param_4 == 0xd2) {
        if (param_5 == 0) {
          iVar3 = FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea10),0);
        }
        else {
          iVar3 = FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea10),0xf1);
        }
      }
      else if (param_4 == 0xd4) {
        iVar3 = FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea14),param_5 & 0xff);
      }
    }
    uVar4 = FUN_0036fd0c(iVar3);
    FUN_0000a07c(*(undefined4 *)(iVar5 + 0x108ea24),param_3 & 0xff);
    *(undefined4 *)(iVar5 + 0x108ea48) = 1;
    FUN_0036fd24(uVar4);
    iVar3 = FUN_005accf4(iVar5 + 0x108e8f8,*(undefined4 *)(iVar5 + 0x108e9d8));
    if (((*(uint *)(iVar5 + 0x108e9f8) & 1) == 0) && (iVar3 != -1)) {
      if (param_3 == 0x70) {
        FUN_00020390(param_1,0x10);
      }
      if (6 < iRam00e107b4) {
        FUN_00443f20(0xd35814,param_1,param_2,0,0,0,0);
      }
      return 0;
    }
    if (iRam00e107b4 < 9) {
      if (iRam00e107c4 < iVar7 + 1) {
        return 0xffffffff;
      }
    }
    else {
      uVar4 = FUN_0000a05c(*(undefined4 *)(iVar5 + 0x108ea08));
      iVar3 = FUN_00443f20(0xd35838,*(undefined4 *)(iVar5 + 0x108e9f8),iVar3,uVar4,0,0,0);
      if (iRam00e107c4 < iVar7 + 1) {
        return 0xffffffff;
      }
    }
    iVar7 = iVar7 + 1;
  } while( true );
}

