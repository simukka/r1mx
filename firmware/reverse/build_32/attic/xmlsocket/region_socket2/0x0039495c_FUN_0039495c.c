/* 0x0039495c  FUN_0039495c  size=300 bytes */


undefined4 FUN_0039495c(int param_1,uint param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uStack_28;
  int *piStack_24;
  
  piStack_24 = (int *)0xe272a8;
  uStack_28 = FUN_00497e84(uRam00e272c8);
  if (uStack_28 == 0) {
    puVar1 = (undefined4 *)FUN_00442914();
    *puVar1 = 0x550002;
    uVar2 = 0xffffffff;
  }
  else {
    FUN_00458bdc(1,uStack_28,uRam0108b7b4);
    uStack_28 = (*pcRam01110acc)(uStack_28);
    uVar3 = 0;
    if (uRam0108b79c != 0) {
      do {
        (*pcRam01110adc)(uStack_28 + uVar3 * iRam0108b790);
        uVar3 = uVar3 + 1;
      } while (uVar3 < uRam0108b79c);
    }
    if (*piStack_24 != 0) {
      FUN_003948ec(uRam00e9c470,uStack_28 & piStack_24[7],uRam0108b7ac >> (uRam0108b7c4 & 0x3f));
    }
    FUN_003940f4(&uStack_28,param_1 + (param_2 >> (uRam0108b7bc & 0x3f)) * 4,4);
    uVar2 = 0;
  }
  return uVar2;
}

