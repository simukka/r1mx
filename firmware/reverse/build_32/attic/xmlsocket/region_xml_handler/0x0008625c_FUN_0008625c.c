/* 0x0008625c  FUN_0008625c  size=128 bytes */


void FUN_0008625c(int param_1,int param_2,int param_3,int param_4)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  iVar4 = 0;
  if (0 < param_4) {
    do {
      while( true ) {
        iVar2 = iVar4 * 4;
        uVar3 = *(uint *)(iVar2 + param_3);
        if (0x4000 < uVar3) break;
        uVar1 = *(ushort *)((uVar3 >> 3 & 0x1ffffffe) + param_1 + 0xf3f2);
LAB_0008627c:
        *(uint *)(iVar2 + param_2) = (uint)uVar1;
        iVar4 = iVar4 + 1;
        param_4 = param_4 + -1;
        if (param_4 == 0) {
          return;
        }
      }
      if (uVar3 >> 10 < 0x385) {
        uVar1 = *(ushort *)((uVar3 >> 10) * 2 + param_1 + 0xece8);
        goto LAB_0008627c;
      }
      iVar4 = iVar4 + 1;
      *(uint *)(iVar2 + param_2) = (uint)*(ushort *)(FUN_0000f3f0 + param_1);
      param_4 = param_4 + -1;
    } while (param_4 != 0);
  }
  return;
}

