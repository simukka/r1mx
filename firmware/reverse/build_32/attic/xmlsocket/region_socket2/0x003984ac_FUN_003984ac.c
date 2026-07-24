/* 0x003984ac  FUN_003984ac  size=132 bytes */


undefined4 FUN_003984ac(undefined4 param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puStack_28;
  undefined4 uStack_24;
  int iStack_20;
  undefined4 uStack_1c;
  int iStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  iStack_18 = FUN_0039b0f0();
  uStack_14 = 0x3a8530;
  iStack_20 = iStack_18 + 1;
  puStack_28 = &uStack_1c;
  uStack_10 = 1;
  uStack_24 = 2;
  uStack_1c = param_1;
  puVar1 = (undefined4 *)FUN_00398e40();
  iVar2 = FUN_00397a4c(*puVar1,&puStack_28);
  if (iVar2 == 0) {
    uVar3 = 10;
  }
  else {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

