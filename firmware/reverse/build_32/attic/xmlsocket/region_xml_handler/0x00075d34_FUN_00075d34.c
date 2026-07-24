/* 0x00075d34  FUN_00075d34  size=976 bytes */


void FUN_00075d34(undefined4 *param_1)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  undefined1 auStack_b8 [8];
  undefined4 uStack_b0;
  uint uStack_ac;
  undefined4 uStack_9c;
  uint uStack_98;
  undefined4 uStack_90;
  uint uStack_8c;
  undefined4 uStack_80;
  uint uStack_7c;
  undefined4 uStack_70;
  uint uStack_6c;
  undefined1 auStack_60 [4];
  undefined4 uStack_5c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined1 *puStack_40;
  undefined4 uStack_3c;
  undefined1 *puStack_38;
  undefined1 *puStack_34;
  undefined4 *puStack_2c;
  undefined1 *puStack_24;
  undefined1 *puStack_20;
  undefined4 *puStack_1c;
  undefined1 *puStack_18;
  undefined1 *puStack_14;
  undefined4 *puStack_10;
  
  puStack_34 = &stack0xffffff40;
  uStack_48 = 0x25710c;
  puStack_40 = auStack_b8;
  uStack_44 = 0xe96ce0;
  uStack_3c = 0x85f50;
  puStack_38 = (undefined1 *)register0x00000004;
  puStack_2c = param_1;
  FUN_003d1214(auStack_60);
  uStack_5c = 0xffffffff;
  FUN_005ea3bc(&uStack_b0,0xd3fa50);
  uStack_5c = 6;
  FUN_00059684(puStack_2c,&uStack_b0,0x10,0x4a,0x4000,100);
  if (0xf < uStack_98) {
    FUN_00245c34(uStack_ac);
  }
  *puStack_2c = 0xe08810;
  *(undefined1 *)(puStack_2c + 0x15) = 1;
  puStack_2c[0x16] = 0xffffffff;
  puStack_2c[0x12] = 0xffffffff;
  puStack_2c[0x11] = 0;
  puStack_2c[0x13] = 0;
  *(undefined1 *)((int)puStack_2c + 0x55) = 0;
  *(undefined1 *)((int)puStack_2c + 0x56) = 0;
  *(undefined1 *)((int)puStack_2c + 0x57) = 0;
  uStack_98 = 0xf;
  uStack_9c = 0;
  uStack_ac = uStack_ac & 0xffffff;
  puStack_24 = (undefined1 *)FUN_00248450(0x14,0xef9080);
  puVar1 = (undefined1 *)0x0;
  if (puStack_24 != (undefined1 *)0x0) {
    uStack_b0 = uRam0065e28c;
    uStack_ac = uRam0065e290;
    *puStack_24 = 0;
    uStack_5c = 4;
    puStack_20 = puStack_24;
    uVar2 = FUN_001d9ed8(1);
    *(undefined4 *)(puStack_24 + 4) = uVar2;
    *(undefined4 *)(puStack_24 + 8) = 1000;
    uStack_90 = uStack_b0;
    uStack_8c = uStack_ac;
    puStack_1c = (undefined4 *)FUN_00248640(0x2c);
    uStack_70 = uStack_90;
    uStack_6c = uStack_8c;
    uStack_80 = uStack_90;
    uStack_7c = uStack_8c;
    *puStack_1c = puStack_2c;
    puStack_1c[1] = uStack_90;
    puStack_1c[3] = 0;
    puStack_1c[2] = uStack_8c;
    uStack_5c = 3;
    FUN_005ea3bc(puStack_1c + 4,0xd6f55c);
    *(undefined4 *)(puStack_20 + 0x10) = 0x6047a0;
    *(undefined4 **)(puStack_20 + 0xc) = puStack_1c;
    puVar1 = puStack_24;
  }
  puStack_2c[0x13] = puVar1;
  if (puVar1 == (undefined1 *)0x0) {
    puVar3 = puStack_2c + 10;
    if (0xf < (uint)puStack_2c[0xf]) {
      puVar3 = (undefined4 *)puStack_2c[10];
    }
    uStack_5c = 5;
    FUN_0005e784(0,3,5,0xd3f794,0x65e27c,0xe3,0xd3fa58,puVar3);
  }
  puStack_18 = (undefined1 *)FUN_00248450(0x14,0xef9080);
  puVar1 = (undefined1 *)0x0;
  if (puStack_18 != (undefined1 *)0x0) {
    uStack_70 = uRam0065e294;
    uStack_6c = uRam0065e298;
    *puStack_18 = 0;
    uStack_5c = 2;
    puStack_14 = puStack_18;
    uVar2 = FUN_001d9ed8(1);
    *(undefined4 *)(puStack_18 + 4) = uVar2;
    *(undefined4 *)(puStack_18 + 8) = 3000;
    uStack_80 = uStack_70;
    uStack_7c = uStack_6c;
    puStack_10 = (undefined4 *)FUN_00248640(0x2c);
    uStack_b0 = uStack_80;
    uStack_ac = uStack_7c;
    uStack_90 = uStack_80;
    uStack_8c = uStack_7c;
    *puStack_10 = puStack_2c;
    puStack_10[1] = uStack_80;
    puStack_10[3] = 0;
    puStack_10[2] = uStack_7c;
    uStack_5c = 1;
    FUN_005ea3bc(puStack_10 + 4,0xd6f55c);
    *(undefined4 *)(puStack_14 + 0x10) = 0x6047a0;
    *(undefined4 **)(puStack_14 + 0xc) = puStack_10;
    puVar1 = puStack_18;
  }
  puStack_2c[0x14] = puVar1;
  if (puVar1 == (undefined1 *)0x0) {
    puVar3 = puStack_2c + 10;
    if (0xf < (uint)puStack_2c[0xf]) {
      puVar3 = (undefined4 *)puStack_2c[10];
    }
    uStack_5c = 5;
    FUN_0005e784(0,3,5,0xd3f794,0x65e27c,0xf1,0xd3fa7c,puVar3);
  }
  uStack_5c = 5;
  FUN_0021a414(0x6d,0x84afc,puStack_2c);
  FUN_003d12b8(auStack_60);
  return;
}

