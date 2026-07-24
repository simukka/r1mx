/* 0x00393e94  FUN_00393e94  size=292 bytes */


void FUN_00393e94(undefined4 param_1,undefined4 param_2,uint param_3,undefined8 *param_4,
                 undefined4 param_5)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  
  if ((param_3 & 2) == 0) {
    uVar2 = (*pcRam01110aec)();
  }
  else {
    uVar2 = *(undefined4 *)((int)param_4 + 0xc);
  }
  if ((param_3 & 1) == 0) {
    uVar4 = (*pcRam01110af0)(param_1);
  }
  else {
    uVar4 = *param_4;
  }
  if ((param_3 & 0x20) != 0) {
    param_2 = *(undefined4 *)(param_4 + 1);
  }
  if ((param_3 & 4) == 0) {
    uVar3 = (*pcRam01110ae8)(param_1);
  }
  else {
    uVar3 = *(undefined4 *)(param_4 + 2);
  }
  uVar1 = (*pcRam01110ae0)(param_1,param_5);
  if ((param_3 & 0x10) != 0) {
    uVar1 = *(undefined4 *)(param_4 + 3);
  }
  uVar5 = FUN_0036fd0c();
  (*pcRam01110ad8)(param_1,(int)uVar5,(int)((ulonglong)uVar4 >> 0x20),(int)uVar4,param_2,uVar1,uVar3
                   ,uVar2,param_5);
  FUN_0036fd24((int)((ulonglong)uVar5 >> 0x20));
  return;
}

