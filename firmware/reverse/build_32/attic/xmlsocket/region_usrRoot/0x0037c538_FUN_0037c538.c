/* 0x0037c538  FUN_0037c538  size=444 bytes */


void FUN_0037c538(int *param_1,int param_2)

{
  if (iRam00e27078 != 0) {
    return;
  }
  FUN_0059ee68(0x51,0x38c9a8,0x5afba4,0x5b0ee0);
  FUN_0059ee68(0x50,0x38cac4,0x5af60c,0x5b0ee0);
  FUN_0059ee68(0x52,0x38cbd0,0x5af60c,0x5b0ee0);
  uRam00fbfab8 = 3;
  uRam00fbfabc = 0x38cc94;
  uRam00fbfac0 = 0x38d13c;
  FUN_0059b608(0xfbfab0);
  uRam00fbfacc = 4;
  uRam00fbfad0 = 0x38ce8c;
  uRam00fbfad4 = 0x38d13c;
  FUN_0059b608(0xfbfac4);
  uRam00e27084 = 0x38d314;
  uRam00e2707c = 0x38d5c8;
  uRam00e9c4b8 = 0x5adb0c;
  FUN_0037d660();
  for (; param_2 != 0; param_2 = param_2 + -1) {
    param_1[1] = 0xe9c0f4;
    *param_1 = (int)piRam00e9c0f4;
    piRam00e9c0f4 = param_1;
    *(int **)(*param_1 + 4) = param_1;
    param_1 = param_1 + 0xc;
  }
  FUN_005bb0cc();
  FUN_0059b19c(0xfbfa98,0x38c83c,0,0xfbfa98);
  iRam00e27078 = 1;
  return;
}

