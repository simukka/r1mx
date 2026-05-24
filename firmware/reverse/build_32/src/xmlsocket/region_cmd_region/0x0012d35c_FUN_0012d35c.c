/* 0x0012d35c  FUN_0012d35c  size=360 bytes */


void FUN_0012d35c(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined1 auStack_30 [16];
  undefined1 auStack_20 [20];
  
  if (*(int *)(param_1 + 40000) == 0) {
    iVar1 = FUN_0044f4cc(0xd4155c,2,0);
    if (-1 < iVar1) {
      iVar2 = FUN_0044e144(iVar1,auStack_20,0xd);
      if (iVar2 == 0xd) {
        iVar2 = FUN_0039b188(auStack_20,0xd4bfa0,0xd);
        if (iVar2 == 0) {
          iVar2 = FUN_0044e144(iVar1,auStack_30,10);
          if (iVar2 != 10) {
            puVar3 = (undefined4 *)FUN_00398e40();
            FUN_0039995c(*puVar3,0xd4c038);
          }
          iVar2 = FUN_00399bd8(auStack_30);
          *(int *)(param_1 + 40000) = iVar2;
          if (iVar2 < 0x17) {
            puVar3 = (undefined4 *)FUN_00398e40();
            FUN_0039995c(*puVar3,0xd4c054);
          }
        }
        else {
          puVar3 = (undefined4 *)FUN_00398e40();
          FUN_0039995c(*puVar3,0xd4c0b4);
        }
      }
      else {
        puVar3 = (undefined4 *)FUN_00398e40();
        FUN_0039995c(*puVar3,0xd4c018);
      }
      FUN_0044f9fc(iVar1);
      return;
    }
    puVar3 = (undefined4 *)FUN_00398e40();
    FUN_0039995c(*puVar3,0xd4c078,iVar1);
    FUN_0012d1ec(param_1);
  }
  return;
}

