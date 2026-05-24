/* 0x0039e014  FUN_0039e014  size=168 bytes */


undefined4 FUN_0039e014(undefined4 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  
  uVar1 = 0;
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 1;
  }
  else {
    if ((code *)param_1[0xe] != reset_vector) {
      (*(code *)param_1[0xe])();
    }
    puVar3 = param_1 + 5;
    puVar4 = (undefined4 *)0xe27588;
    iVar2 = 7;
    do {
      puVar4 = puVar4 + 3;
      puVar3 = puVar3 + 1;
      FUN_0039dfc0(*puVar3,*puVar4);
      FUN_0039f108(*puVar3);
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
    if (param_1[0xf] != 0) {
      FUN_0039f108(param_1[0xf]);
    }
    FUN_0039f108(*param_1);
    FUN_0039f108(param_1);
  }
  return uVar1;
}

