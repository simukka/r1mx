/* 0x0037c8d0  FUN_0037c8d0  size=148B */


void FUN_0037c8d0(void)

{
  if ((iRam00fbfa8c == 0) && (iRam00fbfa88 == 0)) {
    if (pcRam00e9c5f4 != reset_vector) {
      (*pcRam00e9c5f4)();
    }
  }
  else {
    if (iRam00fbfa8c != 0) {
      FUN_0059b1bc(0xfbfa98);
    }
    if (iRam00fbfa88 == 0) {
      uRam00e3a72c = 1;
    }
  }
  return;
}

