/* 0x00394068  FUN_00394068  size=140 bytes */


undefined4 FUN_00394068(int param_1,uint param_2,int *param_3)

{
  uint uVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  
  uVar1 = *(uint *)(param_1 + (param_2 >> (uRam0108b7bc & 0x3f)) * 4) & uRam00e272c4;
  if (uRam00e9bf6c == uVar1) {
    puVar2 = (undefined4 *)FUN_00442914();
    *puVar2 = 0x550002;
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = uVar1 + (param_2 >> (uRam0108b7c4 & 0x3f) & uRam0108b7c8) * iRam0108b790;
    uVar3 = 0;
  }
  return uVar3;
}

