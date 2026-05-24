/* 0x00396e7c  FUN_00396e7c  size=308 bytes */


undefined1 * FUN_00396e7c(undefined1 *param_1,uint param_2,int param_3)

{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  uint uVar4;
  int iVar5;
  
  if ((*(int *)(param_3 + 4) == param_3) && (*(char *)(param_3 + 10) == 'f')) {
    if (param_2 < 2) {
      param_1 = (undefined1 *)0x0;
    }
    else {
      param_2 = param_2 - 1;
      puVar3 = param_1;
      do {
        uVar4 = *(uint *)(param_3 + 0x10);
        if (uVar4 == 0) {
          iVar1 = FUN_0039856c(param_3);
          if (iVar1 != 0) {
            if (puVar3 == param_1) {
              return (undefined1 *)0x0;
            }
            break;
          }
          uVar4 = *(uint *)(param_3 + 0x10);
        }
        iVar1 = *(int *)(param_3 + 0xc);
        if (param_2 < uVar4) {
          uVar4 = param_2;
        }
        iVar2 = FUN_0039abf8(iVar1,10,uVar4);
        if (iVar2 != 0) {
          iVar5 = (iVar2 + 1) - iVar1;
          *(int *)(param_3 + 0xc) = iVar2 + 1;
          *(int *)(param_3 + 0x10) = *(int *)(param_3 + 0x10) - iVar5;
          FUN_0036c8ac(iVar1,puVar3,iVar5);
          puVar3[iVar5] = 0;
          return param_1;
        }
        *(uint *)(param_3 + 0x10) = *(int *)(param_3 + 0x10) - uVar4;
        *(uint *)(param_3 + 0xc) = *(int *)(param_3 + 0xc) + uVar4;
        FUN_0036c8ac(iVar1,puVar3,uVar4);
        param_2 = param_2 - uVar4;
        puVar3 = puVar3 + uVar4;
      } while (param_2 != 0);
      *puVar3 = 0;
    }
  }
  else {
    param_1 = (undefined1 *)0x0;
  }
  return param_1;
}

