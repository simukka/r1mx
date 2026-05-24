/* 0x0039a44c  FUN_0039a44c  size=452 bytes */


uint FUN_0039a44c(byte *param_1,undefined4 *param_2,uint param_3)

{
  byte bVar1;
  undefined4 *puVar2;
  uint uVar3;
  bool bVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  byte *pbVar8;
  byte *pbVar9;
  uint uVar10;
  uint uVar11;
  
  bVar4 = false;
  pbVar9 = param_1 + -1;
  do {
    pbVar8 = pbVar9;
    uVar5 = (uint)pbVar8[1];
    pbVar9 = pbVar8 + 1;
  } while ((*(byte *)(iRam00e272d8 + uVar5) & 0x28) != 0);
  pbVar9 = pbVar8 + 2;
  if (uVar5 == 0x2d) {
    bVar4 = true;
  }
  else if (uVar5 != 0x2b) goto LAB_0039a4a8;
  uVar5 = (uint)*pbVar9;
  pbVar9 = pbVar8 + 3;
LAB_0039a4a8:
  if ((((param_3 == 0) || (param_3 == 0x10)) && (uVar5 == 0x30)) &&
     ((*pbVar9 == 0x78 || (*pbVar9 == 0x58)))) {
    uVar5 = (uint)pbVar9[1];
    pbVar9 = pbVar9 + 2;
    param_3 = 0x10;
  }
  if (param_3 == 0) {
    if (uVar5 == 0x30) {
      param_3 = 8;
    }
    else {
      param_3 = 10;
    }
  }
  if (bVar4) {
    uVar10 = 0x80000000;
  }
  else {
    uVar10 = 0x7fffffff;
  }
  uVar3 = uVar10 / param_3;
  uVar11 = 0;
  iVar7 = 0;
  do {
    bVar1 = *(byte *)(iRam00e272d8 + uVar5);
    if ((bVar1 & 4) == 0) {
      if ((bVar1 & 3) == 0) {
LAB_0039a5a4:
        if (iVar7 < 0) {
          if (bVar4) {
            uVar11 = 0x80000000;
          }
          else {
            uVar11 = 0x7fffffff;
          }
          puVar2 = (undefined4 *)FUN_00442914();
          *puVar2 = 0x26;
        }
        else if (bVar4) {
          uVar11 = -uVar11;
        }
        if (param_2 != (undefined4 *)0x0) {
          if (iVar7 != 0) {
            param_1 = pbVar9 + -1;
          }
          *param_2 = param_1;
        }
        return uVar11;
      }
      if ((bVar1 & 1) == 0) {
        iVar6 = 0x57;
      }
      else {
        iVar6 = 0x37;
      }
      iVar6 = uVar5 - iVar6;
    }
    else {
      iVar6 = uVar5 - 0x30;
    }
    if ((int)param_3 <= iVar6) goto LAB_0039a5a4;
    if (((iVar7 < 0) || (uVar3 < uVar11)) ||
       ((uVar11 == uVar3 && ((int)(uVar10 - param_3 * uVar3) < iVar6)))) {
      iVar7 = -1;
    }
    else {
      iVar7 = 1;
      uVar11 = uVar11 * param_3 + iVar6;
    }
    uVar5 = (uint)*pbVar9;
    pbVar9 = pbVar9 + 1;
  } while( true );
}

