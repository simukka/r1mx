/* 0x000366bc  FUN_000366bc  size=340 bytes */


undefined4 FUN_000366bc(int param_1,undefined4 param_2,int param_3,uint param_4,uint *param_5)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  byte bStack_30;
  byte abStack_2f [15];
  
  iVar5 = *(int *)(param_1 + 0x30);
  uVar1 = (param_4 >> 1) + param_4;
  uVar4 = *(ushort *)(param_1 + 0x5c) - 1 & uVar1;
  uVar6 = *(ushort *)(param_1 + 0x5c) - uVar4;
  iVar3 = *(int *)(iVar5 + 0x58) + *(int *)(param_1 + 0x50) * param_3;
  iVar7 = iVar3 + (uVar1 >> (*(byte *)(param_1 + 0x84) & 0x3f));
  if (2 < uVar6) {
    uVar6 = 2;
  }
  iVar3 = (**(code **)(iVar5 + 0x44))(param_1,iVar3,0,iVar7,uVar4,&bStack_30,uVar6,0);
  uVar2 = 0xffffffff;
  if (iVar3 == 0) {
    iVar7 = iVar7 + 1;
    if ((uVar6 == 1) &&
       (iVar3 = (**(code **)(iVar5 + 0x44))(param_1,iVar7,0,iVar7,0,abStack_2f,1,0), iVar3 != 0)) {
      return 0xffffffff;
    }
    if ((param_4 & 1) == 0) {
      uVar1 = (uint)bStack_30 | (abStack_2f[0] & 0xf) << 8;
    }
    else {
      uVar1 = (uint)(ushort)(CONCAT11(abStack_2f[0],bStack_30) >> 4);
    }
    *param_5 = uVar1;
    uVar2 = 0;
  }
  return uVar2;
}

