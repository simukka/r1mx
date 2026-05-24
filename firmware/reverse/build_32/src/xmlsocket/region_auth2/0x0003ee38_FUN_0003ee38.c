/* 0x0003ee38  FUN_0003ee38  size=588 bytes */


void FUN_0003ee38(undefined4 param_1,undefined4 *param_2,undefined4 *param_3,undefined4 *param_4)

{
  int iVar1;
  int iVar2;
  char acStack_78 [84];
  
  *param_2 = 0;
  *param_3 = 0;
  *param_4 = 0;
  iVar2 = 0;
  do {
    iVar1 = FUN_00396e7c(acStack_78,0x50,param_1);
    if (iVar1 == 0) {
      FUN_0005e784(2,3,0xc,0xd38d1c,0x65ce5c,0xb6c,0xd3acb8);
      return;
    }
    if (acStack_78[0] != '#') {
      if (iVar2 == 1) {
        iVar1 = FUN_003c9eac(acStack_78,0xd3ac84,param_3,param_2);
        if (iVar1 != 2) {
          FUN_0005e784(2,3,0xc,0xd38d1c,0x65ce5c,0xb7c,0xd3ac8c);
          return;
        }
      }
      else if (iVar2 < 2) {
        if (iVar2 != 0) {
LAB_0003f028:
          FUN_0005e784(2,3,0xc,0xd38d1c,0x65ce5c,0xb8c,0xd3acd4);
          *param_2 = 0;
          *param_3 = 0;
          *param_4 = 0;
          return;
        }
        iVar1 = FUN_0039b188(0xd3ac60,acStack_78,2);
        if (iVar1 != 0) {
          FUN_0005e784(2,3,0xc,0xd38d1c,0x65ce5c,0xb75,0xd3acec);
          return;
        }
      }
      else {
        if (iVar2 != 2) goto LAB_0003f028;
        iVar1 = FUN_003c9eac(acStack_78,0xd57218,param_4);
        if (iVar1 != 1) {
          *param_2 = 0;
          *param_3 = 0;
          *param_4 = 0;
          FUN_0005e784(2,3,0xc,0xd38d1c,0x65ce5c,0xb86,0xd3ac64);
          return;
        }
      }
      iVar2 = iVar2 + 1;
    }
    if (2 < iVar2) {
      return;
    }
  } while( true );
}

