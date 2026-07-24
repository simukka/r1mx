/* 0x0002c014  FUN_0002c014  size=980 bytes */


undefined4 FUN_0002c014(int *param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int *piVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  
  iVar8 = *param_1;
  piVar7 = (int *)param_1[1];
  iVar9 = param_1[4];
  uVar10 = param_1[5];
  iVar1 = FUN_0002bc4c(param_1,param_2,*piVar7,piVar7[1]);
  uVar2 = 0xffffffff;
  if (iVar1 != -1) {
    uVar3 = *(ushort *)(iVar8 + 0x5c) - 1;
    uVar5 = param_1[3] & uVar3;
    iVar1 = -((param_1[2] & (int)uVar3 >> 0x1f) + (uint)(*(ushort *)(iVar8 + 0x5c) < uVar5));
    iVar4 = iVar9 - (param_1[2] + (uint)(uVar10 < (uint)param_1[3]));
    if ((iVar1 <= iVar4) &&
       ((iVar1 != iVar4 || (*(ushort *)(iVar8 + 0x5c) - uVar5 <= uVar10 - param_1[3])))) {
      if (((0 < *piVar7) || ((*piVar7 == 0 && (piVar7[1] != 0)))) &&
         ((uVar3 = *(ushort *)(iVar8 + 0x5c) - 1,
          (param_1[2] & (int)uVar3 >> 0x1f) != 0 || (param_1[3] & uVar3) != 0 && (param_1[9] != 0)))
         ) {
        param_1[9] = param_1[9] + -1;
        param_1[6] = param_1[6] + 1;
        uVar5 = *(ushort *)(iVar8 + 0x5c) - 1;
        uVar3 = param_1[3] & uVar5;
        iVar1 = -((param_1[2] & (int)uVar5 >> 0x1f) + (uint)(*(ushort *)(iVar8 + 0x5c) < uVar3));
        iVar4 = iVar9 - (param_1[2] + (uint)(uVar10 < (uint)param_1[3]));
        if ((iVar4 < iVar1) ||
           ((iVar1 == iVar4 && (uVar10 - param_1[3] < *(ushort *)(iVar8 + 0x5c) - uVar3)))) {
          uVar3 = uVar10 - param_1[3];
          iVar1 = iVar9 - (param_1[2] + (uint)(uVar10 < (uint)param_1[3]));
        }
        else {
          uVar5 = *(ushort *)(iVar8 + 0x5c) - 1;
          uVar6 = param_1[3] & uVar5;
          uVar3 = *(ushort *)(iVar8 + 0x5c) - uVar6;
          iVar1 = -((param_1[2] & (int)uVar5 >> 0x1f) + (uint)(*(ushort *)(iVar8 + 0x5c) < uVar6));
        }
        param_1[2] = param_1[2] + iVar1 + (uint)CARRY4(param_1[3],uVar3);
        param_1[3] = param_1[3] + uVar3;
        iVar1 = param_1[3];
        *piVar7 = param_1[2];
        piVar7[1] = iVar1;
      }
      if (param_1[2] < iVar9) {
        do {
          do {
            if (((param_1[9] == 0) &&
                (iVar1 = (*(code *)**(undefined4 **)(iVar8 + 0x30))(param_1,param_2), iVar1 == -1))
               || (iVar1 = (**(code **)(iVar8 + 0xb8))(iVar8,0xcb100050,param_1[6]), iVar1 == -1)) {
              return 0xffffffff;
            }
            uVar3 = param_1[3];
            iVar1 = param_1[2] + (uint)(uVar10 < (uint)param_1[3]);
            if ((iVar9 - iVar1 < 0) ||
               ((iVar9 == iVar1 && (uVar10 - param_1[3] < (uint)*(ushort *)(iVar8 + 0x5c))))) {
              uVar5 = uVar10 - param_1[3];
              iVar1 = param_1[2] + (iVar9 - (param_1[2] + (uint)(uVar10 < (uint)param_1[3]))) +
                      (uint)CARRY4(uVar3,uVar5);
            }
            else {
              uVar5 = (uint)*(ushort *)(iVar8 + 0x5c);
              iVar1 = param_1[2] + (uint)CARRY4(uVar5,uVar3);
            }
            param_1[2] = iVar1;
            param_1[3] = uVar3 + uVar5;
            iVar1 = param_1[3];
            *piVar7 = param_1[2];
            piVar7[1] = iVar1;
            uVar3 = *(ushort *)(iVar8 + 0x5c) - 1;
            if ((param_1[2] & (int)uVar3 >> 0x1f) == 0 && (param_1[3] & uVar3) == 0) {
              param_1[6] = param_1[6] + 1;
              param_1[9] = param_1[9] + -1;
            }
          } while (param_1[2] < iVar9);
          if (param_1[2] != iVar9) {
            return 0;
          }
LAB_0002c248:
        } while ((uint)param_1[3] < uVar10);
      }
      else if (param_1[2] == iVar9) goto LAB_0002c248;
      return 0;
    }
    *piVar7 = iVar9;
    uVar2 = 0;
    piVar7[1] = uVar10;
    param_1[2] = iVar9;
    param_1[3] = uVar10;
  }
  return uVar2;
}

