/* 0x00074c48  FUN_00074c48  size=464 bytes */


int FUN_00074c48(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  iVar4 = 0;
  uVar5 = 0;
  do {
    iVar1 = uVar5 * 0x10;
    if ((*(char *)(iVar1 + 0xe10c6b) != '\0') && (*(char *)(iVar1 + 0xe10c6a) != '\0')) {
      iVar3 = param_1 + 0x28;
      if (0xf < *(uint *)(param_1 + 0x3c)) {
        iVar3 = *(int *)(param_1 + 0x28);
      }
      FUN_0005e784(3,1,5,0xd3f794,0x65e18c,0x592,0xd3f8b0,iVar3,*(undefined4 *)(iVar1 + 0xe10c60));
      iVar3 = FUN_0044f4cc(*(undefined4 *)(iVar1 + 0xe10c60),2,0);
      iVar4 = iVar4 + 1;
      if (iVar3 == -1) {
        iVar3 = param_1 + 0x28;
        if (0xf < *(uint *)(param_1 + 0x3c)) {
          iVar3 = *(int *)(param_1 + 0x28);
        }
        FUN_0005e784(0,3,5,0xd3f794,0x65e18c,0x59a,0xd3f8c8,iVar3,*(undefined4 *)(iVar1 + 0xe10c60))
        ;
      }
      else {
        iVar2 = FUN_0044e510(iVar3,0xbd000004,2);
        if (iVar2 != 0) {
          iVar2 = param_1 + 0x28;
          if (0xf < *(uint *)(param_1 + 0x3c)) {
            iVar2 = *(int *)(param_1 + 0x28);
          }
          FUN_0005e784(0,3,5,0xd3f794,0x65e18c,0x5a0,0xd3f8f0,iVar2,
                       *(undefined4 *)(iVar1 + 0xe10c60));
        }
        FUN_0044f9fc(iVar3);
      }
    }
    uVar5 = uVar5 + 1;
  } while (uVar5 < 6);
  FUN_001d9a58(100);
  return iVar4;
}

