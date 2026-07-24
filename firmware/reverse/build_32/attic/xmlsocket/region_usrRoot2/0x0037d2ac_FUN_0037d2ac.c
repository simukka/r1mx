/* 0x0037d2ac  FUN_0037d2ac  size=104 bytes */


void FUN_0037d2ac(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uRam00fbfa78 = param_2;
  uRam00fbfa8c = param_3;
  uRam00fbfa88 = param_4;
  if (pcRam00e9c3a4 == reset_vector) {
    return;
  }
  (*pcRam00e9c3a4)(param_1,0x38c8d0,0);
  return;
}

