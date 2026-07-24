/* 0x00121400  FUN_00121400  size=188 bytes */


undefined4 FUN_00121400(int param_1,int param_2)

{
  int iVar1;
  
  if (param_2 != 0) {
    return 0;
  }
  iVar1 = param_1 + 4;
  if (0xf < *(uint *)(param_1 + 0x18)) {
    iVar1 = *(int *)(param_1 + 4);
  }
  FUN_0005e784(0,3,0xb,0xd4bc0c,0x6625bc,0x5a3,0xd4bc2c,0x6625cc,iVar1);
  return 0xffffffff;
}

