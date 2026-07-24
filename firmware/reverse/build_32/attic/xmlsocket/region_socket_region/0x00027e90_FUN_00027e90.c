/* 0x00027e90  FUN_00027e90  size=852 bytes */


int FUN_00027e90(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int aiStack_28 [3];
  
  iVar6 = param_1[0xe];
  iVar4 = *(int *)(param_1[0xe] + 0x34) * 0x430;
  iVar7 = *(int *)(param_1[0xe] + 0x38) * 600 + iVar4 + 0x108e6a0;
  iVar5 = 0;
  if (iRam00e107b4 < 9) {
    FUN_005accf4(iVar4 + 0x108e964,0xffffffff);
    iVar1 = *param_1;
  }
  else {
    FUN_00443f20(0xd36710,*(undefined4 *)(param_1[0xe] + 0x34),*(undefined4 *)(param_1[0xe] + 0x38),
                 0,0,0,0);
    FUN_005accf4(iVar4 + 0x108e964,0xffffffff);
    iVar1 = *param_1;
  }
  if ((iVar1 == -1) && (*(char *)(iVar7 + 0x236) != '\0')) {
    if (8 < iRam00e107b4) {
      FUN_00443f20(0xd36810,*(undefined4 *)(param_1[0xe] + 0x34),
                   *(undefined4 *)(param_1[0xe] + 0x38),0,0,0,0);
    }
    iVar5 = FUN_005b800c(param_1,0xe107b8,param_1 + 10,*(undefined4 *)(iVar6 + 0x1c),0,
                         *(undefined4 *)(iVar6 + 0x18),aiStack_28);
    if (iVar5 == 0) {
      FUN_003c8c84(uRam00e3a8fc,uRam00e3a8fe,0,*param_1,0);
      if (8 < iRam00e107b4) {
        uVar3 = *(undefined4 *)(iVar6 + 0x18);
        uVar2 = 0xd367d4;
LAB_000280f0:
        FUN_00443f20(uVar2,aiStack_28[0],uVar3,0,0,0,0);
        *(undefined4 *)(iVar6 + 0x30) = 0;
        FUN_005ad104(iVar4 + 0x108e964);
        return iVar5;
      }
    }
    else if (8 < iRam00e107b4) {
      uVar2 = 0xd36734;
      uVar3 = 0;
      aiStack_28[0] = iVar5;
      goto LAB_000280f0;
    }
  }
  else {
    iVar1 = iVar4 + 0x108e964;
    if ((*param_1 != -1) && (*(char *)(iVar7 + 0x236) == '\0')) {
      if (8 < iRam00e107b4) {
        FUN_00443f20(0xd3679c,*(undefined4 *)(param_1[0xe] + 0x34),
                     *(undefined4 *)(param_1[0xe] + 0x38),0,0,0,0);
      }
      FUN_003c8c84(uRam00e3a8fc,uRam00e3a900,0,*param_1,0);
      thunk_FUN_003c6ce0(param_1);
      *param_1 = -1;
      FUN_005accf4(iVar1,0xffffffff);
      while (iVar5 = FUN_00027a48(iVar4 + 0x108e6a0), iVar5 != 0) {
        FUN_005b7e80(iVar5,6);
      }
      FUN_005ad104(iVar1);
      *(undefined4 *)(iVar6 + 0x30) = 0;
      FUN_005ad104(iVar1);
      return 0;
    }
    if (8 < iRam00e107b4) {
      uVar2 = 0xd3676c;
      uVar3 = *(undefined4 *)(param_1[0xe] + 0x38);
      aiStack_28[0] = *(int *)(param_1[0xe] + 0x34);
      goto LAB_000280f0;
    }
  }
  *(undefined4 *)(iVar6 + 0x30) = 0;
  FUN_005ad104(iVar4 + 0x108e964);
  return iVar5;
}

