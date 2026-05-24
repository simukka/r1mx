/* 0x0002ed80  FUN_0002ed80  size=4016 bytes */


int * FUN_0002ed80(int *param_1,int param_2,int *param_3)

{
  int iVar1;
  undefined4 uVar2;
  int *piVar3;
  undefined4 *puVar4;
  int extraout_r4;
  int extraout_r4_00;
  int extraout_r4_01;
  uint uVar5;
  uint uVar6;
  int *piVar7;
  code *pcVar8;
  undefined4 uVar9;
  int iVar10;
  undefined8 uVar11;
  undefined1 auStack_438 [1040];
  undefined8 uStack_28;
  int iStack_20;
  int *piStack_1c;
  
  uStack_28._0_4_ = 0;
  uStack_28._4_4_ = (int *)0x0;
  if ((param_1 == (int *)0x0 || param_1 == (int *)0xffffffff) ||
     (*(int *)(*param_1 + 0x20) != -0x205368dd)) {
    iVar1 = 0x38000a;
LAB_0002ee00:
    FUN_00442990(iVar1);
    return (int *)0xffffffff;
  }
  piVar7 = (int *)*param_1;
  iVar1 = FUN_005b804c(piVar7[10],0xbd000006,0);
  if (iVar1 != 0 && iVar1 != 0x23) goto LAB_0002ee00;
  uVar11 = FUN_0002b4cc(param_1,0xffffffff);
  uVar9 = (undefined4)uVar11;
  if ((int)((ulonglong)uVar11 >> 0x20) == -1) {
    return (int *)0xffffffff;
  }
  if (param_1[0x11] == 0) goto LAB_0002f020;
  if ((piVar7[9] == 0) || ((*(byte *)(param_1[1] + 8) & 0x40) != 0)) {
    uVar2 = 0x380015;
  }
  else {
    uVar2 = 0x380016;
    if (-1 < *(char *)(param_1[1] + 8)) {
      iVar1 = (int)param_3 >> 0x1f;
      if (param_2 == 0x24) {
        uStack_28._0_4_ = iVar1;
        uStack_28._4_4_ = param_3;
        piVar3 = (int *)FUN_0002d400(param_1,&uStack_28);
        goto LAB_0002ef2c;
      }
      if (param_2 < 0x25) {
        if (param_2 == 8) {
          if (param_1[4] == 0 && param_1[5] == 0) {
            uStack_28._0_4_ = param_1[2];
            uStack_28._4_4_ = (int *)param_1[3];
          }
          else {
            uStack_28._0_4_ = param_1[4];
            uStack_28._4_4_ = (int *)param_1[5];
          }
          iVar1 = FUN_0002b3ec();
          piVar7 = uStack_28._4_4_;
          if (iVar1 == 0) {
            FUN_0002b518(param_1);
            return piVar7;
          }
          uVar9 = 0x380001;
        }
        else {
          if (param_2 < 9) {
            if (param_2 != -0x34efffa0) {
              if (-0x34efffa0 < param_2) {
                if (param_2 == 1) {
                  if (param_1[4] == 0 && param_1[5] == 0) {
                    iVar1 = param_1[2];
                    uVar5 = param_1[3];
                  }
                  else {
                    iVar1 = param_1[4];
                    uVar5 = param_1[5];
                  }
                  piVar7 = (int *)param_1[1];
                  if ((iVar1 < *piVar7) || ((*piVar7 == iVar1 && (uVar5 < (uint)piVar7[1])))) {
                    uVar6 = ((int *)param_1[1])[1];
                    uStack_28._4_4_ = (int *)(uVar6 - uVar5);
                    uStack_28._0_4_ = *(int *)param_1[1] - (iVar1 + (uint)(uVar6 < uVar5));
                  }
                  else {
                    uStack_28._0_4_ = 0;
                    uStack_28._4_4_ = (int *)0x0;
                  }
                  if (param_3 != (int *)0x0) {
                    iVar1 = FUN_0002b3ec();
                    uVar11 = CONCAT44(uStack_28._0_4_,uStack_28._4_4_);
                    if (iVar1 != 0) {
                      FUN_00442990(0x380001);
                      *param_3 = -1;
                      FUN_0002b518(param_1);
                      return (int *)0xffffffff;
                    }
LAB_0002f390:
                    uStack_28._4_4_ = (int *)uVar11;
                    *param_3 = (int)uStack_28._4_4_;
                    uStack_28 = uVar11;
                    FUN_0002b518(param_1);
                    return (int *)0x0;
                  }
                }
                else {
                  if (param_2 < 2) {
                    iVar1 = -0x34efff90;
                    goto LAB_0002ef08;
                  }
                  if (param_2 == 2) {
                    if ((*(char *)(param_1 + 0xb) != '\0') ||
                       (*(char *)((int)param_1 + 0x2d) != '\0')) {
                      piStack_1c = (int *)((-(uint)(*(char *)(param_1 + 0xb) == '\0') & 2) + 4);
                      piVar3 = (int *)(**(code **)(piVar7[0xb] + 8))(param_1,piStack_1c,0);
                      if (piVar3 != (int *)0x0) goto LAB_0002ef2c;
                    }
                    pcVar8 = (code *)piVar7[0x2e];
                    param_3 = (int *)0xcb100010;
                    goto LAB_0002f8dc;
                  }
                  if (param_2 != 7) goto LAB_0002ef8c;
                  uStack_28._0_4_ = iVar1;
                  uStack_28._4_4_ = param_3;
                  if ((*(byte *)(param_1[1] + 0x42) & 0x10) != 0) goto LAB_0002fbb4;
                  if (-1 < (int)param_3) goto LAB_0002f074;
                }
                goto LAB_0002f020;
              }
              if (param_2 != -0x34efffd0) {
                if (param_2 < -0x34efffcf) {
                  iVar1 = -0x34effff0;
                }
                else {
                  iVar1 = -0x34efffb0;
                }
LAB_0002ef08:
                if (param_2 != iVar1) {
LAB_0002ef8c:
                  FUN_0002b518(param_1);
                  iVar1 = FUN_005b804c(piVar7[10],param_2,param_3);
                  if (iVar1 == 0) {
                    return (int *)0x0;
                  }
                  FUN_00442990();
                  return (int *)0xffffffff;
                }
              }
            }
LAB_0002ef18:
            piVar3 = (int *)(*(code *)piVar7[0x2e])(piVar7,param_2,param_3);
LAB_0002ef2c:
            FUN_0002b518(param_1);
            return piVar3;
          }
          if (param_2 == 0x1f) {
            iVar10 = *param_1;
            iVar1 = FUN_0044ec9c(param_3,&iStack_20,auStack_438);
            if (iVar1 == 0) {
              if (iStack_20 == iVar10) {
                iStack_20 = FUN_0002fd30(iVar10,auStack_438,0xa00,0x4000);
                if (iStack_20 != -1) {
                  FUN_0002c680();
                  piVar7 = (int *)0x0;
                  goto LAB_0002f6ac;
                }
              }
              else {
                FUN_00442990(0x380006);
              }
            }
            piVar7 = (int *)0xffffffff;
LAB_0002f6ac:
            FUN_0002b518(param_1);
            return piVar7;
          }
          if (param_2 < 0x20) {
            if (param_2 == 0xf) {
              FUN_0002b518(param_1);
              return (int *)0x0;
            }
            if (param_2 < 0x10) {
              if (param_2 != 10) goto LAB_0002ef8c;
              piVar3 = (int *)FUN_0003097c(param_1,param_3,0);
              goto LAB_0002ef2c;
            }
            if (param_2 == 0x15) {
              piVar3 = (int *)(**(code **)(piVar7[0xc] + 0x24))(param_1);
              if (((piVar3 == (int *)0x0) &&
                  (piVar3 = (int *)(*(code *)piVar7[0x2e])(piVar7,0xcb100010,0),
                  piVar3 == (int *)0x0)) &&
                 (piVar3 = (int *)(*(code *)piVar7[0x2e])(piVar7,0xcb100030,0), piVar3 == (int *)0x0
                 )) {
                puVar4 = (undefined4 *)FUN_00442914();
                uVar9 = *puVar4;
                piVar7 = (int *)FUN_005b804c(piVar7[10],0xbd000002,param_3);
                puVar4 = (undefined4 *)FUN_00442914();
                *puVar4 = uVar9;
                FUN_0002b518(param_1);
                return piVar7;
              }
              goto LAB_0002ef2c;
            }
            if (param_2 != 0x1e) goto LAB_0002ef8c;
            uVar11 = (**(code **)(piVar7[0xc] + 0x10))(param_1);
            uStack_28._0_4_ = (int)((ulonglong)uVar11 >> 0x20);
            uStack_28._4_4_ = (int *)uVar11;
            if (param_3 != (int *)0x0) {
              uStack_28 = uVar11;
              iVar1 = FUN_0002b3ec();
              uVar11 = uStack_28;
              if (iVar1 == 0) goto LAB_0002f390;
              *param_3 = -1;
              goto LAB_0002fcac;
            }
            goto LAB_0002f020;
          }
          if (param_2 == 0x21) {
            piVar3 = (int *)(**(code **)(piVar7[0xb] + 0x10))(piVar7,param_3,0x21);
            goto LAB_0002ef2c;
          }
          if (0x20 < param_2) {
            if (param_2 != 0x22) {
              if (param_2 == 0x23) {
                *(byte *)(param_1[1] + 0x42) =
                     (byte)param_3 & 0x27 | *(byte *)(param_1[1] + 0x42) & 0x18;
                (**(code **)(piVar7[0xb] + 8))(param_1,6,0);
                FUN_0002b518(param_1);
                return (int *)0x0;
              }
              goto LAB_0002ef8c;
            }
            iVar1 = FUN_0002b4cc(param_1,0xffffffff);
            piVar3 = (int *)0xffffffff;
            if (iVar1 != -1) {
              piVar3 = (int *)(**(code **)(piVar7[0xb] + 0x10))(piVar7,param_3,0x22);
              FUN_0002b518(param_1);
LAB_0002f494:
              FUN_0002b518(param_1);
              return piVar3;
            }
            goto LAB_0002ef2c;
          }
          piVar3 = (int *)FUN_0002b410(param_3,&piStack_1c);
          if (((piVar3 == piVar7) || (uVar9 = 0x380006, param_3 == piStack_1c)) &&
             (uVar9 = 0x14, (*(byte *)(param_1[1] + 0x42) & 0x10) != 0)) {
            piVar3 = (int *)FUN_0003083c(piVar7,piStack_1c);
            goto LAB_0002ef2c;
          }
        }
LAB_0002f5b8:
        FUN_00442990(uVar9);
        goto LAB_0002f5c0;
      }
      if (param_2 == 0x31) {
        piVar3 = (int *)FUN_0002d400(param_1,param_3);
        goto LAB_0002ef2c;
      }
      if (param_2 < 0x32) {
        if (param_2 == 0x2b) {
          *param_3 = param_1[0x10] + -1;
          FUN_0002b518(param_1);
          return (int *)0x0;
        }
        if (param_2 < 0x2c) {
          if (param_2 == 0x27) {
            piVar3 = (int *)FUN_0002b564(piVar7);
            goto LAB_0002ef2c;
          }
          if (param_2 < 0x28) {
            if (param_2 != 0x25) goto LAB_0002ef8c;
            piVar3 = (int *)0xffffffff;
            if (param_3 != (int *)0x0) {
              uVar2 = 0x380007;
              if ((*(byte *)(param_1[1] + 0x42) & 0x10) == 0) goto LAB_0002efc8;
              if (param_3[1] == -1) goto LAB_0002ef2c;
              if ((param_1[2] != param_3[1] >> 0x1f) || (param_1[3] != (param_3[1] & 0xfffffffeU)))
              {
                uVar6 = param_3[1];
                uVar5 = uVar6 & 0xfffffffe;
                iVar1 = (int)uVar6 >> 0x1f;
                if ((param_1[2] != iVar1) || (param_1[3] != uVar5)) {
                  if ((*(int *)(param_1[1] + 0x14) == -1) &&
                     (*(int *)(*(int *)(*param_1 + 0x2c) + 0x2c) != 0)) {
                    if ((-1 < iVar1) &&
                       (((int)uVar6 < 0 ||
                        ((uint)(*(int *)(*(int *)(*param_1 + 0x2c) + 0x2c) <<
                               (*(byte *)(*param_1 + 0x84) & 0x3f)) <= uVar5)))) goto LAB_0002f020;
                    param_1[2] = iVar1;
                    param_1[3] = uVar5;
                    FUN_003cc82c(iVar1,uVar5,*(undefined1 *)(*param_1 + 0x84));
                    param_1[6] = *(int *)(*(int *)(*param_1 + 0x2c) + 0x28) + extraout_r4_00;
                    param_1[9] = *(int *)(*(int *)(*param_1 + 0x2c) + 0x2c) - extraout_r4_00;
                  }
                  else {
                    iVar1 = FUN_0002bc4c(param_1,uVar5,iVar1,uVar5);
                    if (iVar1 != 0) {
                      FUN_0002b518(param_1);
                      return (int *)0xffffffff;
                    }
                  }
                }
              }
              pcVar8 = *(code **)(piVar7[0xb] + 4);
              piVar7 = param_1;
              goto LAB_0002f8dc;
            }
          }
          else {
            if (param_2 != 0x29) {
              if (param_2 != 0x2a) goto LAB_0002ef8c;
              piVar3 = (int *)FUN_0002c3e8(param_1,uVar9,iVar1,param_3);
              goto LAB_0002ef2c;
            }
            iVar1 = (**(code **)(piVar7[0xc] + 0x18))(param_1);
            uStack_28._4_4_ = (int *)(iVar1 << (*(byte *)(piVar7 + 0x21) & 0x3f));
            uStack_28._0_4_ = 0;
            iVar1 = FUN_0002b3ec(0,uStack_28._4_4_);
            uVar11 = CONCAT44(uStack_28._0_4_,uStack_28._4_4_);
            if (iVar1 != 0) {
LAB_0002fcac:
              uStack_28 = uVar11;
              FUN_00442990(0x380001);
              goto LAB_0002efcc;
            }
            if (param_3 != (int *)0x0) goto LAB_0002f390;
          }
        }
        else {
          if (param_2 == 0x2e) {
            *param_3 = 0;
            param_3[1] = (uint)*(ushort *)(*param_1 + 0x5e) << (*(byte *)(*param_1 + 0x84) & 0x3f);
            param_3[2] = *(int *)(*param_1 + 100);
            if (*(short *)(*param_1 + 0x5e) != 0) {
              uVar11 = (**(code **)(*(int *)(*param_1 + 0x30) + 0x10))(param_1);
              uVar11 = FUN_003cc82c((int)((ulonglong)uVar11 >> 0x20),(int)uVar11,
                                    *(undefined1 *)(*param_1 + 0x84));
              FUN_003cca2c((int)((ulonglong)uVar11 >> 0x20),(int)uVar11,0,
                           *(undefined2 *)(*param_1 + 0x5e));
              param_3[3] = extraout_r4_01;
            }
            param_3[4] = param_3[3];
            param_3[5] = -1;
            param_3[6] = -1;
            param_3[7] = *(int *)(*param_1 + 0x4c);
            param_3[8] = 0;
            FUN_0002b518(param_1);
            return (int *)0x0;
          }
          if (param_2 < 0x2f) {
            if (param_2 != 0x2c) goto LAB_0002ef8c;
            piVar3 = (int *)0xffffffff;
            if (param_3 != (int *)0x0) {
              if (param_3[1] != 0) {
                piVar3 = (int *)(**(code **)(piVar7[0xb] + 8))(param_1,2,param_3[1]);
              }
              if (*param_3 != 0) {
                piVar3 = (int *)(**(code **)(piVar7[0xb] + 8))(param_1,4,*param_3);
              }
              goto LAB_0002ef2c;
            }
            pcVar8 = *(code **)(piVar7[0xb] + 8);
            param_3 = (int *)0x6;
            piVar7 = param_1;
LAB_0002f8dc:
            piVar3 = (int *)(*pcVar8)(piVar7,param_3,0);
            goto LAB_0002ef2c;
          }
          if (param_2 == 0x2f) {
            piVar3 = (int *)FUN_0003097c(param_1,param_3,1);
            goto LAB_0002ef2c;
          }
          if (param_2 != 0x30) goto LAB_0002ef8c;
          FUN_003cb350(0xd37de0,*(undefined4 *)(*param_1 + 0xc));
          FUN_003cb350(0xd37e04,piVar7[3]);
          piVar3 = (int *)0xffffffff;
          if (iRam00e107f4 == 0) {
            FUN_00442990(0x38000c);
            if (iRam00e1085c != 0) {
              FUN_00443f20(0xd379d8,0,0,0,0,0,0);
              FUN_0002b518(param_1);
              return (int *)0xffffffff;
            }
            goto LAB_0002ef2c;
          }
          if (*(int *)(param_1[1] + 0x14) == -1) {
            iVar1 = FUN_0002b4cc(param_1,0xffffffff);
            if (iVar1 != -1) {
              iVar1 = FUN_005accf4(piVar7[0xd],0xffffffff);
              if (iVar1 != -1) {
                if ((*(byte *)(param_1[1] + 8) >> 6 & 1) == 0) {
                  *(undefined1 *)((int)piVar7 + 0x8e) = 1;
                  FUN_0002b564(piVar7);
                  piVar3 = (int *)FUN_0002ed24(piVar7);
                  *(undefined1 *)((int)piVar7 + 0x8e) = 0;
                  if (piVar3 != (int *)0xffffffff) {
                    *(byte *)(param_1[1] + 8) = *(byte *)(param_1[1] + 8) & 0xbf;
                    piVar3 = (int *)FUN_0002b6d8(param_1,param_3);
                  }
                  FUN_005ad104(piVar7[0xd]);
                }
                else {
                  FUN_00442990(0x380015);
                  FUN_005ad104(piVar7[0xd]);
                }
              }
              FUN_0002b518(param_1);
              goto LAB_0002f494;
            }
            goto LAB_0002ef2c;
          }
        }
      }
      else if (param_2 == 0x36) {
        if (param_3 != (int *)0x0) {
          if (param_1[4] == 0 && param_1[5] == 0) {
            iVar1 = param_1[2];
            iVar10 = param_1[3];
          }
          else {
            iVar1 = param_1[4];
            iVar10 = param_1[5];
          }
          goto LAB_0002f4d0;
        }
      }
      else {
        if (param_2 < 0x37) {
          if (param_2 == 0x33) {
            if (param_3 != (int *)0x0) {
              uVar11 = (**(code **)(piVar7[0xc] + 0x10))(param_1);
              *(undefined8 *)param_3 = uVar11;
LAB_0002f530:
              FUN_0002b518(param_1);
              return (int *)0x0;
            }
          }
          else {
            if (0x32 < param_2) {
              if (param_2 == 0x34) {
                if (param_3 != (int *)0x0) {
                  if (param_1[4] == 0 && param_1[5] == 0) {
                    uStack_28._0_4_ = param_1[2];
                    uStack_28._4_4_ = (int *)param_1[3];
                  }
                  else {
                    uStack_28._0_4_ = param_1[4];
                    uStack_28._4_4_ = (int *)param_1[5];
                  }
                  piVar7 = (int *)param_1[1];
                  if (*piVar7 <= uStack_28._0_4_) {
                    if (*piVar7 != uStack_28._0_4_) {
                      iVar1 = 0;
                      iVar10 = 0;
                      goto LAB_0002f4d0;
                    }
                    if ((int *)piVar7[1] <= uStack_28._4_4_) {
                      iVar1 = 0;
                      iVar10 = 0;
                      goto LAB_0002f4d0;
                    }
                  }
                  piVar7 = (int *)((int *)param_1[1])[1];
                  iVar10 = (int)piVar7 - (int)uStack_28._4_4_;
                  iVar1 = *(int *)param_1[1] - (uStack_28._0_4_ + (uint)(piVar7 < uStack_28._4_4_));
LAB_0002f4d0:
                  *param_3 = iVar1;
                  param_3[1] = iVar10;
                  FUN_0002b518(param_1);
                  return (int *)0x0;
                }
              }
              else {
                if (param_2 != 0x35) goto LAB_0002ef8c;
                if ((*(byte *)(param_1[1] + 0x42) & 0x10) != 0) {
LAB_0002fbb4:
                  FUN_00442990(0x380005);
                  goto LAB_0002efcc;
                }
                if (param_3 != (int *)0x0) {
                  iVar1 = *param_3;
                  param_3 = (int *)param_3[1];
LAB_0002f074:
                  piVar3 = (int *)FUN_0002bc4c(param_1,uVar9,iVar1,param_3);
                  goto LAB_0002ef2c;
                }
              }
              goto LAB_0002f020;
            }
            if (param_3 != (int *)0x0) {
              uVar9 = (**(code **)(piVar7[0xc] + 0x18))(param_1);
              uVar11 = FUN_003cc7cc(0,uVar9,*(undefined1 *)(piVar7 + 0x21));
              *(undefined8 *)param_3 = uVar11;
              goto LAB_0002f530;
            }
          }
          FUN_00442990(0x38000a);
LAB_0002f5c0:
          FUN_0002b518(param_1);
          return (int *)0xffffffff;
        }
        if (param_2 == 0x38) {
          param_2 = -0x34efff90;
          goto LAB_0002ef18;
        }
        if (0x37 < param_2) {
          if (param_2 != 0x3b) {
            if (param_2 != 0x40) goto LAB_0002ef8c;
            piVar7 = (int *)param_1[1];
            iVar10 = *param_1;
            memset(param_3,0x48);
            *param_3 = iVar10;
            param_3[3] = 1;
            iVar1 = piVar7[1];
            param_3[6] = *piVar7;
            param_3[7] = iVar1;
            piVar3 = (int *)0xffffffff;
            param_3[0xb] = (uint)*(ushort *)(iVar10 + 0x5e) << (*(byte *)(iVar10 + 0x84) & 0x3f);
            if (param_3[0xb] != 0) {
              uVar5 = param_3[0xb] - 1;
              FUN_003cca2c(param_3[6] + ((int)uVar5 >> 0x1f) + (uint)CARRY4(param_3[7],uVar5),
                           param_3[7] + uVar5,param_3[0xb] >> 0x1f,param_3[0xb]);
              param_3[0xc] = extraout_r4;
              *(undefined1 *)(param_3 + 0xd) = *(undefined1 *)((int)piVar7 + 0x42);
              param_3[2] = 0x1ff;
              if ((*(byte *)((int)piVar7 + 0x42) & 1) != 0) {
                param_3[2] = param_3[2] & 0xffffff6d;
              }
              if ((*(byte *)((int)piVar7 + 0x42) & 0x10) == 0) {
                param_3[2] = param_3[2] | 0x8000;
              }
              else {
                param_3[2] = param_3[2] | 0x4000;
                param_3[6] = param_3[0xb] >> 0x1f;
                param_3[7] = param_3[0xb];
              }
              iVar1 = (**(code **)(*(int *)(iVar10 + 0x2c) + 0xc))(param_1,param_3);
              piVar3 = (int *)-(uint)(iVar1 == -1);
            }
            goto LAB_0002ef2c;
          }
          uVar9 = 0x380011;
          if ((*(byte *)(param_1[1] + 0x42) & 1) == 0) {
            piVar3 = (int *)FUN_0002c92c(param_1);
            goto LAB_0002ef2c;
          }
          goto LAB_0002f5b8;
        }
        if (param_3 != (int *)0x0) {
          piVar3 = (int *)FUN_0002c3e8(param_1,uVar9,*param_3,param_3[1]);
          goto LAB_0002ef2c;
        }
      }
LAB_0002f020:
      FUN_00442990(0x38000a);
      goto LAB_0002efcc;
    }
  }
LAB_0002efc8:
  FUN_00442990(uVar2);
LAB_0002efcc:
  FUN_0002b518(param_1);
  return (int *)0xffffffff;
}

