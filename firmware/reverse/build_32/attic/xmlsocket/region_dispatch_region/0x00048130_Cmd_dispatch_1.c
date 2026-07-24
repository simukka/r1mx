/* 0x00048130  Cmd_dispatch_1  size=1232 bytes */


void Cmd_dispatch_1(void)

{
  undefined4 uVar1;
  uint in_stack_00000184;
  undefined4 in_stack_00000194;
  uint in_stack_00000198;
  uint in_stack_000001c4;
  undefined4 in_stack_000001d4;
  uint in_stack_000001d8;
  uint in_stack_000001e4;
  undefined4 in_stack_000001f4;
  uint in_stack_000001f8;
  char in_stack_00000201;
  undefined1 in_stack_00000203;
  undefined1 in_stack_00000204;
  undefined1 in_stack_00000205;
  undefined4 in_stack_00000214;
  uint in_stack_00000228;
  undefined1 *puVar2;
  
  uVar1 = FUN_0005e890();
  FUN_005ea3bc(&stack0x00000210,0xd3bbcc);
  FUN_005e817c(&stack0x00000170,uVar1,&stack0x00000210);
  FUN_005e8368(&stack0x00000170,&stack0x00000205);
  FUN_005e7ed0(&stack0x00000170);
  if (0xf < in_stack_00000228) {
    FUN_00245c34(in_stack_00000214);
  }
  FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x38f,0xd3bbe4,in_stack_00000203);
  FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x390,0xd3bc10,in_stack_00000204);
  FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x391,0xd3bc3c,in_stack_00000205);
  FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x392,0xd3bc68,0x65d010);
  FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x393,0xd3bc80);
  FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x394,0xd3bcb8);
  FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x395,0xd3bcf4);
  if (in_stack_00000201 != '\0') {
    uVar1 = FUN_001ce7ec();
    FUN_001ce83c();
    FUN_001ce888();
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d010,0x39b,0xd3bd34,uVar1);
  }
  if (0xf < in_stack_000001f8) {
    FUN_00245c34(in_stack_000001e4);
  }
  in_stack_000001e4 = in_stack_000001e4 & 0xffffff;
  in_stack_000001f8 = 0xf;
  in_stack_000001f4 = 0;
  if (0xf < in_stack_000001d8) {
    FUN_00245c34(in_stack_000001c4);
  }
  in_stack_000001c4 = in_stack_000001c4 & 0xffffff;
  in_stack_000001d4 = 0;
  in_stack_000001d8 = 0xf;
  if (0xf < in_stack_00000198) {
    FUN_00245c34(in_stack_00000184);
  }
  in_stack_00000198 = 0xf;
  in_stack_00000184 = in_stack_00000184 & 0xffffff;
  in_stack_00000194 = 0;
  puVar2 = &stack0x0000015c;
  while (&stack0x00000140 != puVar2) {
    if (0xf < *(uint *)(puVar2 + -4)) {
      FUN_00245c34(*(undefined4 *)(puVar2 + -0x18));
    }
    *(undefined4 *)(puVar2 + -8) = 0;
    puVar2[-0x18] = 0;
    *(undefined4 *)(puVar2 + -4) = 0xf;
    puVar2 = puVar2 + -0x1c;
  }
  puVar2 = &stack0x00000134;
  while (&stack0x000000e0 != puVar2) {
    if (0xf < *(uint *)(puVar2 + -4)) {
      FUN_00245c34(*(undefined4 *)(puVar2 + -0x18));
    }
    *(undefined4 *)(puVar2 + -8) = 0;
    puVar2[-0x18] = 0;
    *(undefined4 *)(puVar2 + -4) = 0xf;
    puVar2 = puVar2 + -0x1c;
  }
  puVar2 = &stack0x000000d4;
  while (&stack0x00000080 != puVar2) {
    if (0xf < *(uint *)(puVar2 + -4)) {
      FUN_00245c34(*(undefined4 *)(puVar2 + -0x18));
    }
    *(undefined4 *)(puVar2 + -8) = 0;
    puVar2[-0x18] = 0;
    *(undefined4 *)(puVar2 + -4) = 0xf;
    puVar2 = puVar2 + -0x1c;
  }
  puVar2 = &stack0x00000074;
  while (&stack0x00000020 != puVar2) {
    if (0xf < *(uint *)(puVar2 + -4)) {
      FUN_00245c34(*(undefined4 *)(puVar2 + -0x18));
    }
    *(undefined4 *)(puVar2 + -8) = 0;
    puVar2[-0x18] = 0;
    *(undefined4 *)(puVar2 + -4) = 0xf;
    puVar2 = puVar2 + -0x1c;
  }
  FUN_003d12b8(&stack0x00000230);
  return;
}

