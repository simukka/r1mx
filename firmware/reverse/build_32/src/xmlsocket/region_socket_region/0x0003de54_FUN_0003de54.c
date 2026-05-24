/* 0x0003de54  FUN_0003de54  size=504 bytes */


void FUN_0003de54(int param_1,int param_2,undefined1 param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined1 *puStack_20;
  int iStack_1c;
  
  if (((param_1 <= iRam00e108e0) && (param_2 != 0)) && (param_4 != 0)) {
    iVar1 = FUN_0044f4cc(*(undefined4 *)(param_1 * 4 + 0xe108cc),2,0);
    if (iVar1 == -1) {
      FUN_0005e784(2,3,0xc,0xd38d1c,0x65cdd0,0x6cd,0xd3a830);
    }
    else {
      iVar2 = FUN_0044e510(iVar1,0x69000001,param_2);
      if (iVar2 < 0) {
        FUN_0044f9fc(iVar1);
        FUN_0005e784(2,3,0xc,0xd38d1c,0x65cdd0,0x6d4,0xd3a804);
      }
      else {
        puVar3 = (undefined1 *)FUN_0045964c(0x100,param_4);
        if (puVar3 == (undefined1 *)0x0) {
          FUN_0005e784(2,3,0xc,0xd38d1c,0x65cdd0,0x6da,0xd3a840,param_4);
        }
        else {
          FUN_0039acec(puVar3,0xaa,param_4);
          *puVar3 = param_3;
          puStack_20 = puVar3;
          iStack_1c = param_4;
          iVar2 = FUN_0044e510(iVar1,0x69000003,&puStack_20);
          if (iVar2 < 0) {
            FUN_0044f9fc(iVar1);
            FUN_0005e784(2,3,0xc,0xd38d1c,0x65cdd0,0x6e9,0xd3a88c);
            FUN_0045b580(puVar3);
          }
          else {
            FUN_00492c58(puVar3,param_4,1);
            FUN_0045b580(puVar3);
            FUN_0044f9fc(iVar1);
            FUN_00009518();
            FUN_005b1edc();
          }
        }
      }
    }
  }
  return;
}

