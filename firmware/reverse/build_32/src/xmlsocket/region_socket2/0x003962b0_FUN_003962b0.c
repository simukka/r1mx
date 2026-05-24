/* 0x003962b0  FUN_003962b0  size=256 bytes */


void FUN_003962b0(void)

{
  int iVar1;
  uint *puVar2;
  uint uVar3;
  
  iVar1 = FUN_003938b0(uRam00e9c470);
  uVar3 = 0;
  if (uRam0108b798 != 0) {
    puVar2 = (uint *)(iVar1 + -4);
    do {
      puVar2 = puVar2 + 1;
      if (uRam00e9bf6c != (*puVar2 & uRam00e272c4)) {
        FUN_003948ec(uRam00e9c470,*puVar2 & uRam00e272c4,uRam0108b7ac >> (uRam0108b7c4 & 0x3f));
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < uRam0108b798);
  }
  FUN_003948ec(uRam00e9c470,uRam00e9bf6c,uRam0108b7ac >> (uRam0108b7c4 & 0x3f));
  FUN_003948ec(uRam00e9c470,iVar1,uRam0108b7a8 >> (uRam0108b7c4 & 0x3f));
  FUN_003948ec(uRam00e9c470,uRam00e9c388,uRam0108b7a8 >> (uRam0108b7c4 & 0x3f));
  FUN_003948ec(uRam00e9c470,uRam00e9c4b4,uRam0108b7b4 >> (uRam0108b7c4 & 0x3f));
  return;
}

