/* 0x005f0030  FUN_005f0030  size=364 bytes */


bool FUN_005f0030(int param_1,uint param_2,int param_3)

{
  uint uVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  uint uVar4;
  
  if (0xfffffffe < param_2) {
    FUN_002513e0();
  }
  uVar1 = *(uint *)(param_1 + 0x18);
  if (param_2 <= uVar1) {
    if ((param_3 != 0) && (param_2 < 0x10)) {
      uVar4 = *(uint *)(param_1 + 0x14);
      if (param_2 < *(uint *)(param_1 + 0x14)) {
        uVar4 = param_2;
      }
      if (0xf < uVar1) {
        uVar3 = *(undefined4 *)(param_1 + 4);
        if (uVar4 != 0) {
          FUN_0039ac74(param_1 + 4,uVar3,uVar4);
        }
        FUN_00245c34(uVar3);
      }
      *(undefined4 *)(param_1 + 0x18) = 0xf;
      *(uint *)(param_1 + 0x14) = uVar4;
      *(undefined1 *)(param_1 + 4 + uVar4) = 0;
      return param_2 != 0;
    }
    if (param_2 == 0) {
      puVar2 = (undefined1 *)(param_1 + 4);
      if (0xf < uVar1) {
        puVar2 = *(undefined1 **)(param_1 + 4);
      }
      *(undefined4 *)(param_1 + 0x14) = 0;
      *puVar2 = 0;
    }
    return param_2 != 0;
  }
  FUN_005e7bb8(param_1,param_2,*(undefined4 *)(param_1 + 0x14));
  return param_2 != 0;
}

