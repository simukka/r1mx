/* 0x000f7b98  FUN_000f7b98  size=272 bytes */


void FUN_000f7b98(undefined4 *param_1)

{
  undefined1 auStack_78 [8];
  undefined1 auStack_70 [4];
  uint uStack_6c;
  undefined4 uStack_5c;
  uint uStack_58;
  undefined1 auStack_40 [4];
  undefined4 uStack_3c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined1 *puStack_20;
  undefined4 uStack_1c;
  undefined1 *puStack_18;
  undefined1 *puStack_14;
  undefined4 *puStack_c;
  
  puStack_14 = &stack0xffffff80;
  uStack_28 = 0x25710c;
  puStack_20 = auStack_78;
  uStack_24 = 0xe98610;
  uStack_1c = 0x107c9c;
  puStack_18 = (undefined1 *)register0x00000004;
  puStack_c = param_1;
  FUN_003d1214(auStack_40);
  uStack_3c = 0xffffffff;
  FUN_005ea3bc(auStack_70,0xd35294);
  uStack_3c = 1;
  FUN_00059684(puStack_c,auStack_70,0x10c,0x4a,0x4000,100);
  if (0xf < uStack_58) {
    FUN_00245c34(uStack_6c);
  }
  puStack_c[0x17] = 0xf;
  puStack_c[0x1c] = 0;
  puStack_c[0x16] = 0;
  *puStack_c = 0xe08c10;
  *(undefined1 *)(puStack_c + 0x12) = 0;
  *(undefined1 *)(puStack_c + 0x1b) = 0;
  *(undefined1 *)(puStack_c + 0x18) = 0;
  puStack_c[0x19] = 0;
  *(undefined1 *)((int)puStack_c + 0x6d) = 0;
  uStack_58 = 0xf;
  uStack_5c = 0;
  uStack_6c = uStack_6c & 0xffffff;
  FUN_003d12b8(auStack_40);
  return;
}

