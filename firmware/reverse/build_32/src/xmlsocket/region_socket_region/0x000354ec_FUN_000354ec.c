/* 0x000354ec  FUN_000354ec  size=1404 bytes */


int FUN_000354ec(int param_1,undefined4 param_2,int param_3,uint param_4,uint param_5,uint param_6,
                int param_7)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 extraout_r4;
  int iVar4;
  undefined4 extraout_r4_00;
  undefined4 extraout_r4_01;
  undefined4 extraout_r4_02;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  uint uVar13;
  bool bVar14;
  undefined8 uVar15;
  
  iVar7 = param_1 + 0xe8;
  if (*(int *)(param_1 + 0xbc) == 0) {
    iVar7 = FUN_00031524();
  }
  else if ((0 < (int)param_5) || ((param_5 == 0 && (param_6 != 0)))) {
    if ((param_3 <= *(int *)(param_1 + 0x158)) &&
       ((*(int *)(param_1 + 0x158) != param_3 || (param_4 <= *(uint *)(param_1 + 0x15c))))) {
      iVar9 = param_3 + param_5 + (uint)CARRY4(param_4,param_6);
      if ((iVar9 <= *(int *)(param_1 + 0x158)) &&
         ((*(int *)(param_1 + 0x158) != iVar9 || (param_4 + param_6 <= *(uint *)(param_1 + 0x15c))))
         ) {
        uVar15 = FUN_005accf4(*(undefined4 *)(param_1 + 0x138),0xffffffff);
        uVar12 = (undefined4)uVar15;
        if ((int)((ulonglong)uVar15 >> 0x20) != 0) {
          return -1;
        }
        if (((int)param_5 < 1) && ((param_5 != 0 || (param_6 <= *(uint *)(param_1 + 0xdc))))) {
          uVar8 = 0;
LAB_000355e8:
          if (0 < (int)param_5) goto LAB_00035600;
          do {
            if ((param_5 != 0) || (param_6 <= uVar8)) {
              FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
              return 0;
            }
LAB_00035600:
            iVar1 = FUN_00034310(param_1,uVar12,param_3 + (uint)CARRY4(uVar8,param_4),
                                 uVar8 + param_4);
            while( true ) {
              if (iVar1 == 0) {
                uVar13 = uVar8 + param_4;
                iVar1 = param_3 + (uint)CARRY4(uVar8,param_4);
                if (((int)(param_5 - (param_6 < uVar8)) < 0) ||
                   ((param_5 == param_6 < uVar8 && (param_6 - uVar8 < *(uint *)(param_1 + 0x128)))))
                {
                  uVar10 = *(uint *)(param_1 + 0x128);
                  uVar6 = *(uint *)(param_1 + 0x15c) - uVar13;
                  iVar2 = iVar1 + (uint)(*(uint *)(param_1 + 0x15c) < uVar13);
                  iVar5 = *(int *)(param_1 + 0x158) - iVar2;
                  bVar14 = *(int *)(param_1 + 0x158) == iVar2;
                }
                else {
                  uVar6 = *(uint *)(param_1 + 0x15c) - uVar13;
                  iVar2 = iVar1 + (uint)(*(uint *)(param_1 + 0x15c) < uVar13);
                  iVar5 = *(int *)(param_1 + 0x158) - iVar2;
                  bVar14 = *(int *)(param_1 + 0x158) == iVar2;
                  uVar10 = param_6 - uVar8;
                }
                if ((iVar5 < 1) && ((!bVar14 || (uVar6 <= uVar10)))) {
                  uVar10 = *(int *)(param_1 + 0x15c) - uVar13;
                }
                iVar2 = FUN_0045b9e4(uRam00e295c4,*(int *)(param_1 + 0x160) * uVar10,0x20);
                if (iVar2 == 0) goto LAB_00035a24;
                uVar11 = *(undefined4 *)(param_1 + 0xfc);
                *(int *)(param_1 + 0xfc) = iVar2;
                uVar15 = FUN_00034758(param_1,iVar7,iVar1,uVar13,*(int *)(param_1 + 0x160) * uVar10,
                                      1);
                iVar4 = (int)((ulonglong)uVar15 >> 0x20);
                uVar12 = (undefined4)uVar15;
                *(undefined4 *)(param_1 + 0xfc) = uVar11;
                iVar5 = iVar2;
                if (iVar4 == 0) goto joined_r0x000357c8;
                FUN_0045b5e4(uRam00e295c4,iVar2);
                goto LAB_0003593c;
              }
              *(int *)(param_1 + 0x130) = *(int *)(param_1 + 0x130) + 1;
              FUN_0036c8ac(*(undefined4 *)(iVar1 + 0x10),*(int *)(param_1 + 0x160) * uVar8 + param_7
                           ,*(undefined4 *)(param_1 + 0x160));
              uVar8 = uVar8 + 1;
              uVar12 = extraout_r4;
              if ((int)param_5 < 1) break;
              iVar1 = FUN_00034310(param_1,extraout_r4,param_3 + (uint)CARRY4(uVar8,param_4),
                                   uVar8 + param_4);
            }
          } while( true );
        }
        iVar4 = FUN_00034834(param_1);
        if (iVar4 == 0) {
          if ((*(uint *)(param_1 + 0x124) & 1) == 0) {
            uVar8 = 0;
            if ((0 < (int)param_5) || ((param_5 == 0 && (param_6 != 0)))) {
              while( true ) {
                if ((0 < (int)param_5) ||
                   ((uVar13 = param_6, param_5 == 0 && (*(uint *)(param_1 + 0x120) < param_6)))) {
                  uVar13 = *(uint *)(param_1 + 0x120);
                }
                iVar1 = *(int *)(param_1 + 0x160) * uVar13;
                iVar9 = FUN_00034758(param_1,iVar7,param_3 + (uint)CARRY4(uVar8,param_4),
                                     uVar8 + param_4,iVar1,1);
                iVar2 = param_7 + iVar1;
                uVar8 = uVar8 + uVar13;
                if (iVar9 != 0) break;
                FUN_0036c8ac(*(undefined4 *)(param_1 + 0xfc));
                bVar14 = param_6 < uVar13;
                param_6 = param_6 - uVar13;
                param_5 = param_5 - bVar14;
                param_7 = iVar2;
                if (((int)param_5 < 1) && ((param_5 != 0 || (param_6 == 0)))) goto LAB_0003593c;
              }
              if (iVar9 != -1) {
                FUN_00442990(iVar9,param_7,iVar1);
              }
              iVar4 = -1;
            }
          }
          else {
            uVar12 = *(undefined4 *)(param_1 + 0xfc);
            *(int *)(param_1 + 0xfc) = param_7;
            iVar4 = FUN_00034758(param_1,iVar7,param_3,param_4,*(int *)(param_1 + 0x160) * param_6,1
                                );
            *(undefined4 *)(param_1 + 0xfc) = uVar12;
          }
        }
LAB_0003593c:
        FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
        return iVar4;
      }
    }
    puVar3 = (undefined4 *)FUN_00442914();
    iVar7 = -1;
    *puVar3 = 0x16;
  }
  else {
    iVar7 = 0;
  }
  return iVar7;
