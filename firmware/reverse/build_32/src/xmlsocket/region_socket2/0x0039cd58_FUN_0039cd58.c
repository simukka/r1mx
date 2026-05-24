/* 0x0039cd58  FUN_0039cd58  size=576 bytes */


undefined4 FUN_0039cd58(code *param_1,int *param_2)

{
  undefined4 *puVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  uint uVar14;
  
  uVar6 = 0;
  if ((param_1 == reset_vector) || (param_2 == (int *)0x0)) {
    uVar6 = 1;
  }
  else {
    *param_2 = 0;
    puVar1 = (undefined4 *)(*param_1)();
    if (puVar1 == (undefined4 *)0x0) {
      uVar6 = 0x14;
    }
    else {
      iVar2 = FUN_0039ca64(puVar1,param_2);
      if (iVar2 == 0) {
        iVar2 = FUN_0039cba0(puVar1);
        if (iVar2 == 0) {
          puVar1[0xe] = 0;
          uVar6 = 0x2b;
          FUN_003cb350(0x3ad5a9,*puVar1);
        }
        else {
          if (((code *)puVar1[0xd] == reset_vector) ||
             (iVar2 = (*(code *)puVar1[0xd])(puVar1), iVar2 == 0)) {
            iVar2 = FUN_0039c9cc();
            *param_2 = iVar2;
            *(undefined4 **)(*(int *)(iRam00e9c6a4 + 4) + iVar2 * 4) = puVar1;
            if (puVar1[0xf] == 0) {
              uVar6 = FUN_0039efe4(0x8c);
              puVar1[0xf] = uVar6;
              FUN_0039ac74(uVar6,*(undefined4 *)
                                  (*(int *)(*(int *)(iRam00e9c6a4 + 4) + iRam00e9c528 * 4) + 0x3c),
                           0x8c);
            }
            if (puVar1 == (undefined4 *)0x0) {
              return 0;
            }
            iVar2 = *(int *)(*(int *)(iRam00e9c6a4 + 4) + iRam00e9c528 * 4);
            uVar7 = 0;
            iVar10 = 0xe27590;
            piVar4 = puVar1 + 6;
            do {
              uVar9 = 0;
              if (*(int *)(iVar10 + 4) != 0) {
                piVar3 = (int *)(*piVar4 + -4);
                do {
                  piVar3 = piVar3 + 1;
                  if ((*piVar3 != 0) && (uVar14 = 0, *(int *)(iVar10 + 8) != 0)) {
                    iVar5 = *(int *)(*piVar4 + uVar9 * 4);
                    do {
                      uVar12 = uVar14 >> 3 & 0x1ffffffc;
                      iVar13 = iVar5 + uVar12;
                      uVar8 = 1 << (uVar14 & 0x1f);
                      if (((*(uint *)(iVar13 + 0xf0) & uVar8) == 0) &&
                         (iVar11 = *(int *)(*(int *)(iVar2 + uVar7 * 4 + 0x18) + uVar9 * 4),
                         (*(uint *)(iVar11 + uVar12 + 0xf0) & uVar8) != 0)) {
                        *(undefined4 *)(iVar5 + uVar14 * 4 + 0x1c) =
                             *(undefined4 *)(iVar11 + uVar14 * 4 + 0x1c);
                        *(uint *)(iVar13 + 0xf0) = *(uint *)(iVar13 + 0xf0) | uVar8;
                      }
                      uVar14 = uVar14 + 1;
                    } while (uVar14 < *(uint *)(iVar10 + 8));
                  }
                  uVar9 = uVar9 + 1;
                } while (uVar9 < *(uint *)(iVar10 + 4));
              }
              uVar7 = uVar7 + 1;
              iVar10 = iVar10 + 0xc;
              piVar4 = piVar4 + 1;
            } while (uVar7 < 7);
            return 0;
          }
          uVar6 = 0x15;
        }
      }
      else {
        puVar1[0xe] = 0;
      }
      FUN_0039e014(puVar1);
    }
  }
  return uVar6;
}

