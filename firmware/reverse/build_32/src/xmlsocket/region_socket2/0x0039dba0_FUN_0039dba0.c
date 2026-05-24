/* 0x0039dba0  FUN_0039dba0  size=236 bytes */


undefined4
FUN_0039dba0(int *param_1,int param_2,uint param_3,uint param_4,undefined4 param_5,
            undefined4 param_6)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  int *piVar4;
  
  puVar1 = (undefined4 *)FUN_0039efe4(0x28);
  *param_1 = (int)puVar1;
  if (puVar1 != (undefined4 *)0x0) {
    if (param_4 < param_3) {
      param_3 = param_4;
    }
    puVar1[3] = param_2;
    puVar1[6] = param_3;
    puVar1[5] = param_3;
    puVar1[4] = param_3;
    puVar1[7] = param_4;
    puVar1[8] = param_5;
    puVar1[9] = param_6;
    uVar2 = FUN_005ab360(0,1);
    *puVar1 = uVar2;
    uVar2 = FUN_005ab360(0,0);
    *(undefined4 *)(*param_1 + 4) = uVar2;
    piVar4 = (int *)(*param_1 + 8);
    for (; param_3 != 0; param_3 = param_3 - 1) {
      iVar3 = FUN_0039efe4(param_2 + 8);
      *piVar4 = iVar3;
      if (*(code **)(*param_1 + 0x20) != reset_vector) {
        (**(code **)(*param_1 + 0x20))(iVar3 + 8,param_2);
      }
      piVar4 = (int *)*piVar4;
    }
  }
  return 0;
}

