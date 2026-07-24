/* 0x0012ed88  FUN_0012ed88  size=276 bytes */


void FUN_0012ed88(undefined4 *param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined8 uVar4;
  
  iVar3 = 10;
  *param_1 = 0xe08db0;
  param_1[5] = 1;
  param_1[0x4c] = 0;
  param_1[3] = 0;
  param_1[4] = 0;
  param_1[2] = 0;
  param_1[1] = 0;
  param_1[0x49] = 0;
  param_1[0x4a] = 0;
  param_1[0x4b] = 0;
  puVar2 = param_1;
  do {
    puVar2[0x4d] = 0;
    puVar2[0x57] = 0;
    puVar2[0x61] = 0;
    puVar2[0x6b] = 0;
    puVar2[0x75] = 0;
    puVar2[0x7f] = 0;
    puVar2[0x89] = 0;
    puVar2[0x93] = 0;
    puVar2 = puVar2 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  param_1[0x9d] = 0;
  iVar3 = 1;
  puVar2 = param_1 + 0x9e;
  do {
    FUN_00373dd0(iVar3);
    uVar4 = FUN_0037678c();
    FUN_00373704((int)((ulonglong)uVar4 >> 0x20),(int)uVar4,0x4052c000,0);
    iVar3 = iVar3 + 1;
    uVar1 = FUN_00374010();
    *puVar2 = uVar1;
    puVar2 = puVar2 + 1;
  } while (iVar3 < 0x2711);
  FUN_0039acec(param_1 + 0xc,0,0x78);
  FUN_0039acec(param_1 + 0x2a,0,0x78);
  param_1[6] = 100;
  param_1[0x48] = 0;
  return;
}

