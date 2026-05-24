/* 0x003940f4  FUN_003940f4  size=272 bytes */


void FUN_003940f4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  int *piVar4;
  undefined4 uVar5;
  undefined4 uStack_28;
  undefined4 auStack_24 [3];
  
  if (iRam00e272a8 != 0) {
    uVar1 = FUN_003938b0(puRam00e9c470);
    puVar2 = (undefined4 *)FUN_00442914();
    uVar5 = *puVar2;
    iVar3 = FUN_00394068(uVar1,param_2,auStack_24);
    if (iVar3 == 0) {
      uStack_28 = 0;
      FUN_00394068(uVar1,param_1,&uStack_28);
      piVar4 = (int *)FUN_00442914();
      if (*piVar4 == 0x550002) {
        puVar2 = (undefined4 *)FUN_00442914();
        *puVar2 = uVar5;
      }
      (*pcRam01110b08)(*puRam00e9c470,uStack_28,param_1,auStack_24[0],param_2,param_3);
      return;
    }
    piVar4 = (int *)FUN_00442914();
    if (*piVar4 == 0x550002) {
      puVar2 = (undefined4 *)FUN_00442914();
      *puVar2 = uVar5;
    }
  }
  FUN_0036c8ac(param_1,param_2,param_3);
  return;
}

