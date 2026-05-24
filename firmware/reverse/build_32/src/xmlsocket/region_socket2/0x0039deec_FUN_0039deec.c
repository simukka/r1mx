/* 0x0039deec  FUN_0039deec  size=212 bytes */


undefined4 FUN_0039deec(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int *piVar5;
  uint uVar6;
  
  uVar4 = 0;
  if (iRam00e9c6a4 == 0) {
    uVar4 = 3;
  }
  else {
    puVar1 = (undefined4 *)FUN_0039efe4(0x40);
    *param_1 = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      uVar4 = 0xc;
    }
    else {
      iVar2 = FUN_0039b0f0(param_2);
      uVar3 = FUN_0039efe4(iVar2 + 1);
      *puVar1 = uVar3;
      FUN_0039af30(uVar3,param_2);
      iVar2 = *param_1;
      *(undefined4 *)(iVar2 + 0x38) = param_4;
      piVar5 = (int *)0xe27588;
      *(undefined4 *)(iVar2 + 0x34) = param_3;
      uVar6 = 0;
      do {
        piVar5 = piVar5 + 3;
        uVar3 = FUN_0039efe4(*piVar5 << 2);
        iVar2 = uVar6 * 4;
        uVar6 = uVar6 + 1;
        *(undefined4 *)(*param_1 + iVar2 + 0x18) = uVar3;
      } while (uVar6 < 7);
    }
  }
  return uVar4;
}

