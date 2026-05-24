
undefined4 Connection_ProcessGuiCommand(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 in_stack_00000094;
  int in_stack_000000c4;
  
  uVar1 = FUN_0005ea28();
  FUN_00091d70(uVar1,*(undefined4 *)(in_stack_000000c4 + 0x31a8));
  if (*(char *)(in_stack_000000c4 + 0x210b) != '\0') {
    iVar2 = in_stack_000000c4 + 0x28;
    if (0xf < *(uint *)(in_stack_000000c4 + 0x3c)) {
      iVar2 = *(int *)(in_stack_000000c4 + 0x28);
    }
    in_stack_00000094 = 1;
    FUN_005f3110(0xd3bbb4,in_stack_000000c4 + 0x10d4,0xe,iVar2);
  }
  if (*(char *)(in_stack_000000c4 + 0x317f) != '\0') {
    iVar2 = in_stack_000000c4 + 0x28;
    if (0xf < *(uint *)(in_stack_000000c4 + 0x3c)) {
      iVar2 = *(int *)(in_stack_000000c4 + 0x28);
    }
    in_stack_00000094 = 1;
    FUN_005f3110(0xd3bbcc,in_stack_000000c4 + 0x2148,0xe,iVar2);
  }
  if (*(char *)(in_stack_000000c4 + 0x1097) != '\0') {
    iVar2 = in_stack_000000c4 + 0x28;
    if (0xf < *(uint *)(in_stack_000000c4 + 0x3c)) {
      iVar2 = *(int *)(in_stack_000000c4 + 0x28);
    }
    in_stack_00000094 = 1;
    FUN_005f3110(0xd3bb94,in_stack_000000c4 + 0x60,0xe,iVar2);
  }
  FUN_005e75e4(&stack0x00000050,1,0);
  FUN_005e75e4(&stack0x00000030,1,0);
  FUN_003d12b8(&stack0x00000090);
  return 0;
}