joined_r0x000357c8:
  for (; uVar10 != 0; uVar10 = uVar10 - 1) {
    uVar15 = FUN_00034310(param_1,uVar12,iVar1,uVar13);
    if ((int)((ulonglong)uVar15 >> 0x20) == 0) {
      *(int *)(param_1 + 0x134) = *(int *)(param_1 + 0x134) + 1;
      iVar4 = FUN_00034d68(param_1,(int)uVar15,iVar1,uVar13,0);
      if (iVar4 == 0) {
        FUN_003cb350(0xd38830,param_1,0x44a);
        FUN_0045b5e4(uRam00e295c4,iVar2);
LAB_00035a24:
        FUN_005ad104(*(undefined4 *)(param_1 + 0x138));
        return -1;
      }
      FUN_0036c8ac(iVar5,*(undefined4 *)(iVar4 + 0x10),*(undefined4 *)(param_1 + 0x160));
      uVar15 = CONCAT44(iVar4,extraout_r4_02);
    }
    else {
      *(int *)(param_1 + 0x130) = *(int *)(param_1 + 0x130) + 1;
    }
    uVar12 = (undefined4)uVar15;
    if ((iVar1 < iVar9) || ((iVar9 == iVar1 && (uVar13 < param_4 + param_6)))) {
      iVar4 = *(int *)(param_1 + 0x160) * uVar8;
      uVar8 = uVar8 + 1;
      FUN_0036c8ac(*(undefined4 *)((int)((ulonglong)uVar15 >> 0x20) + 0x10),iVar4 + param_7,
                   *(undefined4 *)(param_1 + 0x160));
      uVar12 = extraout_r4_00;
    }
    bVar14 = 0xfffffffe < uVar13;
    uVar13 = uVar13 + 1;
    iVar1 = iVar1 + (uint)bVar14;
    iVar5 = iVar5 + *(int *)(param_1 + 0x160);
  }
  FUN_0045b5e4(uRam00e295c4,iVar2);
  uVar12 = extraout_r4_01;
  goto LAB_000355e8;
}

