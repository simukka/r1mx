/* 0x000749f0  FUN_000749f0  size=192 bytes */


void FUN_000749f0(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = FUN_0005e8d8();
  FUN_00074944(uVar1,9,0);
  if (param_1 < 1) {
    return;
  }
  do {
    uVar3 = 0;
    do {
      iVar2 = uVar3 * 0x10;
      uVar3 = uVar3 + 1;
      if ((*(char *)(iVar2 + 0xe10c69) != '\0') &&
         (iVar2 = FUN_001aca04(*(undefined4 *)(iVar2 + 0xe10c60),0), iVar2 == 0)) {
        return;
      }
    } while (uVar3 < 6);
    FUN_001d9a58(10);
    param_1 = param_1 + -10;
    if (param_1 < 1) {
      return;
    }
  } while( true );
}

