/* 0x0003236c  FUN_0003236c  size=1476 bytes */


undefined4 FUN_0003236c(uint *param_1,uint param_2,int param_3)

{
  uint uVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  undefined1 uVar6;
  uint uVar5;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  
  if ((param_3 < 0x60) || (param_3 < 0x40 && 0xfffe < param_2)) {
LAB_000326b8:
    puVar2 = (undefined4 *)FUN_00442914();
    *puVar2 = 0x16;
    return 0xffffffff;
  }
  uVar1 = *param_1;
  if (param_3 < 0x200) {
    if (param_1[2] == 0) {
      param_1[2] = 1;
    }
    if (*(char *)((int)param_1 + 0x29) == '\0') {
      *(undefined1 *)((int)param_1 + 0x29) = 0xfd;
    }
    if (*(char *)(param_1 + 4) == '\0') {
      *(undefined1 *)(param_1 + 4) = 1;
    }
    iVar3 = (param_3 + 0x7ff) / param_3;
    goto LAB_000323f8;
  }
  if (param_2 < 0x2d1) {
    if (param_1[2] == 0) {
      param_1[2] = 1;
    }
    if (*(char *)((int)param_1 + 0x29) == '\0') {
      uVar6 = 0xfd;
LAB_0003268c:
      *(undefined1 *)((int)param_1 + 0x29) = uVar6;
    }
  }
  else {
    if (0x5a0 < param_2) {
      if (param_2 < 0x961) {
        if (param_1[2] == 0) {
          param_1[2] = 1;
        }
        if (*(char *)((int)param_1 + 0x29) == '\0') {
          uVar6 = 0xf9;
LAB_0003281c:
          *(undefined1 *)((int)param_1 + 0x29) = uVar6;
        }
      }
      else {
        if (0xb40 < param_2) {
          if (param_2 < 0xfa1) {
            if (param_1[2] == 0) {
              param_1[2] = 1;
            }
            if (*(char *)((int)param_1 + 0x29) == '\0') {
              *(undefined1 *)((int)param_1 + 0x29) = 0xf8;
            }
            if (*param_1 == 0) {
              *param_1 = 0xc;
            }
          }
          else {
            if (param_1[2] == 0) {
              param_1[2] = 2;
            }
            if (*(char *)((int)param_1 + 0x29) == '\0') {
              *(undefined1 *)((int)param_1 + 0x29) = 0xf8;
            }
          }
          iVar3 = (param_3 + 0x3fff) / param_3;
          *(undefined2 *)((int)param_1 + 0xe) = 0x200;
          goto LAB_000323f8;
        }
        if (param_1[2] == 0) {
          param_1[2] = 1;
        }
        if (*(char *)((int)param_1 + 0x29) == '\0') {
          uVar6 = 0xf0;
          goto LAB_0003281c;
        }
      }
      if (*param_1 == 0) {
        *param_1 = 0xc;
      }
      iVar3 = (param_3 + 0x1bff) / param_3;
      *(undefined2 *)((int)param_1 + 0xe) = 0xe0;
      goto LAB_000323f8;
    }
    if (param_1[2] == 0) {
      param_1[2] = 1;
    }
    if (*(char *)((int)param_1 + 0x29) == '\0') {
      uVar6 = 0xf9;
      goto LAB_0003268c;
    }
  }
  if (*param_1 == 0) {
    *param_1 = 0xc;
  }
  iVar3 = (param_3 + 0xdff) / param_3;
  *(undefined2 *)((int)param_1 + 0xe) = 0x70;
LAB_000323f8:
  if (*(short *)((int)param_1 + 0xe) != 0) {
    iVar3 = (*(short *)((int)param_1 + 0xe) * 0x20 + param_3 + -1) / param_3;
  }
  if (*(char *)(param_1 + 4) == '\0') {
    *(undefined1 *)(param_1 + 4) = 2;
  }
  uVar6 = 0x10;
  if (*(byte *)(param_1 + 4) < 0x10) {
    uVar6 = *(undefined1 *)(param_1 + 4);
  }
  *(undefined1 *)(param_1 + 4) = uVar6;
  uVar4 = param_2 / param_1[2];
  if (*param_1 != 0) goto LAB_0003247c;
  if (uVar4 < 0xff5) goto LAB_0003271c;
  if (0x3fffff < param_2) goto LAB_00032654;
  do {
    *param_1 = 0x10;
LAB_0003247c:
    do {
      uVar5 = *param_1;
      if (uVar5 == 0x10) {
        if (*(short *)(param_1 + 3) == 0) {
          *(undefined2 *)(param_1 + 3) = 1;
        }
        uVar8 = 0xfffe;
        uVar5 = 0xfff5;
        uVar7 = 2;
        uVar9 = 0xff6;
      }
      else if (uVar5 < 0x11) {
        if (uVar5 != 0xc) goto LAB_00032848;
        if (*(short *)(param_1 + 3) == 0) {
          *(undefined2 *)(param_1 + 3) = 1;
        }
        uVar8 = 0xff5;
        uVar7 = 1;
        uVar9 = 0;
        uVar5 = 0xff5;
      }
      else {
        if (uVar5 != 0x20) goto LAB_00032848;
        if (*(short *)(param_1 + 3) == 0) {
          *(undefined2 *)(param_1 + 3) = 0x20;
        }
        uVar8 = 0x1ffffff;
        uVar9 = 0xfff6;
        uVar5 = 0xffffff0;
        uVar7 = 8;
      }
      while ((uVar8 < uVar4 || (param_1[2] < uVar7))) {
        param_1[2] = param_1[2] << 1;
        uVar4 = param_2 / param_1[2];
      }
      uVar4 = 0x80;
      if ((int)param_1[2] < 0x80) {
        uVar4 = param_1[2];
      }
      param_1[2] = uVar4;
      uVar4 = param_1[2];
      uVar7 = param_1[2];
      while (0x10000 < (int)(uVar7 * param_3)) {
        param_1[2] = (int)param_1[2] >> 1;
        uVar4 = param_1[2];
        uVar7 = param_1[2];
      }
      uVar4 = param_2 / uVar4;
      if (uVar1 != 0 && uVar5 <= uVar4) goto LAB_000326b8;
      if (*param_1 == 0xc) {
        uVar4 = uVar4 * 3 >> 1;
        if (param_1[1] == 0) {
          param_1[1] = 0xd383d4;
        }
      }
      else if (*param_1 == 0x20) {
        uVar4 = uVar4 << 2;
        iVar3 = 0;
        if (param_1[1] == 0) {
          uVar7 = 0xd383c8;
          goto LAB_00032744;
        }
      }
      else {
        uVar4 = uVar4 << 1;
        uVar7 = 0xd383c0;
        if (param_1[1] == 0) {
LAB_00032744:
          param_1[1] = uVar7;
        }
      }
      uVar7 = iVar3 * param_3;
      param_1[5] = (int)(uVar4 + param_3 + -1) / param_3;
      *(ushort *)((int)param_1 + 0xe) =
           (short)((int)uVar7 >> 5) + (ushort)((int)uVar7 < 0 && (uVar7 & 0x1f) != 0);
      if ((*param_1 != 0x20) && (0x200 < *(short *)((int)param_1 + 0xe))) {
        *(undefined2 *)((int)param_1 + 0xe) = 0x200;
      }
      uVar4 = ((((param_2 - (int)*(short *)(param_1 + 3)) - iVar3) - param_1[7]) -
              param_1[5] * (uint)*(byte *)(param_1 + 4)) / param_1[2];
      param_1[6] = uVar4;
      if (param_2 < param_1[5] * (uint)*(byte *)(param_1 + 4) + param_1[6] * param_1[2] +
                    param_1[7] + (int)*(short *)(param_1 + 3) + iVar3) {
LAB_00032848:
        puVar2 = (undefined4 *)FUN_00442914();
        *puVar2 = 0x16;
        return 0xffffffff;
      }
      if (uVar9 <= uVar4) {
        if (uVar4 < uVar5) {
          return 0;
        }
        if (*param_1 == 0xc) break;
        if (*param_1 != 0x10) goto LAB_00032848;
LAB_00032654:
        *param_1 = 0x20;
        goto LAB_0003247c;
      }
      if (*param_1 == 0x10) {
LAB_0003271c:
        *param_1 = 0xc;
        goto LAB_0003247c;
      }
    } while (*param_1 != 0x20);
  } while( true );
}

