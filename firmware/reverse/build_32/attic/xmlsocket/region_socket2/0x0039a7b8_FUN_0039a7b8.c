/* 0x0039a7b8  FUN_0039a7b8  size=100 bytes */


undefined4 FUN_0039a7b8(undefined8 *param_1,undefined4 param_2)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00373dd0(param_2);
  uVar2 = FUN_00373704(*(undefined4 *)param_1,*(undefined4 *)((int)param_1 + 4),&MMIO_40240000,0);
  uVar1 = FUN_00373370((int)((ulonglong)uVar2 >> 0x20),(int)uVar2,(int)((ulonglong)uVar1 >> 0x20),
                       (int)uVar1);
  *param_1 = uVar1;
  return 0;
}

