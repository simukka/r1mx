/* 0x000f60e4  FUN_000f60e4  size=284 bytes */


undefined4 FUN_000f60e4(undefined4 param_1,undefined4 param_2,undefined4 *param_3)

{
  int iVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 auStack_28 [16];
  
  iVar1 = FUN_000f5e68();
  uVar5 = 0;
  iVar6 = iVar1 + 1;
  if (iVar1 != 0) {
    puVar2 = (undefined1 *)FUN_000f5e68(param_1,iVar6);
    if (puVar2 != (undefined1 *)0x0) {
      *puVar2 = 0;
      uVar3 = FUN_0039b0f0(iVar6);
      FUN_000f5eb4(param_1,auStack_28,iVar6,uVar3);
      iVar1 = FUN_000f5e68(param_1,puVar2 + 1);
      if ((iVar1 != 0) &&
         (puVar2 = (undefined1 *)FUN_000f5e68(param_1,iVar1 + 1), puVar2 != (undefined1 *)0x0)) {
        *puVar2 = 0;
        uVar3 = FUN_00399bd8(iVar1 + 1);
        uVar4 = FUN_0039b0f0(iVar6);
        FUN_000f5f70(param_1,auStack_28,uVar4 >> 1,uVar3);
        iVar1 = FUN_0039ad64(auStack_28,0xd49de4);
        if (iVar1 == 0) {
          *param_3 = uVar3;
          uVar5 = 1;
        }
      }
    }
  }
  return uVar5;
}

