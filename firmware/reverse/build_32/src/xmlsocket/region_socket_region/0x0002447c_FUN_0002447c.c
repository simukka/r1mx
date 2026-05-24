/* 0x0002447c  FUN_0002447c  size=696 bytes */


undefined4
FUN_0002447c(int param_1,undefined4 param_2,uint param_3,undefined4 param_4,uint *param_5,
            uint param_6)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint *puVar5;
  uint *puVar6;
  uint uVar7;
  
  iVar3 = param_1 * 0x430;
  uVar4 = 0;
  if (6 < iRam00e107b4) {
    FUN_00443f20(0xd35f64,param_1,param_2,param_3,param_4,param_5,6);
  }
  uVar1 = FUN_0000a518(param_2);
  uVar2 = FUN_0000a518(param_5);
  puVar6 = param_5;
  if ((uVar1 & 3) != 0) {
    if (8 < iRam00e107b4) {
      FUN_00443f20(0xd35fe0,1,2,3,4,5,6);
    }
    return 0xffffffff;
  }
  for (; puVar5 = puVar6, param_3 != 0; param_3 = param_3 - uVar7) {
    while( true ) {
      uVar4 = uVar4 + 1;
      if (param_6 <= uVar4) {
        if (iRam00e107b4 < 9) {
          return 0xffffffff;
        }
        FUN_00443f20(0xd35fac,param_6,2,3,4,5,6);
        return 0xffffffff;
      }
      uVar7 = *(int *)(iVar3 + 0x108ea54) - (*(int *)(iVar3 + 0x108ea54) - 1U & uVar1);
      if (param_3 < uVar7) {
        uVar7 = param_3;
      }
      *puVar5 = uVar1 << 0x18 | (uVar1 & 0xff00) << 8 | uVar1 >> 8 & 0xff00 | uVar1 >> 0x18;
      uVar1 = uVar1 + uVar7;
      if (8 < iRam00e107b4) {
        FUN_00443f20(0xd35f50,*puVar5,2,3,4,5,6);
      }
      puVar5[1] = (uVar7 & 0xff00) << 8 | uVar7 << 0x18;
      puVar6 = puVar5 + 2;
      if (8 < iRam00e107b4) break;
      param_3 = param_3 - uVar7;
      puVar5 = puVar6;
      if (param_3 == 0) goto LAB_000245f8;
    }
    FUN_00443f20(0xd35f3c,puVar5[1],2,3,4,5,6);
  }
LAB_000245f8:
  puVar6[-1] = puVar6[-1] | 0x80;
  if (pcRam00e29360 != reset_vector) {
    (*pcRam00e29360)(1,param_5,uVar4 << 3);
  }
  FUN_0000a0bc(*(undefined4 *)(iVar3 + 0x108ea44),uVar2);
  return 0;
}

