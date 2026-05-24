/* 0x00085bc8  FUN_00085bc8  size=1124 bytes */


void FUN_00085bc8(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  undefined4 *puVar7;
  int iVar8;
  int iVar9;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined1 uStack_60;
  undefined2 uStack_5f;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined1 uStack_40;
  undefined2 uStack_3f;
  char acStack_38 [4];
  int iStack_34;
  int aiStack_30 [2];
  
  uStack_78 = uRam00d41730;
  uStack_74 = uRam00d41734;
  uStack_70 = uRam00d41738;
  uStack_6c = uRam00d4173c;
  uStack_68 = uRam00d41740;
  uStack_64 = uRam00d41744;
  uStack_60 = uRam00d41748;
  uStack_5f = uRam00d41749;
  uStack_58 = uRam00d4174c;
  uStack_54 = uRam00d41750;
  uStack_50 = uRam00d41754;
  uStack_4c = uRam00d41758;
  uStack_48 = uRam00d4175c;
  uStack_44 = uRam00d41760;
  uStack_40 = uRam00d41764;
  uStack_3f = uRam00d41765;
  iVar1 = FUN_00191b58(acStack_38);
  if ((iVar1 == -1) || (acStack_38[0] != '\a')) {
    iVar1 = FUN_0044f4cc(&uStack_58,0,0);
    iVar2 = *(int *)(param_1 + 0x94);
    *(undefined4 *)(iVar2 + 0x14) = 1;
    uVar4 = 100;
  }
  else {
    iVar1 = FUN_0044f4cc(&uStack_58,0,0);
    iVar2 = *(int *)(param_1 + 0x94);
    uVar4 = 0x96;
    *(undefined4 *)(iVar2 + 0x14) = 2;
  }
  FUN_0013173c(iVar2,uVar4);
  *(undefined4 *)(param_1 + 0x44) = 100;
  if (iVar1 < 0) {
    *(undefined4 *)(param_1 + 0x48) = 0;
    *(undefined4 *)(param_1 + 0x50) = 0;
    *(undefined4 *)(param_1 + 0x54) = 0;
    puVar7 = (undefined4 *)FUN_00442914();
    FUN_0005e784(2,3,0xc,0xd41584,0x65e5a4,0x813,0xd3c598,0x65e5a4,&uStack_58,*puVar7);
  }
  else {
    FUN_0044e144(iVar1,&iStack_34,4);
    FUN_0044e144(iVar1,aiStack_30,4);
    uVar5 = iStack_34 + 7;
    iVar2 = (((int)uVar5 >> 3) + (uint)((int)uVar5 < 0 && (uVar5 & 7) != 0)) * 8;
    *(int *)(param_1 + 0x50) = aiStack_30[0];
    *(int *)(param_1 + 0x54) = iVar2;
    iVar3 = FUN_0045964c(0x20,iVar2 * aiStack_30[0] * 4);
    iVar2 = *(int *)(param_1 + 0x50);
    *(int *)(param_1 + 0x48) = iVar3;
    iVar9 = 0;
    if (0 < iVar2) {
      iVar6 = *(int *)(param_1 + 0x54);
      do {
        iVar8 = 0;
        if (0 < iVar6) {
          do {
            *(undefined4 *)((iVar6 * iVar9 + iVar8) * 4 + iVar3) = 0xc0000000;
            iVar6 = *(int *)(param_1 + 0x54);
            iVar8 = iVar8 + 1;
          } while (iVar8 < iVar6);
          iVar2 = *(int *)(param_1 + 0x50);
        }
        iVar9 = iVar9 + 1;
      } while (iVar9 < iVar2);
    }
    iVar9 = 0;
    if (0 < iVar2) {
      while( true ) {
        FUN_0044e144(iVar1,iVar3 + *(int *)(param_1 + 0x54) * iVar9 * 4,iStack_34 << 2);
        iVar9 = iVar9 + 1;
        if (*(int *)(param_1 + 0x50) <= iVar9) break;
        iVar3 = *(int *)(param_1 + 0x48);
      }
    }
  }
  iVar1 = FUN_0044f4cc(&uStack_78,0,0);
  if (iVar1 < 0) {
    *(undefined4 *)(param_1 + 0x54) = 0;
    *(undefined4 *)(param_1 + 0x50) = 0;
    *(undefined4 *)(param_1 + 0x4c) = 0;
    puVar7 = (undefined4 *)FUN_00442914();
    FUN_0005e784(2,3,0xc,0xd41584,0x65e5a4,0x82e,0xd3c598,0x65e5a4,&uStack_78,*puVar7);
  }
  else {
    FUN_0044e144(iVar1,&iStack_34,4);
    FUN_0044e144(iVar1,aiStack_30,4);
    uVar5 = iStack_34 + 7;
    iVar2 = (((int)uVar5 >> 3) + (uint)((int)uVar5 < 0 && (uVar5 & 7) != 0)) * 8;
    *(int *)(param_1 + 0x50) = aiStack_30[0];
    *(int *)(param_1 + 0x54) = iVar2;
    iVar3 = FUN_0045964c(0x20,iVar2 * aiStack_30[0] * 4);
    iVar2 = *(int *)(param_1 + 0x50);
    *(int *)(param_1 + 0x4c) = iVar3;
    iVar9 = 0;
    if (0 < iVar2) {
      iVar6 = *(int *)(param_1 + 0x54);
      do {
        iVar8 = 0;
        if (0 < iVar6) {
          do {
            *(undefined4 *)((iVar6 * iVar9 + iVar8) * 4 + iVar3) = 0xc0000000;
            iVar6 = *(int *)(param_1 + 0x54);
            iVar8 = iVar8 + 1;
          } while (iVar8 < iVar6);
          iVar2 = *(int *)(param_1 + 0x50);
        }
        iVar9 = iVar9 + 1;
      } while (iVar9 < iVar2);
    }
    iVar9 = 0;
    if (0 < iVar2) {
      while( true ) {
        FUN_0044e144(iVar1,iVar3 + *(int *)(param_1 + 0x54) * iVar9 * 4,iStack_34 << 2);
        iVar9 = iVar9 + 1;
        if (*(int *)(param_1 + 0x50) <= iVar9) break;
        iVar3 = *(int *)(param_1 + 0x4c);
      }
    }
  }
  iVar1 = *(int *)(param_1 + 0x5c);
  iVar3 = 0;
  iVar2 = 0;
  do {
    puVar7 = (undefined4 *)(iVar2 * 4 + iVar1);
    iVar9 = 0x130;
    do {
      *puVar7 = 0xc0000000;
      puVar7 = puVar7 + 1;
      iVar9 = iVar9 + -1;
    } while (iVar9 != 0);
    iVar3 = iVar3 + 1;
    iVar2 = iVar2 + 0x130;
  } while (iVar3 < 0x32);
  FUN_0013068c(*(undefined4 *)(param_1 + 0x94),iVar1,0xed80,0x130,0x32);
  return;
}

