/* 0x0039be54  FUN_0039be54  size=716 bytes */


undefined4 FUN_0039be54(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined1 auStack_48 [4];
  undefined4 uStack_44;
  undefined1 auStack_40 [36];
  
  uStack_44 = 0x3ac816;
  iVar1 = FUN_0044259c(0x3ac817);
  if (iVar1 == 0) {
    iVar1 = *(int *)(param_2 + 0xb8);
    iVar2 = *(int *)(param_2 + 0xbc);
    iVar4 = FUN_0039ad64(iVar1,0x3ac816);
    if ((iVar4 == 0) || (iVar4 = FUN_0039ad64(iVar2,0x3ac816), iVar4 == 0)) {
      return 0;
    }
  }
  else {
    FUN_0039af30(auStack_40,iVar1);
    FUN_0039b334(auStack_40,&LAB_003ac820,&uStack_44);
    FUN_0039b334(0,&LAB_003ac820,&uStack_44);
    iVar1 = FUN_0039b334(0,&LAB_003ac820,&uStack_44);
    iVar2 = FUN_0039b334(0,&LAB_003ac820,&uStack_44);
  }
  if ((iVar1 == 0) || (iVar2 == 0)) {
    uVar3 = 0;
  }
  else {
    memset(auStack_48,4);
    FUN_0039b1d4(auStack_48,iVar1,2);
    iVar4 = FUN_00399bcc();
    iVar4 = iVar4 + -1;
    memset(auStack_48,4);
    FUN_0039b1d4(auStack_48,iVar2,2);
    iVar5 = FUN_00399bcc();
    iVar8 = *(int *)(param_1 + 0x10);
    iVar5 = iVar5 + -1;
    if ((iVar8 < iVar4) || (iVar5 < iVar8)) {
      uVar3 = 0;
    }
    else {
      if ((iVar8 == iVar4) || (iVar8 == iVar5)) {
        memset(auStack_48,4);
        FUN_0039b1d4(auStack_48,iVar1 + 2,2);
        iVar8 = FUN_00399bcc();
        memset(auStack_48,4);
        FUN_0039b1d4(auStack_48,iVar2 + 2,2);
        iVar6 = FUN_00399bcc();
        iVar7 = *(int *)(param_1 + 0x10);
        if (((iVar7 == iVar4) && (*(int *)(param_1 + 0xc) < iVar8)) ||
           ((iVar7 == iVar5 && (iVar6 < *(int *)(param_1 + 0xc))))) {
          return 0;
        }
        if (((iVar7 == iVar4) && (*(int *)(param_1 + 0xc) == iVar8)) ||
           ((iVar7 == iVar5 && (*(int *)(param_1 + 0xc) == iVar6)))) {
          memset(auStack_48,4);
          FUN_0039b1d4(auStack_48,iVar1 + 4,2);
          iVar1 = FUN_00399bcc();
          memset(auStack_48,4);
          FUN_0039b1d4(auStack_48,iVar2 + 4,2);
          iVar2 = FUN_00399bcc();
          if ((((*(int *)(param_1 + 0x10) != iVar4) || (*(int *)(param_1 + 0xc) != iVar8)) ||
              (iVar1 <= *(int *)(param_1 + 8))) &&
             (((*(int *)(param_1 + 0x10) != iVar5 || (*(int *)(param_1 + 0xc) != iVar6)) ||
              (*(int *)(param_1 + 8) + 1 < iVar2)))) {
            return 1;
          }
          return 0;
        }
      }
      uVar3 = 1;
    }
  }
  return uVar3;
}

