/* 0x0000ddb8  fn_ddb8_rootTaskWrapper  size=108 bytes */


undefined4 FUN_0000ddb8(undefined4 param_1)

{
  FUN_0036fd0c();
  FUN_00458a60(0);
  FUN_00458a60(1);
  hw_seq_init();
  FUN_00371ed0(0);
  instructionSynchronize();
  (*(code *)0x10008)(param_1);
  return 0;
}

