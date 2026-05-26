/* 0x0037b1e4  FUN_0037b1e4  size=780 bytes */


int FUN_0037b1e4(undefined4 param_1,int param_2,uint param_3,undefined4 param_4,uint param_5,
                undefined4 param_6,undefined4 param_7,undefined4 *param_8)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int *piVar6;
  byte in_cr0;
  byte in_cr1;
  byte unaff_cr2;
  byte unaff_cr3;
  byte unaff_cr4;
  byte in_cr5;
  byte in_cr6;
  byte in_cr7;
  undefined1 auStack_78 [48];
  int aiStack_48 [4];
  uint uStack_38;
  
  uStack_38 = (uint)(in_cr0 & 0xf) << 0x1c | (uint)(in_cr1 & 0xf) << 0x18 |
              (uint)(unaff_cr2 & 0xf) << 0x14 | (uint)(unaff_cr3 & 0xf) << 0x10 |
              (uint)(unaff_cr4 & 0xf) << 0xc | (uint)(in_cr5 & 0xf) << 8 | (uint)(in_cr6 & 0xf) << 4
              | (uint)(in_cr7 & 0xf);
  uVar5 = param_3 & 0xf40000;
  iVar1 = iRam00e3a790;
  if ((param_5 >> 3 & 1) == 0) {
    if (((param_5 & 0x10) != 0) && (iRam00e9c030 == 0)) {
      return 0x501;
    }
    iVar3 = FUN_0037ac3c(uVar5,param_2,aiStack_48);
    iVar1 = aiStack_48[0];
    if (iVar3 == -1) {
      return 0x505;
    }
  }
  aiStack_48[0] = iVar1;
  uVar2 = 0;
  if (pcRam00e9c578 != reset_vector) {
    uVar2 = (*pcRam00e9c578)(aiStack_48[0],0);
  }
  iVar1 = FUN_005bb3cc(param_1,param_3 & 0xf,0x382330);
  if (iVar1 == 0) {
    if (pcRam00e9c578 != reset_vector) {
      (*pcRam00e9c578)(uVar2,0);
    }
    FUN_0039acec(auStack_78,0,0x28);
    FUN_005b17d0();
    if (piRam00e9c5c0 != (int *)0xe9c5c0) {
      piVar6 = piRam00e9c5c0;
      do {
        uVar4 = piVar6[7];
        if ((((uVar4 & 0x10) != 0) &&
            ((((uVar5 == 0x200000 &&
               ((((uVar4 & 0x200000) != 0 && (piVar6[6] == param_2)) ||
                (((uVar4 & 0x40000) != 0 && (piVar6[6] == aiStack_48[0])))))) ||
              ((uVar5 == 0x40000 &&
               (((uVar4 & 0x200000) != 0 || (((uVar4 & 0x40000) != 0 && (piVar6[6] == param_2)))))))
              ) || (((uVar5 == 0x400000 && ((uVar4 & 0x240000) != 0)) || ((uVar4 & 0x400000) != 0)))
             ))) && (iVar1 = FUN_005bb5f0(auStack_78,uVar4 & 0xf,piVar6[3]), iVar1 != 0)) {
          FUN_005b1894();
          return iVar1;
        }
        piVar6 = (int *)*piVar6;
      } while (piVar6 != (int *)0xe9c5c0);
    }
    FUN_005b1894();
    iVar1 = FUN_005bb5f0(auStack_78,param_3 & 0xf,param_1);
    if (iVar1 == 0) {
      iVar3 = FUN_0037b0a4(param_1,0,param_2,param_3 | 0x10,param_4,param_5,param_6,param_7);
      iVar1 = 0x50b;
      if (iVar3 != 0) {
        iVar1 = 0;
        *param_8 = *(undefined4 *)(iVar3 + 8);
      }
    }
  }
  else if (pcRam00e9c578 == reset_vector) {
    iVar1 = 0x502;
  }
  else {
    (*pcRam00e9c578)(uVar2,0);
    iVar1 = 0x502;
  }
  return iVar1;
}

