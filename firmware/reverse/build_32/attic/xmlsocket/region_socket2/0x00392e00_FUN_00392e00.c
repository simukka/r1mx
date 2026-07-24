/* 0x00392e00  FUN_00392e00  size=428 bytes */


void FUN_00392e00(int param_1,int param_2,int param_3,code *param_4)

{
  byte in_cr0;
  byte in_cr1;
  byte unaff_cr2;
  byte unaff_cr3;
  byte unaff_cr4;
  byte in_cr5;
  byte in_cr6;
  byte in_cr7;
  int iStack_c8;
  int iStack_c4;
  int iStack_c0;
  code *pcStack_bc;
  int iStack_b8;
  int iStack_b4;
  undefined1 auStack_a0 [4];
  undefined4 uStack_9c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  int *piStack_80;
  undefined4 uStack_7c;
  undefined1 *puStack_78;
  undefined1 *puStack_74;
  uint uStack_4c;
  
  puStack_74 = &stack0xffffff30;
  uStack_4c = (uint)(in_cr0 & 0xf) << 0x1c | (uint)(in_cr1 & 0xf) << 0x18 |
              (uint)(unaff_cr2 & 0xf) << 0x14 | (uint)(unaff_cr3 & 0xf) << 0x10 |
              (uint)(unaff_cr4 & 0xf) << 0xc | (uint)(in_cr5 & 0xf) << 8 | (uint)(in_cr6 & 0xf) << 4
              | (uint)(in_cr7 & 0xf);
  uStack_88 = 0x25710c;
  uStack_84 = 0xe9becc;
  piStack_80 = &iStack_c8;
  uStack_7c = 0x3a2f68;
  iStack_c8 = param_1;
  iStack_c4 = param_2;
  iStack_c0 = param_3;
  pcStack_bc = param_4;
  puStack_78 = (undefined1 *)register0x00000004;
  FUN_003d1214(auStack_a0);
  if (pcStack_bc != reset_vector) {
    iStack_b4 = iStack_c4;
    iStack_b8 = iStack_c8 + iStack_c4 * iStack_c0;
    while (iStack_b4 = iStack_b4 + -1, iStack_b4 != -1) {
      iStack_b8 = iStack_b8 - iStack_c0;
      uStack_9c = 3;
      (*pcStack_bc)(iStack_b8);
    }
  }
  FUN_003d12b8(auStack_a0);
  return;
}

