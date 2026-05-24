/* 0x0039b7f4  FUN_0039b7f4  size=360 bytes */


/* WARNING: Removing unreachable block (ram,0x0039b828) */

undefined4 FUN_0039b7f4(uint param_1,undefined4 *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  uVar5 = param_1 / 0x15180;
  param_1 = param_1 % 0x15180;
  uVar6 = uVar5 / 0x16d;
  while (iVar1 = FUN_0039b74c(uVar6,0), (int)uVar5 < iVar1) {
    uVar6 = uVar6 - 1;
  }
  iVar1 = (int)(uVar5 + 4) % 7;
  param_2[6] = iVar1;
  if (iVar1 < 0) {
    param_2[6] = iVar1 + 7;
  }
  iVar2 = FUN_0039b74c(uVar6,0);
  iVar2 = uVar5 - iVar2;
  iVar4 = 0;
  iVar3 = FUN_0039b780(uVar6 + 0x46,1,0);
  iVar1 = iVar4;
  if (iVar3 <= iVar2) {
    do {
      iVar4 = iVar1 + 1;
      iVar1 = FUN_0039b780(uVar6 + 0x46,iVar1 + 2,0);
      if (iVar2 < iVar1) break;
      iVar1 = iVar4;
    } while (iVar4 < 0xb);
  }
  iVar3 = uVar6 + 0x46;
  param_2[4] = iVar4;
  param_2[5] = iVar3;
  iVar1 = FUN_0039b780(iVar3,iVar4,0);
  param_2[3] = (iVar2 - iVar1) + 1;
  iVar1 = FUN_0039b780(iVar3,iVar4);
  param_2[2] = (int)param_1 / 0xe10;
  param_2[7] = iVar1 + -1;
  FUN_00399cec((int)param_1 % 0xe10,0x3c,&uStack_18);
  param_2[1] = uStack_18;
  *param_2 = uStack_14;
  return 0;
}

