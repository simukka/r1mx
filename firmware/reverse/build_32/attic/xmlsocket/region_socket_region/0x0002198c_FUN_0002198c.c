/* 0x0002198c  FUN_0002198c  size=220 bytes */


undefined4 FUN_0002198c(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = param_2 * 600 + param_1 * 0x430 + 0x108e6a0;
  if ((((param_1 < 2 && -1 < (int)((-1 - param_2) + (uint)(param_2 == 0))) && (iRam00e10734 != 0))
      && (*(int *)(param_1 * 0x430 + 0x108e9e4) != 0)) && (*(char *)(iVar2 + 0x234) == '\0')) {
    uVar1 = 0;
    if ((*(ushort *)(iVar2 + 0xa4) & 0x20) != 0) {
      uVar1 = 0xe7;
      if ((*(ushort *)(iVar2 + 0xa6) & 0x1000) == 0) {
        if ((*(ushort *)(iVar2 + 0xa6) & 0x2000) == 0) {
          return 0;
        }
        uVar1 = 0xea;
      }
      uVar1 = FUN_00020988(param_1,param_2,uVar1,0,0);
    }
    return uVar1;
  }
  return 0xffffffff;
}

