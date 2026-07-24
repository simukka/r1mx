/* 0x000d0454  FUN_000d0454  size=100 bytes */


/* WARNING: Control flow encountered bad instruction data */

undefined4 FUN_000d0454(undefined4 param_1,undefined4 *param_2)

{
  switch(*param_2) {
  case 0:
  case 1:
  case 2:
  case 3:
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 9:
  case 10:
  case 0xb:
  case 0xc:
  case 0xd:
  case 0xe:
  case 0xf:
  case 0x10:
  case 0x11:
  case 0x12:
  case 0x13:
  case 0x14:
  case 0x15:
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  default:
    return 1;
  }
}

