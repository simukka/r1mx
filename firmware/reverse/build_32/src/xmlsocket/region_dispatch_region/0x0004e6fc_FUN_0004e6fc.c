/* 0x0004e6fc  FUN_0004e6fc  size=936 bytes */


int FUN_0004e6fc(int param_1,int param_2)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  uint *puVar5;
  undefined4 *puVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  
  uVar2 = (uint)bRam00e149b4;
  iVar9 = param_1 + 0x70;
  FUN_0039acec(iVar9,0,0x400);
  iVar3 = FUN_0000d350(0xd3a900,iVar9,0x400,0);
  bVar1 = iVar3 == 0;
  uVar2 = (int)-(uVar2 ^ 7) >> 0x1f & 0xfffffffe;
  FUN_0039ac74(param_2,iVar9,0x400);
  iVar3 = 0;
  uVar11 = 0;
  iVar9 = param_2 + 0x400;
  if (bVar1) {
    if (*(uint *)(param_1 + 0x70) == 0x5243414c) {
      iVar3 = FUN_0045b974(0x4c80);
      if (iVar3 == 0) {
        FUN_0005e784(0,3,0x11,0xd3c31c,0x65d0a8,0x60d,0xd3c438,0x65d0a8);
        return 0;
      }
      FUN_0005e784(2,3,0x11,0xd3c31c,0x65d0a8,0x612,0xd3c3cc,0x65d0a8,0x1180);
      uVar10 = 0;
      iVar12 = iVar9;
      if (uVar2 != 0xffffffe2) {
        do {
          iVar9 = FUN_0000d350(0xd3a900,iVar3,0x4c80,uVar11 + 0x400);
          bVar1 = iVar9 == 0;
          uVar10 = uVar10 + 1;
          iVar9 = iVar12 + 0x4c80;
          FUN_0039ac74(iVar12,iVar3,0x4c80);
          if (!bVar1) {
            puVar6 = (undefined4 *)FUN_00442914();
            FUN_0005e784(0,3,0x11,0xd3c31c,0x65d0a8,0x61d,0xd3c408,0x65d0a8,*puVar6,0x61e,uVar11);
            break;
          }
          uVar11 = uVar11 + 0x4c80;
          iVar12 = iVar9;
        } while (uVar10 < uVar2 + 0x1e);
      }
      iVar12 = iVar9;
      if (uVar11 < *(uint *)(param_1 + 0x88)) {
        do {
          iVar9 = FUN_0000d350(0xd3a900,iVar3,0x4c80,uVar11 + 0x400);
          bVar1 = iVar9 == 0;
          iVar9 = iVar12 + 0x4c80;
          FUN_0039ac74(iVar12,iVar3,0x4c80);
          if (!bVar1) {
            puVar6 = (undefined4 *)FUN_00442914();
            FUN_0005e784(0,3,0x11,0xd3c31c,0x65d0a8,0x62d,0xd3c408,0x65d0a8,*puVar6,0x62e,uVar11);
            break;
          }
          uVar11 = uVar11 + 0x4c80;
          iVar12 = iVar9;
        } while (uVar11 < *(uint *)(param_1 + 0x88));
      }
      iVar3 = iVar9 - param_2;
      uVar2 = 0xd5b86c;
      if (!(bool)(iVar3 != 0 & bVar1)) {
        uVar2 = 0xd3b588;
      }
      uVar8 = 0xd3c3ec;
      uVar7 = 0x638;
      uVar4 = 2;
    }
    else {
      uVar2 = *(uint *)(param_1 + 0x70) >> 0x18;
      uVar8 = 0xd3c3ac;
      uVar4 = 0;
      uVar7 = 0x640;
    }
  }
  else {
    puVar5 = (uint *)FUN_00442914();
    uVar2 = *puVar5;
    uVar8 = 0xd3c408;
    uVar7 = 0x602;
    uVar4 = 0;
  }
  FUN_0005e784(uVar4,3,0x11,0xd3c31c,0x65d0a8,uVar7,uVar8,0x65d0a8,uVar2);
  return iVar3;
}

