/* 0x00028acc  FUN_00028acc  size=672 bytes */


undefined4
FUN_00028acc(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  undefined1 auStack_48 [36];
  
  iVar1 = param_1 * 0x430;
  if ((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) &&
     (*(int *)(iVar1 + 0x108e9e4) != 0)) {
    if ((*(int *)(iVar1 + 0x108eacc) == -1) || (*(int *)(iVar1 + 0x108eacc) == 0)) {
      FUN_003cae4c(auStack_48,0xd36a38,param_1);
      uVar3 = FUN_005af79c(auStack_48,uRam00e10738,0,0x1000,0x37ad4,iVar1 + 0x108e6a0,0,0,0,0,0,0,0,
                           0,0);
      *(undefined4 *)(iVar1 + 0x108eacc) = uVar3;
      if (*(int *)(iVar1 + 0x108eacc) == -1) {
        return 0;
      }
    }
    iVar2 = FUN_0001f738(param_1,param_2,param_3,param_4);
    if (iVar2 != 0) {
      iVar1 = *(int *)(param_2 * 600 + iVar1 + 0x108e6a0 + 0x240);
      FUN_0039b1d4(iVar1 + 0x88,param_5,10);
      if (8 < iRam00e107b4) {
        FUN_00443f20(0xd36a58,iVar1 + 0x60,0xe107b8,param_5,*(undefined4 *)(iVar1 + 0x1c),
                     *(undefined4 *)(iVar1 + 0x18),0);
      }
      *(int *)(iVar1 + 0x98) = iVar1;
      *(undefined4 *)(iVar1 + 0x60) = 0xffffffff;
      if (*(int *)(iVar2 + 0x10) != 0) {
        (**(code **)(iVar2 + 0x10))(iVar2);
      }
      FUN_00027e90(iVar1 + 0x60);
      if (iRam00e107b4 < 9) {
        uVar3 = *(undefined4 *)(iVar1 + 0x60);
      }
      else {
        FUN_00443f20(0xd36a44,0x65c7cc,0,0,0,0,0);
        uVar3 = *(undefined4 *)(iVar1 + 0x60);
      }
      return uVar3;
    }
    puVar4 = (undefined4 *)FUN_00442914();
    FUN_003cb248(0xd36a90,*puVar4,param_2,param_1);
  }
  else {
    FUN_003cb248(0xd369f4,param_2,param_1);
  }
  return 0;
}

