/* 0x00399508  FUN_00399508  size=248 bytes */


uint FUN_00399508(byte param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  
  *(undefined4 *)(param_2 + 0x14) = *(undefined4 *)(param_2 + 0x24);
  if ((((*(ushort *)(param_2 + 0x18) & 8) == 0) || (*(int *)(param_2 + 0x1c) == 0)) &&
     (iVar1 = FUN_00399600(param_2), iVar1 != 0)) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = (uint)param_1;
    iVar1 = *(int *)(param_2 + 0xc) - *(int *)(param_2 + 0x1c);
    if (*(int *)(param_2 + 0x20) <= iVar1) {
      iVar1 = FUN_00396d3c(param_2);
      if (iVar1 != 0) {
        return 0xffffffff;
      }
      iVar1 = 0;
    }
    pbVar3 = *(byte **)(param_2 + 0xc);
    *(int *)(param_2 + 0x14) = *(int *)(param_2 + 0x14) + -1;
    *pbVar3 = param_1;
    *(byte **)(param_2 + 0xc) = pbVar3 + 1;
    if (((*(int *)(param_2 + 0x20) == iVar1 + 1) ||
        (((*(ushort *)(param_2 + 0x18) & 1) != 0 && (uVar2 == 10)))) &&
       (iVar1 = FUN_00396d3c(param_2), iVar1 != 0)) {
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}

