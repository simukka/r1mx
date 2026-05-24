/* 0x000206bc  FUN_000206bc  size=716 bytes */


undefined4 FUN_000206bc(int param_1,int param_2,int param_3)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = param_1 * 0x430;
  if (iRam00e107b4 < 5) {
    uVar1 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea20));
    uVar1 = uVar1 >> 4 & 1;
    iVar5 = uVar1 * 600 + iVar4 + 0x108e6a0;
    if (param_2 != 0x40) goto LAB_0002072c;
LAB_00020828:
    FUN_005b5070(*(undefined4 *)(iVar4 + 0x108e9d0),*(undefined4 *)(iVar4 + 0x108e9dc),0x3036c,
                 param_1);
    do {
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
      if ((uVar3 & 0x80) == 0) break;
    } while (*(int *)(iVar4 + 0x108e9d4) != 0);
    do {
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
      if ((uVar3 & 0x40) != 0) break;
    } while (*(int *)(iVar4 + 0x108e9d4) != 0);
    do {
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
      if ((uVar3 & 8) == 0) break;
    } while (*(int *)(iVar4 + 0x108e9d4) != 0);
  }
  else {
    uVar2 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
    FUN_00443f20(0xd357cc,param_1,param_2,uVar2,0,0,0);
    uVar1 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea20));
    uVar1 = uVar1 >> 4 & 1;
    iVar5 = uVar1 * 600 + iVar4 + 0x108e6a0;
    if (param_2 == 0x40) goto LAB_00020828;
LAB_0002072c:
    if (param_2 < 0x41) {
      if (param_2 == 8) {
        do {
          uVar1 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
          if ((uVar1 & 8) != 0) break;
          uVar1 = FUN_0000a6ec(param_1,0);
        } while ((uVar1 & 0xf0f) == 0x103);
      }
      else if (param_2 == 0x10) {
        do {
          uVar1 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
          if ((uVar1 & 0x10) != 0) break;
          uVar1 = FUN_0000a6ec(param_1,0);
        } while ((uVar1 & 0xf0f) == 0x103);
      }
      goto LAB_00020740;
    }
    if (param_2 == 0x80) {
      do {
        uVar1 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
        if ((uVar1 & 0x80) == 0) break;
        uVar1 = FUN_0000a6ec(param_1,0);
      } while ((uVar1 & 0xf0f) == 0x103);
      goto LAB_00020740;
    }
    if (param_2 != 0x88) goto LAB_00020740;
    FUN_005b5070(*(undefined4 *)(iVar4 + 0x108e9d0),*(undefined4 *)(iVar4 + 0x108e9dc),0x3036c,
                 param_1);
    do {
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
      if ((uVar3 & 0x80) == 0) break;
    } while (*(int *)(iVar4 + 0x108e9d4) != 0);
    do {
      uVar3 = FUN_0000a05c(*(undefined4 *)(iVar4 + 0x108ea2c));
      if ((uVar3 & 8) == 0) break;
    } while (*(int *)(iVar4 + 0x108e9d4) != 0);
  }
  FUN_005b5250(*(undefined4 *)(iVar4 + 0x108e9d0));
  if (*(int *)(iVar4 + 0x108e9d4) == 0) {
    *(undefined4 *)(iVar4 + 0x108e9d4) = 1;
    if (param_3 != 1) {
      return 0xffffffff;
    }
    (**(code **)(iVar5 + 0x238))(param_1,uVar1);
    return 0xffffffff;
  }
LAB_00020740:
  if (4 < iRam00e107b4) {
    FUN_00443f20(0xd357bc,0,0,0,0,0,0);
  }
  return 0;
}

