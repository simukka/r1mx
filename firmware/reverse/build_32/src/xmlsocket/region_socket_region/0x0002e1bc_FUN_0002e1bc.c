/* 0x0002e1bc  FUN_0002e1bc  size=740 bytes */


undefined4
FUN_0002e1bc(int param_1,undefined4 param_2,int param_3,uint param_4,int param_5,undefined4 param_6,
            int param_7,uint param_8)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 extraout_r4;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  
  if (2 < param_8) {
    return 0xffffffff;
  }
  if (param_1 == 0) {
    puVar2 = (undefined4 *)FUN_00442914();
    uVar1 = 0x38000a;
    goto LAB_0002e248;
  }
  if (param_3 < *(int *)(param_1 + 0x158)) {
LAB_0002e27c:
    if (((uint)(param_5 + param_7) <= *(uint *)(param_1 + 0x160)) && (-1 < param_5 && param_7 != 0))
    {
      uVar6 = FUN_005accf4(*(undefined4 *)(param_1 + 0x138),0xffffffff);
      uVar1 = (undefined4)uVar6;
      if ((int)((ulonglong)uVar6 >> 0x20) != 0) {
        return 0xffffffff;
      }
      if (*(int *)(param_1 + 0x13c) == 0) {
        return 0xffffffff;
      }
      if ((((*(int *)(param_1 + 0x148) != -1) || (*(int *)(param_1 + 0x14c) != -1)) &&
          ((*(int *)(param_1 + 0x148) != param_3 || (*(uint *)(param_1 + 0x14c) != param_4)))) &&
         (*(int *)(param_1 + 0x150) != 0)) {
        uVar4 = *(undefined4 *)(param_1 + 0x148);
        uVar5 = *(undefined4 *)(param_1 + 0x14c);
        *(undefined4 *)(param_1 + 0x148) = 0xffffffff;
        *(undefined4 *)(param_1 + 0x14c) = 0xffffffff;
        *(undefined4 *)(param_1 + 0x150) = 0;
        uVar6 = FUN_0002e05c(param_1,uVar1,uVar4,uVar5,*(undefined4 *)(param_1 + 0x13c),1);
        uVar1 = (undefined4)uVar6;
        if ((int)((ulonglong)uVar6 >> 0x20) == -1) goto LAB_0002e428;
      }
      if (((*(int *)(param_1 + 0x148) != param_3) || (*(uint *)(param_1 + 0x14c) != param_4)) &&
         (*(int *)(param_1 + 0x150) == 0)) {
        if (((param_8 == 0) || (*(int *)(param_1 + 0x160) != param_7)) &&
           (iVar3 = FUN_0002e05c(param_1,uVar1,param_3,param_4,*(undefined4 *)(param_1 + 0x13c),0),
           iVar3 == -1)) goto LAB_0002e428;
        *(int *)(param_1 + 0x148) = param_3;
        *(uint *)(param_1 + 0x14c) = param_4;
        *(undefined4 *)(param_1 + 0x150) = 0;
      }
      param_5 = *(int *)(param_1 + 0x13c) + param_5;
      if (param_8 == 1) {
        FUN_0036c8ac(param_6,param_5,param_7);
        *(undefined4 *)(param_1 + 0x150) = 1;
      }
      else if (param_8 == 0) {
        FUN_0036c8ac(param_5,param_6,param_7);
      }
      else if (param_8 == 2) {
        FUN_0036c8ac(param_6,param_5,param_7);
        iVar3 = FUN_0002e05c(param_1,extraout_r4,param_3,param_4,*(undefined4 *)(param_1 + 0x13c),2)
        ;
        if (iVar3 == -1) {
LAB_0002e428:
          FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
          return 0xffffffff;
        }
        *(int *)(param_1 + 0x148) = param_3;
        *(uint *)(param_1 + 0x14c) = param_4;
        *(undefined4 *)(param_1 + 0x150) = 0;
      }
      FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
      return 0;
    }
  }
  else if (*(int *)(param_1 + 0x158) == param_3) {
    if (*(uint *)(param_1 + 0x15c) <= param_4) {
      puVar2 = (undefined4 *)FUN_00442914();
      uVar1 = 0x16;
      goto LAB_0002e248;
    }
    goto LAB_0002e27c;
  }
  puVar2 = (undefined4 *)FUN_00442914();
  uVar1 = 0x16;
LAB_0002e248:
  *puVar2 = uVar1;
  return 0xffffffff;
}

