/* 0x0002dc70  FUN_0002dc70  size=468 bytes */


int FUN_0002dc70(int param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  
  iVar9 = -1;
  if (param_2 == (uint *)0x0) {
    uVar3 = 0xd37ab8;
    if (iRam00e1085c == 0) {
      return -1;
    }
  }
  else {
    if ((param_1 == 0xe10828) || (param_1 == 0xe107f8)) {
      uVar1 = *param_2;
      iVar12 = 4;
      iVar5 = 0;
      uVar4 = uVar1;
      uVar10 = param_2[1];
      uVar11 = param_2[2];
      do {
        iVar7 = iVar5 + param_1;
        if ((*(int *)(iVar5 + param_1) == 0) ||
           (uVar2 = uVar4, uVar6 = uVar10, uVar8 = uVar11, uVar1 < *(uint *)(iVar5 + param_1))) {
          uVar2 = *(uint *)(iVar5 + param_1);
          uVar6 = *(uint *)(iVar7 + 4);
          uVar8 = *(uint *)(iVar7 + 8);
          *(uint *)(iVar5 + param_1) = uVar4;
          iVar9 = 0;
          *(uint *)(iVar7 + 4) = uVar10;
          *(uint *)(iVar7 + 8) = uVar11;
          uVar1 = uVar2;
        }
        iVar5 = iVar5 + 0xc;
        iVar12 = iVar12 + -1;
        uVar4 = uVar2;
        uVar10 = uVar6;
        uVar11 = uVar8;
      } while (iVar12 != 0);
      if ((iVar9 == -1) && (iRam00e1085c != 0)) {
        FUN_00443f20(0xd37a68,0,0,0,0,0,0);
      }
      return iVar9;
    }
    if (iRam00e1085c == 0) {
      return -1;
    }
    uVar3 = 0xd37a90;
  }
  FUN_00443f20(uVar3,0,0,0,0,0,0);
  return -1;
}

