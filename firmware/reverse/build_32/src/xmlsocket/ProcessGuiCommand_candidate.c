
void ProcessGuiCommand_candidate(void)

{
  int *in_r9;
  int in_r11;
  int iVar1;
  int iVar2;
  int unaff_r29;
  int unaff_r30;
  bool bVar3;
  byte unaff_cr3;
  
  iVar2 = in_r9[1] + 1;
  iVar1 = in_r11 + (uint)(0xfffffffe < (uint)in_r9[1]);
  *in_r9 = iVar1;
  in_r9[1] = iVar2;
  if ((iVar1 == 0) && (iVar2 == 1)) {
    uRam01153418 = 0;
  }
  if (((uint)(unaff_r30 == 0xffff) & ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {
    bVar3 = 0xfffffffe < uRam01153404;
    uRam01153404 = uRam01153404 + 1;
    iRam01153400 = iRam01153400 + (uint)bVar3;
    if ((iRam01153400 == 0) && (uRam01153404 == 1)) {
      uRam01153408 = 0;
    }
  }
  if (((uint)(unaff_r30 == 0xffff) & ((uint)(unaff_cr3 & 0xf) << 0x10) >> 0x11 & 1) != 0) {
    bVar3 = 0xfffffffe < uRam011533e4;
    uRam011533e4 = uRam011533e4 + 1;
    iRam011533e0 = iRam011533e0 + (uint)bVar3;
    if ((iRam011533e0 == 0) && (uRam011533e4 == 1)) {
      uRam011533f0 = 0;
    }
  }
  if (unaff_r30 != 0xffff || unaff_r29 != 0) {
    return;
  }
  FUN_005e8e00(0xea0608);
  FUN_005e8e00(0xea0624);
  FUN_005e8e00(0xea0640);
  FUN_005e8e00(0xea065c);
  FUN_005e8e00(0xea0678);
  FUN_005e8e00(0xea0694);
  FUN_005e8e00(0xea06b0);
  FUN_005e8e00(0xea06cc);
  FUN_005e8e00(0xea06e8);
  FUN_005e8e00(0xea0704);
  FUN_005e8e00(0xea0720);
  FUN_005e8e00(0xea073c);
  FUN_0024b634(0xea0758);
  return;
}

