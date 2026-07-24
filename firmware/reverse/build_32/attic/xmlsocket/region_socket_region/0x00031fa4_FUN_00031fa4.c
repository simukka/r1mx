/* 0x00031fa4  FUN_00031fa4  size=812 bytes */


int FUN_00031fa4(int param_1,uint param_2,int param_3)

{
  uint uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  
  iVar5 = 0;
  if (param_2 == 0xcb100050) {
LAB_000320a4:
    uVar6 = FUN_005accf4(*(undefined4 *)(param_1 + 0x138),0xffffffff);
    uVar1 = (uint)uVar6;
    if ((int)((ulonglong)uVar6 >> 0x20) == -1) {
      return -1;
    }
  }
  else {
    uVar1 = param_2;
    if (param_2 < 0xcb100051) {
      if ((param_2 == 0xcb100010) || (param_2 == 0xcb100030)) goto LAB_000320a4;
    }
    else if ((param_2 == 0xcb100060) || (param_2 == 0xcb100070)) goto LAB_000320a4;
  }
  if (param_2 == 0xcb100050) {
LAB_000320cc:
    if (((*(int *)(param_1 + 0x13c) != 0) &&
        ((*(int *)(param_1 + 0x148) != -1 || (*(int *)(param_1 + 0x14c) != -1)))) &&
       ((*(int *)(param_1 + 0x150) != 0 &&
        (iVar5 = FUN_0002e05c(param_1,uVar1,*(undefined4 *)(param_1 + 0x148),
                              *(undefined4 *)(param_1 + 0x14c),*(undefined4 *)(param_1 + 0x13c),1),
        iVar5 == -1)))) {
      FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
      return -1;
    }
    if ((*(int *)(param_1 + 0x13c) == 0) || (param_2 != 0xcb100050)) {
      if (param_2 == 0xcb100030) {
        *(undefined4 *)(param_1 + 0x148) = 0xffffffff;
        *(undefined4 *)(param_1 + 0x14c) = 0xffffffff;
      }
      *(undefined4 *)(param_1 + 0x150) = 0;
    }
    else {
      memset(*(undefined4 *)(param_1 + 0x13c),*(undefined4 *)(param_1 + 0x140));
      *(undefined4 *)(param_1 + 0x148) = 0;
      *(int *)(param_1 + 0x14c) = param_3;
      *(undefined4 *)(param_1 + 0x150) = 1;
    }
  }
  else {
    if (param_2 < 0xcb100051) {
      if (param_2 != 0xcb100010) {
        if (param_2 != 0xcb100030) {
LAB_00032040:
          iVar5 = FUN_005b804c(*(undefined4 *)(param_1 + 0x28),param_2,param_3);
          if (iVar5 == 0) {
            return 0;
          }
          FUN_00442990();
          return -1;
        }
        goto LAB_000320cc;
      }
LAB_00032138:
      if ((((*(int *)(param_1 + 0x13c) != 0) &&
           ((*(int *)(param_1 + 0x148) != -1 || (*(int *)(param_1 + 0x14c) != -1)))) &&
          (*(int *)(param_1 + 0x150) != 0)) &&
         (iVar5 = FUN_0002e05c(param_1,uVar1,*(undefined4 *)(param_1 + 0x148),
                               *(undefined4 *)(param_1 + 0x14c),*(undefined4 *)(param_1 + 0x13c),1),
         iVar5 == 0)) {
        *(undefined4 *)(param_1 + 0x150) = 0;
      }
      uVar2 = 0xcb100070;
      if (param_2 != 0xcb100070) goto LAB_0003210c;
      uVar3 = *(undefined4 *)(param_1 + 0x28);
    }
    else {
      if (param_2 != 0xcb100060) {
        if (param_2 != 0xcb100070) goto LAB_00032040;
        goto LAB_00032138;
      }
      if (((*(int *)(param_1 + 0x13c) != 0) && (*(int *)(param_1 + 0x148) == 0)) &&
         (*(int *)(param_1 + 0x14c) == param_3)) {
        *(undefined4 *)(param_1 + 0x148) = 0xffffffff;
        *(undefined4 *)(param_1 + 0x14c) = 0xffffffff;
        *(undefined4 *)(param_1 + 0x150) = 0;
      }
      uVar3 = *(undefined4 *)(param_1 + 0x28);
      uVar2 = 0xcb100060;
    }
    iVar4 = FUN_005b804c(uVar3,uVar2,param_3);
    iVar5 = 0;
    if (iVar4 != 0 && iVar4 != 0x23) {
      FUN_00442990();
      FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
      return -1;
    }
  }
LAB_0003210c:
  FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
  return iVar5;
}

