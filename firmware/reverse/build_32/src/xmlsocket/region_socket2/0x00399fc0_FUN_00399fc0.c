/* 0x00399fc0  FUN_00399fc0  size=1052 bytes */


void FUN_00399fc0(undefined1 *param_1,int param_2,int param_3,code *param_4)

{
  undefined1 uVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  undefined1 *puVar5;
  undefined1 *puVar6;
  undefined1 *puVar7;
  undefined1 *puVar8;
  undefined1 *puVar9;
  undefined1 *puVar10;
  undefined1 *puVar11;
  
LAB_00399fe0:
  do {
    puVar9 = param_1 + param_3 * (param_2 >> 1);
    puVar6 = param_1 + param_3 * (param_2 + -1);
    if (5 < param_2) {
      iVar3 = (*param_4)(param_1,puVar9);
      iVar4 = (*param_4)(puVar9,puVar6);
      puVar5 = puVar9;
      if (iVar3 < 0) {
        if ((0 < iVar4) && (iVar3 = (*param_4)(param_1,puVar6), puVar5 = param_1, iVar3 < 0)) {
          puVar5 = puVar6;
        }
      }
      else if (((0 < iVar3) && (iVar4 < 0)) &&
              (iVar3 = (*param_4)(param_1,puVar6), puVar5 = param_1, 0 < iVar3)) {
        puVar5 = puVar6;
      }
      if (puVar5 != puVar9) {
        puVar9 = puVar9 + -1;
        puVar5 = puVar5 + -1;
        iVar3 = param_3;
        do {
          uVar1 = puVar5[1];
          puVar5 = puVar5 + 1;
          *puVar5 = puVar9[1];
          puVar9 = puVar9 + 1;
          *puVar9 = uVar1;
          iVar3 = iVar3 + -1;
        } while (iVar3 != 0);
        puVar9 = puVar9 + (1 - param_3);
      }
    }
    bVar2 = false;
    puVar5 = param_1;
    while( true ) {
      puVar8 = puVar5;
      if (puVar5 < puVar9) {
        iVar3 = (*param_4)(puVar5,puVar9);
        while ((puVar8 = puVar5, iVar3 < 1 &&
               (puVar5 = puVar5 + param_3, puVar8 = puVar5, puVar5 < puVar9))) {
          iVar3 = (*param_4)(puVar5,puVar9);
        }
      }
      for (; puVar9 < puVar6; puVar6 = puVar6 + -param_3) {
        iVar3 = (*param_4)(puVar9,puVar6);
        if (0 < iVar3) {
          puVar5 = puVar8 + param_3;
          puVar7 = puVar6;
          puVar11 = puVar6;
          puVar10 = puVar9;
          if (puVar8 == puVar9) goto LAB_0039a17c;
          goto LAB_0039a178;
        }
      }
      puVar5 = puVar8;
      puVar7 = puVar9;
      puVar10 = puVar8;
      if (puVar8 == puVar9) break;
LAB_0039a178:
      puVar6 = puVar6 + -param_3;
      puVar11 = puVar10;
LAB_0039a17c:
      puVar7 = puVar7 + -1;
      puVar8 = puVar8 + -1;
      iVar3 = param_3;
      do {
        uVar1 = puVar8[1];
        puVar8 = puVar8 + 1;
        *puVar8 = puVar7[1];
        puVar7 = puVar7 + 1;
        *puVar7 = uVar1;
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
      bVar2 = true;
      puVar9 = puVar11;
    }
    puVar6 = param_1;
    if (!bVar2) goto LAB_0039a3bc;
    iVar3 = ((int)puVar9 - (int)param_1) / param_3;
    param_2 = (param_2 - iVar3) + -1;
    puVar6 = puVar9 + param_3;
    if (iVar3 <= param_2) {
      if (iVar3 < 4) {
        if (1 < iVar3) {
          if (iVar3 == 2) {
            iVar3 = (*param_4)(param_1 + param_3,param_1);
            if (iVar3 < 0) {
              puVar5 = param_1 + -1;
              puVar9 = param_1 + param_3 + -1;
              iVar3 = param_3;
              do {
                uVar1 = puVar9[1];
                puVar9 = puVar9 + 1;
                *puVar9 = puVar5[1];
                puVar5 = puVar5 + 1;
                *puVar5 = uVar1;
                iVar3 = iVar3 + -1;
              } while (iVar3 != 0);
            }
          }
          else {
            FUN_00399ef0(param_1,iVar3,param_3,param_4);
          }
        }
        param_1 = puVar6;
        if (param_2 < 4) {
          if (param_2 < 2) {
            return;
          }
          if (param_2 == 2) {
            iVar3 = (*param_4)(puVar6 + param_3,puVar6);
            if (iVar3 < 0) {
              puVar5 = puVar6 + -1;
              puVar9 = puVar6 + param_3 + -1;
              do {
                uVar1 = puVar9[1];
                puVar9 = puVar9 + 1;
                *puVar9 = puVar5[1];
                puVar5 = puVar5 + 1;
                *puVar5 = uVar1;
                param_3 = param_3 + -1;
              } while (param_3 != 0);
              return;
            }
            return;
          }
          goto LAB_0039a3bc;
        }
      }
      else {
        FUN_00399fc0(param_1,iVar3,param_3,param_4);
        param_1 = puVar6;
      }
      goto LAB_00399fe0;
    }
    if (param_2 < 4) {
      if (1 < param_2) {
        if (param_2 == 2) {
          iVar4 = (*param_4)(puVar6 + param_3,puVar6);
          if (iVar4 < 0) {
            puVar5 = puVar6 + -1;
            puVar9 = puVar6 + param_3 + -1;
            iVar4 = param_3;
            do {
              uVar1 = puVar9[1];
              puVar9 = puVar9 + 1;
              *puVar9 = puVar5[1];
              puVar5 = puVar5 + 1;
              *puVar5 = uVar1;
              iVar4 = iVar4 + -1;
            } while (iVar4 != 0);
          }
        }
        else {
          FUN_00399ef0(puVar6,param_2,param_3,param_4);
        }
      }
      param_2 = iVar3;
      if (iVar3 < 4) {
        if (iVar3 < 2) {
          return;
        }
        puVar6 = param_1;
        if (iVar3 == 2) {
          iVar3 = (*param_4)(param_1 + param_3,param_1);
          if (-1 < iVar3) {
            return;
          }
          puVar6 = param_1 + -1;
          puVar9 = param_1 + param_3 + -1;
          do {
            uVar1 = puVar9[1];
            puVar9 = puVar9 + 1;
            *puVar9 = puVar6[1];
            puVar6 = puVar6 + 1;
            *puVar6 = uVar1;
            param_3 = param_3 + -1;
          } while (param_3 != 0);
          return;
        }
LAB_0039a3bc:
        FUN_00399ef0(puVar6,param_2,param_3,param_4);
        return;
      }
    }
    else {
      FUN_00399fc0(puVar6,param_2,param_3,param_4);
      param_2 = iVar3;
    }
  } while( true );
}

