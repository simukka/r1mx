/* 0x0002e4a0  FUN_0002e4a0  size=2180 bytes */


undefined4 FUN_0002e4a0(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined2 uVar6;
  int iVar7;
  undefined8 uVar8;
  byte abStack_238 [11];
  undefined1 uStack_22d;
  undefined1 uStack_22c;
  byte bStack_22b;
  undefined1 uStack_22a;
  undefined1 uStack_229;
  undefined1 uStack_228;
  undefined1 uStack_225;
  undefined1 uStack_224;
  undefined1 uStack_222;
  undefined1 uStack_221;
  undefined1 uStack_21c;
  undefined1 uStack_21b;
  byte bStack_218;
  byte bStack_217;
  byte bStack_216;
  byte bStack_215;
  byte bStack_214;
  byte bStack_213;
  byte bStack_212;
  byte bStack_211;
  undefined1 auStack_202 [456];
  char cStack_3a;
  char cStack_39;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined1 uStack_30;
  int iStack_28;
  uint uStack_24;
  uint uStack_20;
  undefined4 uStack_1c;
  
  uVar1 = FUN_00442920();
  if ((param_1 == 0) || (*(int *)(param_1 + 0x20) != -0x205368dd)) {
    FUN_00442990(0x38000a);
    return 0xffffffff;
  }
  iVar2 = FUN_005accf4(*(undefined4 *)(param_1 + 0x34),0xffffffff);
  if (iVar2 == -1) {
    return 0xffffffff;
  }
  if (*(int *)(param_1 + 0x24) == 1) {
    FUN_0002b564(param_1);
  }
  *(undefined4 *)(param_1 + 0x24) = 0;
  FUN_00442990(0);
  FUN_0039acec(abStack_238,0,0x200);
  *(undefined4 *)(param_1 + 0x48) = 0;
  uStack_38 = 0;
  uStack_34 = 0;
  uStack_30 = 0;
  iVar2 = FUN_005b8250(*(undefined4 *)(param_1 + 0x28),&iStack_28);
  if ((iVar2 != 0) || (iVar2 = FUN_005b82ac(*(undefined4 *)(param_1 + 0x28),&uStack_20), iVar2 != 0)
     ) goto LAB_0002e6a0;
  if (uStack_20 == 0) {
    uVar1 = 0xd37b34;
joined_r0x0002e6dc:
    if (uRam00e1085c != 0) {
LAB_0002e6e0:
      uStack_24 = 0;
      uStack_20 = 0;
LAB_0002e6e8:
      FUN_00443f20(uVar1,uStack_20,uStack_24,0,0,0,0);
    }
  }
  else {
    uStack_1c = uStack_20;
    if (0x200 < uStack_20) {
      uStack_1c = 0x200;
    }
    uVar8 = FUN_0002e1bc(param_1,uStack_1c,0,*(undefined4 *)(param_1 + 0x48),0,abStack_238,uStack_1c
                         ,0);
    if ((int)((ulonglong)uVar8 >> 0x20) == -1) {
      if (uRam00e1085c != 0) {
        FUN_00443f20(0xd37bf4,0,0,0,0,0,0);
      }
      uVar1 = 0xd37b68;
      goto joined_r0x0002e6dc;
    }
    uVar4 = (uint)abStack_238[0];
    if ((uVar4 == 0xe9) || (uVar4 == 0xeb)) {
      iVar2 = FUN_0002e1bc(param_1,(int)uVar8,0,*(undefined4 *)(param_1 + 0x48),uStack_20 - 2,
                           &uStack_1c,2,0);
      if (iVar2 == -1) {
        uVar1 = 0xd37b9c;
joined_r0x0002ea50:
        if (uRam00e1085c == 0) goto LAB_0002e688;
        goto LAB_0002e6e0;
      }
      uVar4 = (uint)CONCAT11(uStack_1c._1_1_,uStack_1c._0_1_);
      if ((uVar4 != 0xaa55) && ((cStack_3a != 'U' || (cStack_39 != -0x56)))) {
        iVar2 = uStack_20 - 2;
        uVar1 = 0xd37b18;
        uVar5 = 0x603;
        uStack_1c = uVar4;
        goto LAB_0002e684;
      }
      uStack_1c = (uint)CONCAT11(uStack_22c,uStack_22d);
      *(ushort *)(param_1 + 0x5c) = CONCAT11(uStack_22c,uStack_22d);
      if (uStack_1c == 0) {
        FUN_0002b7fc(1,0xb,0,0,0x616);
        uVar1 = 0xd37c28;
        goto joined_r0x0002ea50;
      }
      if (uStack_1c == uStack_20) {
        *(undefined1 *)(param_1 + 0x84) = 0;
        uStack_1c = 5;
        do {
          uVar4 = uStack_1c + 1;
          if (1 << (uStack_1c & 0x3f) == (uint)*(ushort *)(param_1 + 0x5c)) {
            *(char *)(param_1 + 0x84) = (char)uStack_1c;
            break;
          }
          uStack_1c = uVar4;
        } while (uVar4 < 0x10);
        if (*(char *)(param_1 + 0x84) == '\0') {
          uVar4 = (uint)*(ushort *)(param_1 + 0x5c);
          iVar2 = 0xb;
          uVar1 = 0;
          uVar5 = 0x637;
        }
        else {
          uStack_1c = (uint)CONCAT11(uStack_224,uStack_225);
          if (uStack_1c == 0) {
            uStack_1c = (uint)bStack_215 << 0x18 | (uint)bStack_216 << 0x10 | (uint)bStack_217 << 8
                        | (uint)bStack_218;
            if (uStack_1c == 0) {
              iVar2 = 0x20;
              uVar4 = 0;
              uVar1 = 0;
              uVar5 = 0x64b;
              goto LAB_0002e684;
            }
          }
          else {
          }
          *(uint *)(param_1 + 0x58) = uStack_1c;
          if ((iStack_28 != 0) || (uStack_24 != uStack_1c)) {
            if ((iStack_28 < 1) && ((iStack_28 != 0 || (uStack_24 <= uStack_1c)))) {
              FUN_0002b7fc(1,0x20,0,0,0x66c);
              if (uRam00e1085c != 0) {
                uVar1 = 0xd37c48;
                uStack_20 = uStack_1c;
                goto LAB_0002e6e8;
              }
              goto LAB_0002e688;
            }
            if (9 < uRam00e1085c) {
              FUN_00443f20(0xd37c74,uStack_1c,uStack_24,0,0,0,0);
            }
          }
          *(ushort *)(param_1 + 0x5e) = (ushort)bStack_22b;
          if (*(short *)(param_1 + 0x5e) == 0) {
            iVar2 = 0xd;
            uVar4 = 0;
            uVar1 = 0;
            uVar5 = 0x679;
          }
          else {
            *(undefined1 *)(param_1 + 0x62) = uStack_228;
            if (*(char *)(param_1 + 0x62) == '\0') {
              iVar2 = 0x10;
              uVar4 = 0;
              uVar1 = 0;
              uVar5 = 0x683;
            }
            else {
              *(uint *)(param_1 + 0x54) = (uint)CONCAT11(uStack_21b,uStack_21c);
              *(ushort *)(param_1 + 0x60) = CONCAT11(uStack_229,uStack_22a);
              if (*(short *)(param_1 + 0x60) == 0) {
                iVar2 = 0xe;
                uVar4 = 0;
                uVar1 = 0;
                uVar5 = 0x691;
              }
              else {
                *(uint *)(param_1 + 0x50) = (uint)CONCAT11(uStack_221,uStack_222);
                if (*(int *)(param_1 + 0x50) != 0) {
                  if (*(uint *)(param_1 + 0x50) <= 0x20000 / *(ushort *)(param_1 + 0x5c)) {
                    FUN_0036c8ac(auStack_202,&uStack_38,8);
                    uStack_1c = FUN_0002b858(abStack_238);
                    if (uStack_1c != 0xffffffff) {
                      if (uStack_1c == 1) {
                        iVar2 = FUN_0039ad64(&uStack_38,0xd37d44);
                        uVar5 = 0;
                        if (iVar2 != 0) goto LAB_0002e8d4;
                        *(undefined4 *)(param_1 + 0x74) = 1;
                        FUN_003cb350(0xd37d50);
                      }
                      else {
                        iVar2 = FUN_0039ad64(&uStack_38,0xd37b5c);
                        if (iVar2 == 0) {
                          *(undefined4 *)(param_1 + 0x74) = 0;
                          FUN_003cb350(0xd37cdc);
                        }
                        else {
                          uVar5 = 1;
LAB_0002e8d4:
                          *(undefined4 *)(param_1 + 0x74) = uVar5;
                        }
                      }
                      *(undefined2 *)(param_1 + 0x80) = 0x27;
                      uVar6 = 0x2b;
LAB_0002e8e4:
                      *(undefined2 *)(param_1 + 0x82) = uVar6;
                      *(uint *)(param_1 + 0x78) =
                           (uint)*(ushort *)(param_1 + 0x60) +
                           *(int *)(param_1 + 0x50) * (uint)*(byte *)(param_1 + 0x62);
                      *(uint *)(param_1 + 0x4c) =
                           (uint)abStack_238[*(ushort *)(param_1 + 0x80) + 3] << 0x18 |
                           (uint)abStack_238[*(ushort *)(param_1 + 0x80) + 2] << 0x10 |
                           (uint)abStack_238[*(ushort *)(param_1 + 0x80) + 1] << 8 |
                           (uint)abStack_238[*(ushort *)(param_1 + 0x80)];
                      iVar7 = 0;
                      FUN_0036c8ac(abStack_238 + *(ushort *)(param_1 + 0x82),param_1 + 0x68,0xb);
                      *(undefined1 *)(param_1 + 0x73) = 0;
                      iVar2 = 0xe107f8;
                      do {
                        if ((*(code **)(iVar2 + 4) != reset_vector) &&
                           (iVar3 = (**(code **)(iVar2 + 4))(param_1,*(undefined4 *)(iVar2 + 8)),
                           iVar3 == 0)) break;
                        iVar7 = iVar7 + 1;
                        iVar2 = iVar2 + 0xc;
                      } while (iVar7 < 4);
                      if (iVar7 == 4) {
                        return 0xffffffff;
                      }
                      iVar2 = 0xe10828;
                      iVar7 = 0;
                      do {
                        if ((*(code **)(iVar2 + 4) != reset_vector) &&
                           (iVar3 = (**(code **)(iVar2 + 4))(param_1,*(undefined4 *)(iVar2 + 8)),
                           iVar3 == 0)) break;
                        iVar7 = iVar7 + 1;
                        iVar2 = iVar2 + 0xc;
                      } while (iVar7 < 4);
                      if (iVar7 != 4) {
                        FUN_00442990(uVar1);
                        *(undefined4 *)(param_1 + 0x24) = 1;
                        return 0;
                      }
                      return 0xffffffff;
                    }
                    uStack_1c = 0xffffffff;
                    if (uRam00e1085c == 0) goto LAB_0002e688;
                    uVar1 = 0xd37db0;
                    goto LAB_0002e6e0;
                  }
                  FUN_0002b7fc(1,0x16,*(undefined4 *)(param_1 + 0x50),0,0x6ab);
                  if (uRam00e1085c != 0) {
                    uStack_24 = (uint)*(ushort *)(param_1 + 0x5c);
                    uVar1 = 0xd37ca8;
                    uStack_20 = *(uint *)(param_1 + 0x50);
                    goto LAB_0002e6e8;
                  }
                  goto LAB_0002e688;
                }
                *(undefined4 *)(param_1 + 0x74) = 2;
                *(uint *)(param_1 + 0x50) =
                     (uint)bStack_211 << 0x18 | (uint)bStack_212 << 0x10 | (uint)bStack_213 << 8 |
                     (uint)bStack_214;
                if (*(int *)(param_1 + 0x50) != 0) {
                  uVar6 = 0x47;
                  *(undefined2 *)(param_1 + 0x80) = 0x43;
                  goto LAB_0002e8e4;
                }
                uVar1 = 0xd37d3c;
                iVar2 = 0x24;
                uVar4 = 0;
                uVar5 = 0x70d;
              }
            }
          }
        }
        goto LAB_0002e684;
      }
      FUN_0002b7fc(1,0xb,uStack_1c,0,0x61d);
      if (uRam00e1085c == 0) goto LAB_0002e688;
      uVar1 = 0xd37bc4;
      uStack_24 = uStack_1c;
      goto LAB_0002e6e8;
    }
    iVar2 = 0;
    uVar1 = 0;
    uVar5 = 0x5df;
LAB_0002e684:
    FUN_0002b7fc(1,iVar2,uVar4,uVar1,uVar5);
  }
LAB_0002e688:
  iVar2 = FUN_00442920();
  if (iVar2 == 0) {
    FUN_00442990(0x38001c);
  }
LAB_0002e6a0:
  iVar2 = FUN_00442920();
  if (iVar2 == 0) {
    FUN_00442990(0x38001c);
  }
  return 0xffffffff;
}

