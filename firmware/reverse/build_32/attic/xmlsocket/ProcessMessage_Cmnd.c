
/* WARNING: Restarted to delay deadcode elimination for space: stack */

undefined4 ProcessMessage_Cmnd(void)

{
  bool bVar1;
  undefined4 in_r0;
  undefined4 *puVar2;
  uint uVar3;
  int iVar4;
  undefined1 *puVar5;
  int in_r6;
  int in_r7;
  int in_r9;
  uint uVar6;
  undefined1 *puVar7;
  undefined4 *in_stack_00000024;
  uint in_stack_00000034;
  uint in_stack_00000038;
  char cStack00000040;
  undefined4 uStack000000b4;
  int in_stack_000000e4;
  int in_stack_000000e8;
  undefined4 *in_stack_000001b4;
  uint in_stack_000001b8;
  undefined1 *in_stack_000001bc;
  undefined1 *in_stack_000001c0;
  uint in_stack_000001c4;
  uint in_stack_000001c8;
  undefined1 *in_stack_000001cc;
  uint in_stack_000001d0;
  
  uStack000000b4 = in_r0;
  FUN_0005e784(3,0x20,6,in_r6 + -0x18e0,in_r7 + -0x1fdc,0x420,in_r9 + -0xb14,0x65e018);
  FUN_005f08cc(0xd3c6b8,in_stack_000000e4 + 0x68,6,0x65e018);
  FUN_005f08cc(0xd3c9fc,in_stack_000000e4 + 0x84,6,0x65e018);
  FUN_005f08cc(0xd3bf98,in_stack_000000e4 + 0xd8,6,0x65e018);
  FUN_0006d1d4(in_stack_000000e4);
  FUN_00069508(in_stack_000000e4);
  FUN_005f3110(0xd3f514,&stack0x00000040,6,0x65e018);
  if (cStack00000040 == '\0') goto LAB_00070bc0;
  in_stack_000001b4 = *(undefined4 **)(in_stack_000000e8 * 0x94 + 0xe10aac);
  in_stack_000001b8 = FUN_0039b0f0(in_stack_000001b4);
  puVar2 = &stack0x00000024;
  if (0xf < in_stack_00000038) {
    puVar2 = in_stack_00000024;
  }
  if (in_stack_000001b4 < puVar2) {
LAB_00070a38:
    bVar1 = false;
  }
  else {
    puVar2 = &stack0x00000024;
    if (0xf < in_stack_00000038) {
      puVar2 = in_stack_00000024;
    }
    bVar1 = true;
    if ((undefined4 *)((int)puVar2 + in_stack_00000034) <= in_stack_000001b4) goto LAB_00070a38;
  }
  if (bVar1) {
    in_stack_000001bc = &stack0x00000020;
    puVar2 = &stack0x00000024;
    if (0xf < in_stack_00000038) {
      puVar2 = in_stack_00000024;
    }
    in_stack_000001c4 = (int)in_stack_000001b4 - (int)puVar2;
    in_stack_000001c0 = in_stack_000001bc;
    if (in_stack_00000034 < in_stack_000001c4) {
      uStack000000b4 = 4;
      FUN_00250ea4(in_stack_000001bc);
    }
    in_stack_000001c8 = *(int *)(in_stack_000001c0 + 0x14) - in_stack_000001c4;
    if (in_stack_000001b8 < in_stack_000001c8) {
      in_stack_000001c8 = in_stack_000001b8;
    }
    if (in_stack_000001bc == in_stack_000001c0) {
      uStack000000b4 = 4;
      FUN_005f3808(in_stack_000001bc,in_stack_000001c4 + in_stack_000001c8,0xffffffff);
      FUN_005f3808(in_stack_000001bc,0,in_stack_000001c4);
    }
    else {
      in_stack_000001d0 = in_stack_000001c8;
      in_stack_000001cc = in_stack_000001bc;
      if (0xfffffffe < in_stack_000001c8) {
        uStack000000b4 = 4;
        FUN_002513e0(in_stack_000001bc);
      }
      if (*(uint *)(in_stack_000001bc + 0x18) < in_stack_000001c8) {
        uStack000000b4 = 4;
        FUN_005e7bb8(in_stack_000001bc,in_stack_000001c8,*(undefined4 *)(in_stack_000001bc + 0x14));
      }
      else if (in_stack_000001d0 == 0) {
        puVar7 = in_stack_000001cc + 4;
        if (0xf < *(uint *)(in_stack_000001cc + 0x18)) {
          puVar7 = *(undefined1 **)(in_stack_000001cc + 4);
        }
        *(undefined4 *)(in_stack_000001cc + 0x14) = 0;
        *puVar7 = 0;
      }
      if (in_stack_000001d0 != 0) {
        puVar7 = in_stack_000001bc + 4;
        if (0xf < *(uint *)(in_stack_000001bc + 0x18)) {
          puVar7 = *(undefined1 **)(in_stack_000001bc + 4);
        }
        puVar5 = in_stack_000001c0 + 4;
        if (0xf < *(uint *)(in_stack_000001c0 + 0x18)) {
          puVar5 = *(undefined1 **)(in_stack_000001c0 + 4);
        }
        FUN_0039ac74(puVar7,puVar5 + in_stack_000001c4,in_stack_000001c8);
        uVar3 = *(uint *)(in_stack_000001bc + 0x18);
        puVar7 = in_stack_000001bc;
        uVar6 = in_stack_000001c8;
        goto LAB_00070b70;
      }
    }
  }
  else {
    uStack000000b4 = 4;
    iVar4 = FUN_005f0030(&stack0x00000020,in_stack_000001b8,0);
    if (iVar4 != 0) {
      puVar2 = &stack0x00000024;
      if (0xf < in_stack_00000038) {
        puVar2 = in_stack_00000024;
      }
      FUN_0039ac74(puVar2,in_stack_000001b4,in_stack_000001b8);
      puVar7 = &stack0x00000020;
      uVar3 = in_stack_00000038;
      uVar6 = in_stack_000001b8;
LAB_00070b70:
      puVar5 = puVar7 + 4;
      if (0xf < uVar3) {
        puVar5 = *(undefined1 **)(puVar7 + 4);
      }
      *(uint *)(puVar7 + 0x14) = uVar6;
      puVar5[uVar6] = 0;
    }
  }
  uStack000000b4 = 4;
  FUN_005f08cc(*(undefined4 *)(in_stack_000000e8 * 0x94 + 0xe10a7c),&stack0x00000020,6,0x65e018);
LAB_00070bc0:
  FUN_005e8e00(&stack0x00000020);
  FUN_003d12b8(&stack0x000000b0);
  return 0;
}

