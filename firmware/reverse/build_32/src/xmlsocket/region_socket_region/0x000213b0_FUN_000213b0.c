/* 0x000213b0  FUN_000213b0  size=164 bytes */


undefined4 FUN_000213b0(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = param_1 * 0x430 + 0x108e964;
  uVar1 = 0xffffffff;
  if (*(char *)(param_2 * 600 + param_1 * 0x430 + 0x108e8d4) == '\0') {
    FUN_005accf4(iVar2,0xffffffff);
    uVar1 = FUN_00020988(param_1,param_2,0xb0,0xd8,0);
    FUN_005ad104(iVar2);
  }
  return uVar1;
}

