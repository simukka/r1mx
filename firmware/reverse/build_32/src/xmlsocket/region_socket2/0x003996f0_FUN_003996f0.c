/* 0x003996f0  FUN_003996f0  size=408 bytes */


int FUN_003996f0(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined1 auStack_468 [12];
  undefined1 *puStack_45c;
  undefined4 uStack_458;
  undefined4 uStack_454;
  ushort uStack_450;
  undefined2 uStack_44e;
  undefined1 *puStack_44c;
  undefined4 uStack_448;
  undefined4 uStack_444;
  undefined4 uStack_440;
  undefined4 uStack_43c;
  undefined4 uStack_42c;
  undefined4 uStack_428;
  undefined1 auStack_418 [1032];
  
  if ((*(int *)(param_1 + 4) == param_1) && (*(char *)(param_1 + 10) == 'f')) {
    if ((((*(ushort *)(param_1 + 0x18) & 8) == 0) || (*(int *)(param_1 + 0x1c) == 0)) &&
       (iVar1 = FUN_00399600(), iVar1 != 0)) {
      iVar1 = -1;
    }
    else if (((*(ushort *)(param_1 + 0x18) & 0x1a) == 10) && (-1 < *(short *)(param_1 + 0x1a))) {
      uStack_450 = *(ushort *)(param_1 + 0x18) & 0xfffd;
      puStack_45c = auStack_418;
      uStack_44e = *(undefined2 *)(param_1 + 0x1a);
      uStack_454 = 0x400;
      uStack_448 = 0x400;
      uStack_444 = 0;
      uStack_458 = 0;
      uStack_440 = 0;
      uStack_43c = 0;
      uStack_42c = 0;
      uStack_428 = 0;
      puStack_44c = puStack_45c;
      FUN_00442e48(auStack_468,0x66);
      iVar1 = FUN_003c9f44(param_2,param_3,0x3a9888,auStack_468);
      if ((-1 < iVar1) && (iVar2 = FUN_00396d3c(auStack_468), iVar2 != 0)) {
        iVar1 = -1;
      }
      if ((uStack_450 & 0x40) != 0) {
        *(ushort *)(param_1 + 0x18) = *(ushort *)(param_1 + 0x18) | 0x40;
      }
      FUN_00442e64(auStack_468);
    }
    else {
      iVar1 = FUN_003c9f44(param_2,param_3,0x3a9888,param_1);
      if ((*(int *)(param_1 + 4) == param_1) &&
         ((*(char *)(param_1 + 10) == 'f' && ((*(ushort *)(param_1 + 0x18) & 0x40) != 0)))) {
        iVar1 = -1;
      }
    }
  }
  else {
    iVar1 = -1;
  }
  return iVar1;
}

