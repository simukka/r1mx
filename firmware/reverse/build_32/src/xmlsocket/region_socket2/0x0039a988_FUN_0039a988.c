/* 0x0039a988  FUN_0039a988  size=624 bytes */


undefined4 FUN_0039a988(byte *param_1,int *param_2)

{
  byte bVar1;
  bool bVar2;
  bool bVar3;
  bool bVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  byte *pbVar10;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  uStack_28 = 0;
  uVar8 = 0;
  iVar9 = 0;
  uStack_24 = 0;
  iVar7 = 0;
  bVar2 = false;
  for (pbVar10 = param_1;
      (((bVar1 = *pbVar10, bVar1 == 0x20 || (bVar1 == 9)) || (bVar1 == 10)) ||
      (((bVar1 == 0xb || (bVar1 == 0xd)) || (bVar1 == 0xc)))); pbVar10 = pbVar10 + 1) {
  }
  if (bVar1 == 0) {
    if (param_2 == (int *)0x0) {
      return 0;
    }
    *param_2 = (int)param_1;
    return 0;
  }
  if (bVar1 == 0x2d) {
    uVar8 = 1;
  }
  else if (bVar1 != 0x2b) goto LAB_0039aa50;
  pbVar10 = pbVar10 + 1;
  if (*pbVar10 == 0) {
    if (param_2 == (int *)0x0) {
      return 0;
    }
    *param_2 = (int)param_1;
    return 0;
  }
LAB_0039aa50:
  bVar4 = false;
  bVar3 = false;
  if ((9 < *pbVar10 - 0x30) && (*pbVar10 != 0x2e)) {
    if (param_2 != (int *)0x0) {
      *param_2 = (int)param_1;
    }
    return 0;
  }
  while( true ) {
    uVar6 = (uint)*pbVar10;
    if ((9 < uVar6 - 0x30) && (uVar6 != 0x2e)) break;
    bVar2 = true;
    if (uVar6 == 0x2e) {
      bVar3 = true;
    }
    else {
      iVar5 = FUN_0039a7b8(&uStack_28,uVar6 - 0x30);
      iVar9 = iVar9 + (uint)(iVar5 != 0);
      if (bVar3) {
        iVar9 = iVar9 + -1;
      }
    }
    pbVar10 = pbVar10 + 1;
  }
  if ((((uVar6 == 0x65) || (uVar6 == 0x45)) || (uVar6 == 100)) || (uVar6 == 0x44)) {
    pbVar10 = pbVar10 + 1;
    bVar2 = true;
    if (*pbVar10 != 0) {
      for (; ((bVar1 = *pbVar10, bVar1 == 0x20 || (bVar1 == 9)) ||
             (((bVar1 == 10 || ((bVar1 == 0xb || (bVar1 == 0xd)))) || (bVar1 == 0xc))));
          pbVar10 = pbVar10 + 1) {
      }
      if (bVar1 != 0) {
        if (((bVar1 == 0x2d) || (bVar1 == 0x2b)) &&
           (bVar1 = *pbVar10, pbVar10 = pbVar10 + 1, bVar1 == 0x2d)) {
          bVar4 = true;
        }
        uVar6 = (uint)*pbVar10;
        if (uVar6 != 0) {
          while (uVar6 - 0x30 < 10) {
            if (iVar7 < 0x134) {
              iVar7 = iVar7 * 10 + (uint)*pbVar10 + -0x30;
            }
            pbVar10 = pbVar10 + 1;
            uVar6 = (uint)*pbVar10;
          }
          if (bVar4) {
            iVar9 = iVar9 - iVar7;
          }
          else {
            iVar9 = iVar9 + iVar7;
          }
        }
      }
    }
  }
  if (param_2 != (int *)0x0) {
    if (bVar2) {
      param_1 = pbVar10;
    }
    *param_2 = (int)param_1;
  }
  uVar8 = FUN_0039a8a8(&uStack_28,iVar9,uVar8);
  return uVar8;
}

