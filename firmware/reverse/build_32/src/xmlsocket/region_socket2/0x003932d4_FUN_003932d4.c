/* 0x003932d4  FUN_003932d4  size=416 bytes */


void FUN_003932d4(int param_1,undefined4 param_2,int param_3,undefined4 param_4,code *param_5)

{
  byte in_cr0;
  byte in_cr1;
  byte unaff_cr2;
  byte unaff_cr3;
  byte unaff_cr4;
  byte in_cr5;
  byte in_cr6;
  byte in_cr7;
  int iStack_d8;
  undefined4 uStack_d4;
  int iStack_d0;
  undefined4 uStack_cc;
  code *pcStack_c8;
  int iStack_c4;
  undefined4 uStack_c0;
  undefined1 auStack_a0 [4];
  undefined4 uStack_9c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  int *piStack_80;
  undefined4 uStack_7c;
  undefined1 *puStack_78;
  undefined1 *puStack_74;
  uint uStack_4c;
  
  puStack_74 = &stack0xffffff20;
  uStack_4c = (uint)(in_cr0 & 0xf) << 0x1c | (uint)(in_cr1 & 0xf) << 0x18 |
              (uint)(unaff_cr2 & 0xf) << 0x14 | (uint)(unaff_cr3 & 0xf) << 0x10 |
              (uint)(unaff_cr4 & 0xf) << 0xc | (uint)(in_cr5 & 0xf) << 8 | (uint)(in_cr6 & 0xf) << 4
              | (uint)(in_cr7 & 0xf);
  uStack_88 = 0x25710c;
  uStack_84 = 0xe9bef0;
  piStack_80 = &iStack_d8;
  uStack_7c = 0x3a3414;
  iStack_d8 = param_1;
  uStack_d4 = param_2;
  iStack_d0 = param_3;
  uStack_cc = param_4;
  pcStack_c8 = param_5;
  puStack_78 = (undefined1 *)register0x00000004;
  FUN_003d1214(auStack_a0);
  iStack_c4 = iStack_d8;
  if (iStack_d0 != 0) {
    uStack_c0 = *(undefined4 *)(iStack_d8 + -4);
    iStack_c4 = iStack_d8 - iStack_d0;
    uStack_9c = 3;
    FUN_00392e00(iStack_d8,uStack_c0,uStack_d4,uStack_cc);
  }
  uStack_9c = 0xffffffff;
  (*pcStack_c8)(iStack_c4);
  FUN_003d12b8(auStack_a0);
  return;
}

