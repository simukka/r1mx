
void FN_47000(void)

{
  int iVar1;
  int in_r10;
  uint in_stack_00000014;
  undefined4 in_stack_00000024;
  uint in_stack_00000028;
  uint in_stack_00000054;
  undefined4 in_stack_00000064;
  uint in_stack_00000068;
  int in_stack_00000074;
  undefined4 in_stack_00000078;
  undefined4 uStack000000a8;
  int in_stack_000000b8;
  int in_stack_000000bc;
  int in_stack_000000c0;
  int in_stack_000000c4;
  undefined4 in_stack_000000ec;
  int in_stack_000000f0;
  
  uStack000000a8 = in_stack_00000078;
  if (in_stack_00000074 != 1) {
    if (in_stack_00000074 == 2) goto LAB_00047050;
    in_stack_00000074 = 0;
    FUN_005e7ed0(&stack0x00000040);
  }
  if (0xf < in_stack_00000068) {
    FUN_00245c34(in_stack_00000054);
  }
  in_stack_00000068 = 0xf;
  in_stack_00000054 = in_stack_00000054 & 0xffffff;
  in_stack_00000064 = 0;
LAB_00047050:
  if (0xf < in_stack_00000028) {
    FUN_00245c34(in_stack_00000014);
  }
  in_stack_00000028 = 0xf;
  in_stack_00000014 = in_stack_00000014 & 0xffffff;
  in_stack_00000074 = 0xffffffff;
  in_stack_00000024 = 0;
  FUN_003d1934(uStack000000a8);
  iVar1 = in_stack_000000bc + 4;
  if (0xf < *(uint *)(in_stack_000000bc + 0x18)) {
    iVar1 = *(int *)(in_stack_000000bc + 4);
  }
  FUN_0039ac74(*(undefined4 *)(in_r10 + 4),iVar1 + in_stack_000000c0,in_stack_000000c4);
  iVar1 = in_stack_000000b8 + 4;
  if (0xf < *(uint *)(in_stack_000000b8 + 0x18)) {
    iVar1 = *(int *)(in_stack_000000b8 + 4);
  }
  *(int *)(in_stack_000000b8 + 0x14) = in_stack_000000c4;
  *(undefined1 *)(iVar1 + in_stack_000000c4) = 0;
  in_stack_00000074 = 3;
  in_stack_000000ec = FUN_0005e890();
  FUN_005ea3bc(&stack0x00000050,0xd3b9ac);
  in_stack_00000074 = 2;
  FUN_005e817c(&stack0x00000040,in_stack_000000ec,&stack0x00000050);
  in_stack_00000074 = 1;
  in_stack_000000f0 = FUN_005ea6b0(&stack0x00000040,&stack0x00000010,0xffffffff);
  in_stack_00000074 = 2;
  FUN_005e7ed0(&stack0x00000040);
  if (0xf < in_stack_00000068) {
    FUN_00245c34(in_stack_00000054);
  }
  in_stack_00000068 = 0xf;
  in_stack_00000054 = in_stack_00000054 & 0xffffff;
  in_stack_00000064 = 0;
  if (in_stack_000000f0 != 0) {
    in_stack_00000074 = 3;
    FUN_0005e784(2,3,0xc,0xd38d1c,0x65d008,0x11e,0xd3ba44,0xd3b9ac);
  }
  if (0xf < in_stack_00000028) {
    FUN_00245c34(in_stack_00000014);
  }
  in_stack_00000028 = 0xf;
  in_stack_00000014 = in_stack_00000014 & 0xffffff;
  in_stack_00000024 = 0;
  FUN_003d12b8(&stack0x00000070);
  return;
}

