/* 0x0037d6a4  FUN_0037d6a4  size=280 bytes */


undefined4 FUN_0037d6a4(int param_1,int param_2,uint param_3,int param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int *piVar4;
  uint uVar5;
  undefined4 uVar6;
  
  uVar5 = 0;
  uVar1 = 0;
  uVar6 = 0xffffffff;
  if (piRam00e9c5c0 != (int *)0xe9c5c0) {
    piVar4 = piRam00e9c5c0;
    do {
      while (((piVar4[3] != param_1 || (uVar3 = piVar4[7], (param_3 & 0x1f) != (uVar3 & 0x1f))) ||
             ((((uVar3 & 0x200000) == 0 || (piVar4[6] != param_2)) &&
              (((((uVar3 & 0x40000) == 0 || (piVar4[6] != *(int *)(param_2 + 0x94))) &&
                ((uVar3 & 0x400000) == 0)) && ((uVar3 >> 0x17 & 1 & (uint)(param_2 == -1)) == 0)))))
             )) {
LAB_0037d6e8:
        piVar4 = (int *)*piVar4;
        if (piVar4 == (int *)0xe9c5c0) goto LAB_0037d764;
      }
      uVar6 = 0;
      if (piVar4[8] == 0) {
        uVar1 = uVar1 | uVar3;
        uVar5 = uVar5 | piVar4[9];
        if ((piVar4[9] & 1U) != 0) {
          iVar2 = piVar4[0xb];
          *(int *)(param_4 + 0x28) = piVar4[10];
          *(int *)(param_4 + 0x2c) = iVar2;
        }
        goto LAB_0037d6e8;
      }
      piVar4[8] = piVar4[8] + -1;
      piVar4 = (int *)*piVar4;
    } while (piVar4 != (int *)0xe9c5c0);
  }
LAB_0037d764:
  *(uint *)(param_4 + 0x1c) = uVar1;
  *(uint *)(param_4 + 0x24) = uVar5;
  return uVar6;
}

