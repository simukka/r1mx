/* 0x00031524  FUN_00031524  size=844 bytes */


undefined4
FUN_00031524(int param_1,undefined4 param_2,int param_3,uint param_4,int param_5,uint param_6,
            int param_7)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  bool bVar9;
  undefined8 uVar10;
  
  if (param_1 == 0) {
    puVar4 = (undefined4 *)FUN_00442914();
    uVar5 = 0x38000a;
  }
  else {
    bVar9 = param_5 < 0;
    bVar1 = param_5 == 0;
    if ((param_5 < 1) && ((!bVar1 || (param_6 == 0)))) {
      return 0;
    }
    if ((param_3 <= *(int *)(param_1 + 0x158)) &&
       ((*(int *)(param_1 + 0x158) != param_3 || (param_4 <= *(uint *)(param_1 + 0x15c))))) {
      iVar8 = param_3 + param_5 + (uint)CARRY4(param_4,param_6);
      if ((iVar8 <= *(int *)(param_1 + 0x158)) &&
         ((*(int *)(param_1 + 0x158) != iVar8 || (param_4 + param_6 <= *(uint *)(param_1 + 0x15c))))
         ) {
        uVar10 = FUN_005accf4(*(undefined4 *)(param_1 + 0x138),0xffffffff);
        if ((int)((ulonglong)uVar10 >> 0x20) != 0) {
          return 0xffffffff;
        }
        if (((param_3 <= *(int *)(param_1 + 0x148)) &&
            ((*(int *)(param_1 + 0x148) != param_3 || (param_4 <= *(uint *)(param_1 + 0x14c))))) &&
           ((*(int *)(param_1 + 0x148) < iVar8 ||
            ((*(int *)(param_1 + 0x148) == iVar8 && (*(uint *)(param_1 + 0x14c) < param_4 + param_6)
             ))))) {
          if ((bVar1) && (param_6 == 1)) {
            FUN_0036c8ac(*(undefined4 *)(param_1 + 0x13c),param_7,*(undefined4 *)(param_1 + 0x160));
            FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
            return 0;
          }
          if (*(int *)(param_1 + 0x150) != 0) {
            iVar8 = FUN_0002e05c(param_1,(int)uVar10,*(undefined4 *)(param_1 + 0x148),
                                 *(undefined4 *)(param_1 + 0x14c),*(undefined4 *)(param_1 + 0x13c),1
                                );
            if (iVar8 != 0) {
              FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
              return 0xffffffff;
            }
            *(undefined4 *)(param_1 + 0x150) = 0;
          }
        }
        uVar5 = 0;
        FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
        iVar8 = FUN_0002de44(param_1);
        if (iVar8 == 0) {
          return 0xffffffff;
        }
        uVar6 = 0;
        if (param_5 < 1) {
          if (bVar1) goto LAB_000316b8;
        }
        else {
          do {
            do {
              if ((bVar9) || ((bVar1 && (param_6 < 0x20)))) {
                iVar7 = *(int *)(param_1 + 0x160) * param_6;
                iVar3 = FUN_0002dfd0(param_1,iVar8,param_3 + (uint)CARRY4(uVar6,param_4),
                                     uVar6 + param_4,iVar7,1);
                uVar2 = param_6;
              }
              else {
                iVar7 = *(int *)(param_1 + 0x160) * 0x20;
                iVar3 = FUN_0002dfd0(param_1,iVar8,param_3 + (uint)CARRY4(uVar6,param_4),
                                     uVar6 + param_4,iVar7,1);
                uVar2 = 0x20;
              }
              if (iVar3 != 0) {
                if (iVar3 != -1) {
                  FUN_00442990(iVar3,param_7,iVar7);
                }
                uVar5 = 0xffffffff;
                goto LAB_000316bc;
              }
              param_7 = param_7 + iVar7;
              uVar6 = uVar6 + uVar2;
              FUN_0036c8ac(*(undefined4 *)(iVar8 + 0x14));
              bVar9 = param_6 < uVar2;
              param_6 = param_6 - uVar2;
              param_5 = param_5 - (uint)bVar9;
              bVar9 = param_5 < 0;
              bVar1 = param_5 == 0;
            } while (0 < param_5);
            if (!bVar1) break;
LAB_000316b8:
          } while (param_6 != 0);
        }
LAB_000316bc:
        FUN_0002df3c(param_1,iVar8);
        return uVar5;
      }
    }
    puVar4 = (undefined4 *)FUN_00442914();
    uVar5 = 0x16;
  }
  *puVar4 = uVar5;
  return 0xffffffff;
}

