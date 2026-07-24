/* 0x0039eb98  FUN_0039eb98  size=184 bytes */


int FUN_0039eb98(undefined4 *param_1)

{
  uint uVar1;
  int iVar2;
  uint *apuStack_18 [4];
  
  iVar2 = 0;
  if ((param_1 != (undefined4 *)0x0) &&
     (iVar2 = FUN_003bd1a8(apuStack_18,*param_1,3,param_1[1]), iVar2 == 0)) {
    apuStack_18[0][0x21] = 1;
    apuStack_18[0][0x37] = apuStack_18[0][0x37] | 0x80000000;
    apuStack_18[0][0x2f] = param_1[2];
    uVar1 = param_1[3];
    apuStack_18[0][0x38] = apuStack_18[0][0x38] | 0x6000;
    apuStack_18[0][0x30] = uVar1;
    *apuStack_18[0] = *apuStack_18[0] | 1;
    iVar2 = FUN_003bd67c();
    FUN_0039f108(param_1);
    FUN_003bd274(apuStack_18[0]);
  }
  return iVar2;
}

