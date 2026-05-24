/* 0x0002d400  FUN_0002d400  size=668 bytes */


int FUN_0002d400(int *param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 extraout_r4;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = *param_1;
  uVar1 = 0x38000a;
  iVar4 = *(int *)(param_1[1] + 0xc);
  if (((param_2 != (int *)0x0) && (uVar1 = 0x38000e, *param_2 != 0 || param_2[1] != 0)) &&
     (uVar1 = 0x380005, (*(byte *)(param_1[1] + 0x42) & 0x10) == 0)) {
    if ((param_1[0x10] & 2U) != 0) {
      if ((*param_2 != -1) || (uVar1 = 0xffffffff, param_2[1] != -1)) {
        iVar3 = param_2[1] + (uint)*(ushort *)(iVar5 + 0x5c);
        FUN_003cc82c(*param_2 + (uint)CARRY4(param_2[1],(uint)*(ushort *)(iVar5 + 0x5c)) + -1 +
                     (uint)(iVar3 != 0),iVar3 + -1,*(undefined1 *)(iVar5 + 0x84));
        uVar1 = extraout_r4;
      }
      iVar3 = (**(code **)(*(int *)(iVar5 + 0x30) + 0x14))(param_1,uVar1);
      if (iVar3 == -1) {
        return -1;
      }
      if ((*param_2 == -1) && (param_2[1] == -1)) {
        piVar2 = (int *)param_1[1];
        iVar3 = (uint)*(ushort *)(iVar5 + 0x5e) * (param_1[8] - *(int *)(param_1[1] + 0xc)) <<
                (*(byte *)(iVar5 + 0x84) & 0x3f);
        *piVar2 = iVar3 >> 0x1f;
        piVar2[1] = iVar3;
      }
      else {
        piVar2 = (int *)param_1[1];
        iVar3 = param_2[1];
        *piVar2 = *param_2;
        piVar2[1] = iVar3;
      }
      iVar3 = (**(code **)(*(int *)(iVar5 + 0x2c) + 8))(param_1,0,0);
      if (iVar3 == -1) {
        return -1;
      }
      if (iVar4 != 0) {
        uVar1 = *(undefined4 *)(param_1[1] + 0xc);
        *(int *)(param_1[1] + 0xc) = iVar4;
        (**(code **)(*(int *)(iVar5 + 0x30) + 8))(param_1,0xffffffff,0);
        iVar4 = 1;
        *(undefined4 *)(param_1[1] + 0xc) = uVar1;
        piVar2 = *(int **)(*param_1 + 0x3c);
        if (1 < *(ushort *)(param_1[1] + 0x40)) {
          do {
            if (((piVar2[0x11] != 0) && (piVar2 != param_1)) && (piVar2[1] == param_1[1])) {
              iVar4 = iVar4 + 1;
              piVar2[4] = piVar2[2];
              piVar2[5] = piVar2[3];
              piVar2[2] = 0;
              piVar2[3] = 0;
              piVar2[9] = 0;
              piVar2[6] = 0;
            }
            piVar2 = piVar2 + 0x12;
          } while (iVar4 < (int)(uint)*(ushort *)(param_1[1] + 0x40));
        }
      }
      iVar4 = (**(code **)(*(int *)(iVar5 + 0x30) + 0xc))(param_1,0xffffffff,0);
      return -(uint)(iVar4 == -1);
    }
    uVar1 = 0x380011;
  }
  FUN_00442990(uVar1);
  return -1;
}

