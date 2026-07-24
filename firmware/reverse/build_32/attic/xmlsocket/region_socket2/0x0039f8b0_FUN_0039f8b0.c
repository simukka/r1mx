/* 0x0039f8b0  FUN_0039f8b0  size=1000 bytes */


undefined4 FUN_0039f8b0(uint *param_1,byte *param_2,int param_3)

{
  uint uVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  
  *param_1 = (uint)*param_2 << 0x18 ^ (uint)param_2[1] << 0x10 ^ (uint)param_2[2] << 8 ^
             (uint)param_2[3];
  param_1[1] = (uint)param_2[4] << 0x18 ^ (uint)param_2[5] << 0x10 ^ (uint)param_2[6] << 8 ^
               (uint)param_2[7];
  iVar3 = 0;
  param_1[2] = (uint)param_2[8] << 0x18 ^ (uint)param_2[9] << 0x10 ^ (uint)param_2[10] << 8 ^
               (uint)param_2[0xb];
  param_1[3] = (uint)param_2[0xc] << 0x18 ^ (uint)param_2[0xd] << 0x10 ^ (uint)param_2[0xe] << 8 ^
               (uint)param_2[0xf];
  if (param_3 == 0x80) {
    puVar2 = (uint *)0xd269d0;
    while( true ) {
      uVar1 = param_1[3];
      puVar2 = puVar2 + 1;
      uVar4 = *param_1 ^ *(uint *)((uVar1 >> 0xe & 0x3fc) + 0xd251d4) & 0xff000000 ^
              *(uint *)((uVar1 >> 6 & 0x3fc) + 0xd251d4) & 0xff0000 ^
              *(uint *)((uVar1 & 0xff) * 4 + 0xd251d4) & 0xff00 ^
              *(uint *)((uVar1 >> 0x16 & 0x3fc) + 0xd251d4) & 0xff ^ *puVar2;
      param_1[4] = uVar4;
      iVar3 = iVar3 + 1;
      uVar4 = param_1[1] ^ uVar4;
      param_1[5] = uVar4;
      uVar4 = param_1[2] ^ uVar4;
      param_1[6] = uVar4;
      param_1[7] = uVar1 ^ uVar4;
      if (iVar3 == 10) break;
      param_1 = param_1 + 4;
    }
    return 10;
  }
  param_1[4] = (uint)param_2[0x10] << 0x18 ^ (uint)param_2[0x11] << 0x10 ^ (uint)param_2[0x12] << 8
               ^ (uint)param_2[0x13];
  param_1[5] = (uint)param_2[0x14] << 0x18 ^ (uint)param_2[0x15] << 0x10 ^ (uint)param_2[0x16] << 8
               ^ (uint)param_2[0x17];
  if (param_3 == 0xc0) {
    puVar2 = (uint *)0xd269d0;
    while( true ) {
      uVar1 = param_1[5];
      puVar2 = puVar2 + 1;
      uVar4 = *param_1 ^ *(uint *)((uVar1 >> 0xe & 0x3fc) + 0xd251d4) & 0xff000000 ^
              *(uint *)((uVar1 >> 6 & 0x3fc) + 0xd251d4) & 0xff0000 ^
              *(uint *)((uVar1 & 0xff) * 4 + 0xd251d4) & 0xff00 ^
              *(uint *)((uVar1 >> 0x16 & 0x3fc) + 0xd251d4) & 0xff ^ *puVar2;
      param_1[6] = uVar4;
      uVar4 = param_1[1] ^ uVar4;
      iVar3 = iVar3 + 1;
      param_1[7] = uVar4;
      uVar4 = param_1[2] ^ uVar4;
      param_1[8] = uVar4;
      uVar4 = param_1[3] ^ uVar4;
      param_1[9] = uVar4;
      if (iVar3 == 8) break;
      uVar4 = param_1[4] ^ uVar4;
      param_1[10] = uVar4;
      param_1[0xb] = uVar1 ^ uVar4;
      param_1 = param_1 + 6;
    }
    return 0xc;
  }
  param_1[6] = (uint)param_2[0x18] << 0x18 ^ (uint)param_2[0x19] << 0x10 ^ (uint)param_2[0x1a] << 8
               ^ (uint)param_2[0x1b];
  param_1[7] = (uint)param_2[0x1c] << 0x18 ^ (uint)param_2[0x1d] << 0x10 ^ (uint)param_2[0x1e] << 8
               ^ (uint)param_2[0x1f];
  if (param_3 == 0x100) {
    puVar2 = (uint *)0xd269d0;
    while( true ) {
      uVar1 = param_1[7];
      puVar2 = puVar2 + 1;
      uVar4 = *param_1 ^ *(uint *)((uVar1 >> 0xe & 0x3fc) + 0xd251d4) & 0xff000000 ^
              *(uint *)((uVar1 >> 6 & 0x3fc) + 0xd251d4) & 0xff0000 ^
              *(uint *)((uVar1 & 0xff) * 4 + 0xd251d4) & 0xff00 ^
              *(uint *)((uVar1 >> 0x16 & 0x3fc) + 0xd251d4) & 0xff ^ *puVar2;
      param_1[8] = uVar4;
      uVar4 = param_1[1] ^ uVar4;
      iVar3 = iVar3 + 1;
      param_1[9] = uVar4;
      uVar4 = param_1[2] ^ uVar4;
      param_1[10] = uVar4;
      uVar4 = param_1[3] ^ uVar4;
      param_1[0xb] = uVar4;
      if (iVar3 == 7) break;
      uVar4 = param_1[4] ^ *(uint *)((uVar4 >> 0x16 & 0x3fc) + 0xd251d4) & 0xff000000 ^
              *(uint *)((uVar4 >> 0xe & 0x3fc) + 0xd251d4) & 0xff0000 ^
              *(uint *)((uVar4 >> 6 & 0x3fc) + 0xd251d4) & 0xff00 ^
              *(uint *)((uVar4 & 0xff) * 4 + 0xd251d4) & 0xff;
      param_1[0xc] = uVar4;
      uVar4 = param_1[5] ^ uVar4;
      param_1[0xd] = uVar4;
      uVar4 = param_1[6] ^ uVar4;
      param_1[0xe] = uVar4;
      param_1[0xf] = uVar1 ^ uVar4;
      param_1 = param_1 + 8;
    }
    return 0xe;
  }
  return 0;
}

